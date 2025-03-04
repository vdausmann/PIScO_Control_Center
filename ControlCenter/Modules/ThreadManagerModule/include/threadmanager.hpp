#pragma once
#include "info.hpp"
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <mutex>
#include <queue>

// TODO: Documentation

typedef std::function<Info(const size_t& threadId, std::mutex& lock, void* taskData, const size_t& taskIdx, const size_t& taskSize)> taskFunction;

// return type for finished task
struct Task {
    size_t taskIdx; // index in taskData pointer
    size_t size; // size of assigned memory to the task
    size_t funcIdx; // index in taskFunctions pointer
    Info taskInfo;
    Info threadManagerInfo;
};

struct ThreadManager {
private:
    std::queue<Task> _availableTasksQueue;
    std::queue<Task> _finishedTasksQueue;
    std::condition_variable _availableTaskCondition;
    std::condition_variable _finishedTaskCondition;
    std::condition_variable _taskBufferCondition;
    std::mutex _availableTaskMutex;
    std::mutex _finishedTaskMutex;
    std::mutex _taskMutex;
    std::vector<std::thread> _threads;
    size_t _taskBufferSize;
    void* _taskData;
    taskFunction* _taskFunctions;
    std::atomic<bool> _stop;
    bool _returnFinishedTasks;

    Info _getNextTask(Task& task);
    void _worker(size_t threadId);

public:
    ThreadManager(void* taskData, taskFunction* taskFunctions, size_t numThreads, bool returnFinishedTasks, size_t taskBufferSize);
    Info addTask(Task& task);
    void getFinishedTask(Task& result);
    void finishThreads();
    void cleanUp();
    ~ThreadManager();
};
