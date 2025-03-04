#include "threadmanager.hpp"
#include <cstring>
#include <iostream>

ThreadManager::ThreadManager(void* taskData, taskFunction* taskFunctions, size_t numThreads, bool returnFinishedTasks, size_t taskBufferSize)
    : _taskBufferSize(taskBufferSize)
    , _taskData(taskData)
    , _taskFunctions(taskFunctions)
    , _returnFinishedTasks(returnFinishedTasks)
{
    for (size_t i = 0; i < numThreads; i++) {
        _threads.emplace_back(std::thread(&ThreadManager::_worker, this, i));
    }
}

Info ThreadManager::_getNextTask(Task& task)
{
    {
        std::unique_lock lock(_availableTaskMutex);
        _availableTaskCondition.wait(lock, [this] { return _stop || !_availableTasksQueue.empty(); });

        if (_stop && _availableTasksQueue.empty()) {
            return ThreadManagerFinished;
        }

        task = _availableTasksQueue.front();
        _availableTasksQueue.pop();
        _taskBufferCondition.notify_one();
    }
    return Success;
}

void ThreadManager::_worker(size_t threadId)
{
    while (true) {
        Task task;
        Task result;
        // get next task
        result.threadManagerInfo = _getNextTask(task);
        if (result.threadManagerInfo == ThreadManagerFinished)
            break;

        // try to run task function with provided data
        Info info;
        try {
            info = _taskFunctions[task.funcIdx](threadId, _taskMutex, _taskData, task.taskIdx, task.size);
        } catch (std::exception& e) {
            info = RuntimeError;
            std::cout << makeRed("Exception in taskFunction " + std::to_string(task.funcIdx) + " and taskData at (" + std::to_string(task.taskIdx) + ":" + std::to_string(task.size) + ": ") << e.what() << std::endl;
        }

        result.taskInfo = info;
        result.taskIdx = task.taskIdx;
        result.size = task.size;
        result.funcIdx = task.funcIdx;

        // if wanted, push finished task to queue:
        if (_returnFinishedTasks) {
            std::unique_lock lock(_finishedTaskMutex);
            _finishedTasksQueue.push(result);
            _finishedTaskCondition.notify_one();
        }

        // taskFunction can tell the worker that it is finished
        if (info == ThreadManagerThisWorkerFinished) {
            break;
        }
    }
}

Info ThreadManager::addTask(Task& task)
{
    {
        std::unique_lock lock(_availableTaskMutex);
        _taskBufferCondition.wait(lock, [this] { return _availableTasksQueue.size() < _taskBufferSize || _stop; });

        if (_stop) {
            return ThreadManagerFinished;
        }

        _availableTasksQueue.push(task);
        _availableTaskCondition.notify_one();
    }

    return Success;
}

void ThreadManager::getFinishedTask(Task& result)
{
    {
        std::unique_lock lock(_finishedTaskMutex);
        _finishedTaskCondition.wait(lock, [this] { return _stop || !_finishedTasksQueue.empty(); });

        if (_stop && _finishedTasksQueue.empty()) {
            result.threadManagerInfo = ThreadManagerFinished;
            return;
        }

        result = _finishedTasksQueue.front();
        _finishedTasksQueue.pop();
    }
}

void ThreadManager::finishThreads()
{
    _stop = true;
    _taskBufferCondition.notify_all();
    _availableTaskCondition.notify_all();
    _finishedTaskCondition.notify_all();

    for (size_t i = 0; i < _threads.size(); i++) {
        _threads[i].join();
    }
    _threads.clear();
}

void ThreadManager::cleanUp()
{
    finishThreads();

    while (!_availableTasksQueue.empty())
        _availableTasksQueue.pop();
    while (!_finishedTasksQueue.empty())
        _finishedTasksQueue.pop();
}

ThreadManager::~ThreadManager()
{
    cleanUp();
}
