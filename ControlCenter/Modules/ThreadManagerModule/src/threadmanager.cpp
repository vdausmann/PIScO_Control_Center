#include "threadmanager.hpp"
#include <cstring>
#include <iostream>

ThreadManager::ThreadManager(void* taskData, taskFunction* taskFunctions, size_t numThreads, bool returnFinishedTasks, size_t taskBufferSize)
    : _taskBufferSize(taskBufferSize)
    , _averagingSamples(0)
    , _avgWaitTime(0)
    , _avgTaskRunTime(0)
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

        auto start = std::chrono::high_resolution_clock::now();
        // get next task
        result.threadManagerInfo = _getNextTask(task);
        if (result.threadManagerInfo == ThreadManagerFinished)
            break;

        double waitDuration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start).count();

        // try to run task function with provided data
        Info info;
        try {
            auto start = std::chrono::high_resolution_clock::now();
            info = _taskFunctions[task.funcIdx](threadId, _taskMutex, _taskData, task.taskIdx, task.size);
            double duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start).count();

            // metrics:
            {
                std::unique_lock lock(_metricsMutex);
                _avgTaskRunTime += duration;
                _avgWaitTime = _avgWaitTime + waitDuration;
                _averagingSamples++;
            }

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

double ThreadManager::getAvgWaitTime()
{
    return _avgWaitTime / _averagingSamples;
}

double ThreadManager::getAvgTaskRunTime()
{
    return _avgTaskRunTime / _averagingSamples;
}
