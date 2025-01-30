#include "threads.hpp"
#include "background_correction.hpp"
#include "reader.hpp"
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

void ThreadManager::_workerFunction(int bufferStartPos, int bufferEndPos)
{
    std::cout << "Thread: " << std::this_thread::get_id() << std::endl;
    for (int i = bufferStartPos; i < bufferEndPos; i++) {
        if (_settings->invertImage) {
            cv::bitwise_not(_buffer[i], _threadLocalBuffer[i]);
        } else {
            _threadLocalBuffer[i] = _buffer[i].clone();
        }
    }
    cv::Mat background;
    // _backgroundModel(_threadLocalBuffer, background, bufferStartPos, bufferEndPos);
    minMaxMethod(_threadLocalBuffer, background, bufferStartPos, bufferEndPos);
    background.release();
}

ThreadManager::ThreadManager(const Settings& settings)
    : _settings(&settings)
    , _counter(0)
{
    _bufferSize = _settings->stackBufferSizeMultiplier * _settings->stackSize,
    getAllFiles(_settings->sourceDir, _files);
    std::cout << "Found " << _files.size() << " files" << std::endl;
    for (int i = 0; i < _settings->stackBufferSizeMultiplier; i++) {
        _finishedStacks.insert(i * _settings->stackSize + (i + 1) * _settings->stackSize * _bufferSize);
    }

    _buffer.resize(_bufferSize);
    _threadLocalBuffer.resize(_bufferSize);

    // start workers:
    for (int i = 0; i < _settings->nThreads; i++) {
        _threads.emplace_back(&ThreadManager::worker, this);
    }

    // _backgroundModel = minMethod;
    // // start main thread:
    _running
        = true;
    this->run();
}

void ThreadManager::worker()
{
    while (true) {
        int bufferPos, bufferStartPos, bufferEndPos;
        {
            // std::cout << "Thread: " << std::this_thread::get_id() << " waiting for task" << std::endl;
            std::unique_lock<std::mutex> lock(_taskMutex);
            _taskCondition.wait(lock, [this] { return !_running || !_availableStacks.empty(); });

            if (!_running && _availableStacks.empty())
                return;

            // std::cout << "Thread: " << std::this_thread::get_id() << " got task" << std::endl;
            // get next task (bufferPos)
            bufferPos = *_availableStacks.begin();
            _availableStacks.erase(bufferPos);
            _counter++;
        }

        bufferStartPos = bufferPos % (_bufferSize);
        bufferEndPos = bufferPos / (_bufferSize);
        std::cout << "Thread: " << std::this_thread::get_id() << " got task with start: " << bufferStartPos << " and end: " << bufferEndPos << "" << std::endl;

        // run task:
        _workerFunction(bufferStartPos, bufferEndPos);

        // notify main thread of finished thread
        {
            std::unique_lock<std::mutex> lock(_mainMutex);
            _finishedStacks.insert(bufferPos);
        }
        _mainCondition.notify_one();
    }
}

void ThreadManager::run()
{
    // TODO: Handle remaining files that are not a multiple of stackSize
    while (true) {
        {
            // wait for finished task
            std::unique_lock<std::mutex> lock(_mainMutex);
            _mainCondition.wait(lock, [this] { return !_running || !_finishedStacks.empty(); });

            if (!_running)
                return;

            // get next finished task (bufferPos)
            int bufferPos = *_finishedStacks.begin();
            _finishedStacks.erase(bufferPos);

            int bufferStartPos = bufferPos % (_bufferSize);
            int bufferEndPos = bufferPos / (_bufferSize);
            std::cout << "Main thread got finished task with start: " << bufferStartPos << " and end: " << bufferEndPos << "" << std::endl;
            if (_files.empty()) {
                std::cout << "No more files left" << std::endl;
                _running = false;
                _taskCondition.notify_all();
                break;
            }

            if (_files.size() < _settings->stackSize) {
                bufferEndPos = bufferStartPos + _files.size();
                bufferPos = bufferStartPos + bufferEndPos * _bufferSize;
            }
            readNextImageStack(_files, _buffer, bufferStartPos, bufferEndPos, _settings);
            // if less than one stacks remain, combine it with the current one. To ensure enough space is in the buffer, wait for another task to finish
            // if (_files.size() < _settings->stackSize) {
            //     std::cout << "Less than " << _settings->stackSize << " files left, combining them..." << std::endl;
            //     combiningStacks = true;
            //     combiningStacksBufferPos = bufferPos;
            //     continue;
            // }

            // notify worker thread of new task
            _availableStacks.insert(bufferPos);
            _taskCondition.notify_one();
        }
    }

    // wait for all threads
    {
        std::unique_lock<std::mutex> lock(_mainMutex);
        _mainCondition.wait(lock, [this] { return _availableStacks.empty(); });
    }

    for (auto& thread : _threads) {
        thread.join();
    }
}
