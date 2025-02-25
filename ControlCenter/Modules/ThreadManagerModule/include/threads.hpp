#pragma once

#include <atomic>
#include <condition_variable>
#include <cstdint>
#include <functional>
#include <iostream>
#include <mutex>
#include <queue>
#include <thread>
#include <vector>

// Error handling:
typedef int Error;
// Success is encoded as 0
// Warnings have positive values.
// Errors have negative values.
// This conventions can easialy
constexpr Error Success = 0;

// Warnings
constexpr Error EmptyTask = 1;
constexpr Error NoFinishedTasksAvailable = 2;
constexpr Error nextWarning = 3;

// Errors
constexpr Error Unknown = -1;
constexpr Error TaskFunctionNotSet = -2;
constexpr Error Runtime = -3;
constexpr Error nextError = -4;

std::string error(Error errorCode);
extern std::function<std::string(Error)> errorFunction;

/* Task struct holds a function that will be called when the task is run. The first argument of the task
 * function has to be a pointer to a task. This allows different behavior of the task function depending on
 * the task data. All other arguments needed for the task function are passed in the initTaskFunction method
 * and will be used to call the task function. Passing by reference is not possible. Instead pointers can
 * be used. The task function will return an optional errorMessage which is stored in the tasks errorMessage
 * variable. The tasks errorMessage can for example be handled in the addNextTask function from the
 * ThreadManager. Tasks also can be empty. This case should be handled in the task function. The last task
 * that will be send to the thread manager should have a stop signal. Here, an empty task can be used. The
 * id provided upon creation of a task can be usefull when receiving the finished task.
 */
struct Task {
private:
    std::function<Error()> _taskFunction;
    int _taskId;

public:
    Error errorCode;
    bool softStopThreadManager;
    bool hardStopThreadManager;
    bool emptyTask;

    int getTaskId() const { return _taskId; }

    Error runTask();

    void makeEmpty()
    {
        emptyTask = true;
        errorCode = EmptyTask;
    }

    Task(int id)
        : emptyTask(false)
        , softStopThreadManager(false)
        , hardStopThreadManager(false)
        , _taskId(id)
    {
    }

    Task()
        : emptyTask(false)
        , softStopThreadManager(false)
        , hardStopThreadManager(false)
        , _taskId(-1)
    {
    }

    // Looks complicated, but just allows the constructor to be called with a function and as many arguments
    // as needed for this function. The function can than be called on runTask(). Carefull: passing by
    // reference is not possible!
    // thanks ChatGPT
    template <typename Callable, typename... Args>
    void initTaskFunction(Callable&& func, Args... args)
    {
        // Store a lambda that captures the function and its arguments
        _taskFunction = [func = std::forward<Callable>(func), ... capturedArgs = std::forward<Args>(args), this]() mutable -> Error {
            // _taskFunction = [func = std::forward<Callable>(func), tupleArgs = std::make_tuple(std::ref(args)...)]() mutable -> std::optional<std::string> {
            try {
                return func(this, capturedArgs...);
                // return std::apply(func, tupleArgs);
            } catch (const std::exception& e) {
                std::cout << std::string("Exception: ") + e.what() << std::endl;
                return Runtime;
            } catch (...) {

                return Runtime;
            }
        };
    }
};

Task emptyTask();
Task stopTask();

void checkError(const Task& finishedTask, bool printWarnings = true);

/* ThreadManager class. The class starts _numThreads threads and provides the threads with Tasks to be run.
 * The preloaded tasks (up to _maxQueueSize tasks) are stored in the _availableTasksQueue. The finished tasks
 * are stored in the _finishedTasksQueue. New tasks can only be added when there is at least one finished task.
 * The new tasks are added via the addNextTask method, which will return the finished task that is replaced.
 * The ThreadManager runs automatically after creation and waits for tasks to be added. An external source
 * calls the addNextTask function and provides the new task from there. The function blocks the external
 * source until the new task is added to _availableTasksQueue. After that, a worker thread will be started
 * with the new task.
 */
class ThreadManager {
private:
    int _maxQueueSize;
    int _numThreads;
    std::mutex _taskMutex, _mainMutex;
    std::queue<Task> _availableTasksQueue, _finishedTasksQueue;
    std::condition_variable _taskCondition, _mainCondition;
    std::vector<std::thread> _threads;
    std::function<Task(Task&)> _getNewTaskFunction;
    std::atomic<bool> _softStop, _hardStop;
    bool joined;

    void worker();

public:
    ThreadManager(int maxQueueSize, int numThreads);
    Task addNextTask(Task& newTask);
    void cleanUp();
    void start();
    void finishThreads();
    Error getFinishedTask(Task& task);
    ~ThreadManager();
};
