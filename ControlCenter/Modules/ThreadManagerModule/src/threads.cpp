#include "threads.hpp"
#include <iostream>
#include <mutex>

std::string error(Error errorCode)
{
    const std::unordered_map<Error, std::string> errorMap {
        { Success, "Success" },
        { EmptyTask, "Empty task" },
        { TaskFunctionNotSet, "Task function not set" },
        { Runtime, "Runtime error" },
        { Unknown, "Unknown error" },
    };

    try {
        return errorMap.at(errorCode);
    } catch (const std::out_of_range& e) {
        return "Invalid error code: " + std::to_string(errorCode);
    }
}

std::function<std::string(Error)> errorFunction = error;

void checkError(const Task& finishedTask, bool printWarnings)
{
    if (finishedTask.errorCode > 0 && printWarnings)
        std::cout << "\033[1;33mWarning from task with id " << finishedTask.getTaskId() << ": " << errorFunction(finishedTask.errorCode) << "\033[0m" << std::endl;
    else if (finishedTask.errorCode < 0)
        throw std::runtime_error("\033[31mError from task with id " + std::to_string(finishedTask.getTaskId()) + ": " + errorFunction(finishedTask.errorCode) + "\033[0m");
}

void checkError(const Error& errorCode, bool printWarnings)
{
    if (errorCode > 0 && printWarnings)
        std::cout << "\033[1;33mWarning: " << errorFunction(errorCode) << "\033[0m" << std::endl;
    else if (errorCode < 0)
        throw std::runtime_error("\033[31mError: " + errorFunction(errorCode) + "\033[0m");
}

// Function that is called in a worker thread to run the task function if defined. Returns the optional error message.
Error Task::runTask()
{
    if (_taskFunction)
        return _taskFunction();
    return TaskFunctionNotSet;
}

Task emptyTask()
{
    Task task;
    task.makeEmpty();
    return task;
}

Task stopTask()
{
    Task task;
    task.makeEmpty();
    task.softStopThreadManager = true;
    return task;
}

// Constructor of the ThreadManager. The maxQueueSize is the maximal number of tasks that can be stored in the queue at the same time. The numThreads is the number of worker threads that are started.
ThreadManager::ThreadManager(int maxQueueSize, int numThreads)
    : _maxQueueSize(maxQueueSize)
    , _numThreads(numThreads)
    , joined(false)
{
    _softStop = false;
    _hardStop = false;

    // fill _finishedTasksQueue with _maxQueueSize empty tasks to start the ThreadManager.
    for (int i = 0; i < _maxQueueSize; i++) {
        Task task(i);
        task.makeEmpty();
        _finishedTasksQueue.push(task);
    }

    // add the worker threads:
    for (int i = 0; i < _numThreads; i++) {
        _threads.emplace_back(&ThreadManager::worker, this);
    }
}

// Worker thread function. Waits until a new task is available. If the ThreadManager is stopped, the worker thread will exit. Else, it will run the tasks function and add the finished task to the finished task queue.
void ThreadManager::worker()
{
    while (true) {
        Task task;
        {
            // std::cout << "Worker thread " << std::this_thread::get_id() << " waiting for task" << std::endl;
            // wait until program is finished or new task is available
            std::unique_lock<std::mutex> lock(_taskMutex);
            _taskCondition.wait(lock, [this] { return _softStop || _hardStop || !_availableTasksQueue.empty(); });
            // std::cout << "Worker thread " << std::this_thread::get_id() << " finished waiting for task" << std::endl;

            if ((_softStop && _availableTasksQueue.empty()) || _hardStop)
                break;

            // get the next task
            task = _availableTasksQueue.front();
            _availableTasksQueue.pop();

            // check if task has stop signal
            if (task.hardStopThreadManager) {
                _hardStop = true;
                _taskCondition.notify_all();
                _mainCondition.notify_all();
            } else if (task.softStopThreadManager) {
                _softStop = true;
                _taskCondition.notify_all();
                _mainCondition.notify_all();
            }
        }

        // run task function
        task.errorCode = task.runTask();

        // notify main thread for finished task and add it to the finished task list
        {
            std::unique_lock<std::mutex> lock(_mainMutex);
            _finishedTasksQueue.push(task);
        }
        _mainCondition.notify_one();
    }
}

// Stops the threads and waits until they are finished.
void ThreadManager::finishThreads()
{
    // wait for all threads to finish
    _softStop = true;
    _taskCondition.notify_all();
    _mainCondition.notify_all();
    for (std::thread& t : _threads) {
        t.join();
    }
    joined = true;
}

// Returns finished tasks if available.
Error ThreadManager::getFinishedTask(Task& task)
{
    std::unique_lock<std::mutex> lock(_mainMutex);
    if (_finishedTasksQueue.empty()) {
        task.makeEmpty();
        return NoFinishedTasksAvailable;
    }
    task = _finishedTasksQueue.front();
    _finishedTasksQueue.pop();
    return Success;
}

// Function to clean up the ThreadManager. It will soft stop the threads and clear the queues.
void ThreadManager::cleanUp()
{
    if (!joined) {
        _softStop = true;
        _taskCondition.notify_all();
        _mainCondition.notify_all();
        for (std::thread& t : _threads) {
            t.join();
        }
        joined = true;
    }
    while (!_finishedTasksQueue.empty()) {
        _finishedTasksQueue.pop();
    }
}

// This function will be called by an external source providing the next task. It will block until the task can be added to the task queue, thus blocking the external source until the next task can be added. The function returns the finishedTask which will be replaced by the newTask.
Task ThreadManager::addNextTask(Task& newTask)
{
    // wait until one task is finished
    std::unique_lock<std::mutex> lock(_mainMutex);
    _mainCondition.wait(lock, [this] { return !_finishedTasksQueue.empty() || _softStop || _hardStop; });

    if (_softStop || _hardStop) {
        return Task();
    }

    Task finishedTask = _finishedTasksQueue.front();
    _finishedTasksQueue.pop();

    {
        std::unique_lock<std::mutex> lock(_taskMutex);
        _availableTasksQueue.push(newTask);
    }
    _taskCondition.notify_one();

    return finishedTask;
}

ThreadManager::~ThreadManager()
{
    cleanUp();
}
