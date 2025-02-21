#pragma once

#include "utils.hpp"
#include <opencv2/core.hpp>
#include <thread>

struct Thread {
public:
    bool isRunning;
    int bufferPos;

    void runTask(const std::vector<cv::Mat>& buffer, const Settings* settings);
    Thread();

private:
    std::thread thread;

    void threadFunction(const std::vector<cv::Mat>& buffer, const Settings* settings);
};

class ThreadManager {
public:
    ThreadManager(const Settings& settings);
    cv::Mat* getStackImage(int index, int threadIdx);
    void start();

private:
    int bufferSize;
    int bufferPos;
    int nThreads;
    int stackSize;

    const Settings* settings;

    std::vector<cv::Mat> buffer;
    std::vector<int> freeBufferPos;
    std::vector<int> emptyBufferPos;
    std::vector<std::string> files;

    std::vector<Thread> threads;

    void updateBuffer();
};
