#pragma once

#include "utils.hpp"
#include <atomic>
#include <condition_variable>
#include <mutex>
#include <opencv2/core.hpp>
#include <thread>
#include <unordered_set>
#include <vector>

class ThreadManager {
private:
    int _counter;
    int _bufferSize;

    std::vector<cv::Mat> _buffer;
    std::vector<cv::Mat> _threadLocalBuffer;
    std::vector<std::thread> _threads;
    std::vector<std::string> _files;
    std::unordered_set<int> _availableStacks; // contains the start and end buffer position of the available stacks -> idx = bufferStartPos + bufferEndPos * bufferSize
    std::unordered_set<int> _finishedStacks; // contains start and end buffer position of the finished stacks -> idx = bufferStartPos + bufferEndPos * bufferSize
    std::mutex _taskMutex, _mainMutex;
    std::condition_variable _taskCondition, _mainCondition;
    std::atomic<bool> _running;

    const Settings* _settings;

    void worker();
    void run();
    void _workerFunction(int, int);
    void (*_backgroundModel)(const std::vector<cv::Mat>&, cv::Mat&, int, int);

public:
    ThreadManager(const Settings& settings);
};
