#pragma once
#include <opencv2/core/mat.hpp>
#include <queue>
#include <unordered_map>
#include <vector>
#include <optional>
#include <chrono>
#include <condition_variable>

using namespace std::chrono_literals;

struct CropStack {
	std::vector<cv::Mat> stackImages;
	std::vector<std::unordered_map<size_t, std::vector<cv::Rect>>> tileMap;	// [stackImageIdx][sourceImageIdx][cropIdx]
};

template<typename T>
class ThreadSafeQueue {
public:
    explicit ThreadSafeQueue(size_t capacity)
        : capacity_(capacity) {}

    // ---------------- Push ----------------

    // Blocking push
    bool push(T value) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_full_.wait(lock, [&] {
            return queue_.size() < capacity_ || closed_ || stop_requested_;
        });

        if (closed_ || stop_requested_)
            return false;

        queue_.push(std::move(value));
        cv_not_empty_.notify_one();
        return true;
    }

    // Timed push
    template<class Rep, class Period>
    bool push_for(T value, const std::chrono::duration<Rep,Period>& timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!cv_not_full_.wait_for(lock, timeout, [&] {
                return queue_.size() < capacity_ || closed_ || stop_requested_;
            })) {
            return false; // timeout
        }

        if (closed_ || stop_requested_)
            return false;

        queue_.push(std::move(value));
        cv_not_empty_.notify_one();
        return true;
    }

    // ---------------- Pop ----------------

    // Blocking pop
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [&] {
            return !queue_.empty() || closed_ || stop_requested_;
        });

        // Immediate abort
        if (stop_requested_)
            return std::nullopt;

        // Graceful close: queue drained
        if (queue_.empty())
            return std::nullopt;

        T value = std::move(queue_.front());
        queue_.pop();
        cv_not_full_.notify_one();
        return value;
    }

    // Timed pop
    template<class Rep, class Period>
    std::optional<T> pop_for(const std::chrono::duration<Rep,Period>& timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!cv_not_empty_.wait_for(lock, timeout, [&] {
                return !queue_.empty() || closed_ || stop_requested_;
            })) {
            return std::nullopt; // timeout
        }

        if (stop_requested_)
            return std::nullopt;

        if (queue_.empty())
            return std::nullopt;

        T value = std::move(queue_.front());
        queue_.pop();
        cv_not_full_.notify_one();
        return value;
    }

    // ---------------- Shutdown ----------------

    // Graceful: no more pushes, drain existing data
    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

    // Immediate abort: drop everything
    void request_stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stop_requested_ = true;
        }
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

    bool closed() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return closed_;
    }

    bool stop_requested() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return stop_requested_;
    }

private:
    size_t capacity_;
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    bool closed_ = false;
    bool stop_requested_ = false;
};
