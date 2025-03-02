#include "threadmanager.hpp"
#include <assert.h>
#include <chrono>
#include <functional>
#include <iostream>
#include <thread>

// custom error
constexpr Info ValueNotPos = nextWarning;

struct TaskData {
    int a;
    int b;
    int c;
};

// custom error function to allow printing of custom error
std::string customError(Info infoCode)
{
    const std::unordered_map<Info, std::string> errorMap {
        { ValueNotPos, "Value not positive" },
    };
    try {
        return errorMap.at(infoCode);
    } catch (const std::out_of_range& e) {
        return info(infoCode);
    }
}

Info f(const size_t& threadId, std::mutex& lock, void* taskData, const size_t& taskIdx, const size_t& taskSize)
{
    try {

        TaskData* dataPtr = (TaskData*)taskData;
        if (dataPtr[taskIdx].b < 0) {
            dataPtr[taskIdx].c = -1;
            return ValueNotPos;
        }
        dataPtr[taskIdx].c = dataPtr[taskIdx].a + dataPtr[taskIdx].b;
        std::this_thread::sleep_for(std::chrono::milliseconds(400));

        // {
        // std::unique_lock<std::mutex> l(lock);
        // std::cout << dataPtr[taskIdx].a << "+" << dataPtr[taskIdx].b << "=" << dataPtr[taskIdx].c << std::endl;
        // }
        // data = nullptr;
        return Success;
    } catch (std::exception& e) {
        std::string funcName = __func__;
        std::cout << makeRed("Exception in " + funcName + ": ") << e.what() << std::endl;
        return RuntimeError;
    }
}

void addTasks(ThreadManager& tm, void* taskData, size_t bufferSize)
{
    Info info = Success;
    TaskData* taskDataLocal = (TaskData*)taskData;
    for (size_t i = 0; i < bufferSize; i++) {
        taskDataLocal[i].a = int(i);
        taskDataLocal[i].b = int(i) - 1;
        // taskDataLocal[i].c = 0;

        Task task;
        task.taskIdx = i;
        task.size = 1;
        task.funcIdx = 0;
        info = tm.addTask(task);
        checkInfo(info, true, true);
    }

    Task finishedTask;
    for (size_t i = 0; i < 20; i++) {
        tm.getFinishedTask(finishedTask);
        checkInfo(finishedTask.threadManagerInfo, true, true);
        checkInfo(finishedTask.taskInfo, true, true);

        std::cout << taskDataLocal[finishedTask.taskIdx].a << "+" << taskDataLocal[finishedTask.taskIdx].b << "=" << taskDataLocal[finishedTask.taskIdx].c << std::endl;

        taskDataLocal[finishedTask.taskIdx].a = i;
        taskDataLocal[finishedTask.taskIdx].b = i - 1;

        Task task;
        task.taskIdx = finishedTask.taskIdx;
        task.size = 1;
        task.funcIdx = 0;
        info = tm.addTask(task);
        checkInfo(info, true, true);
    }

    tm.finishThreads();

    while (finishedTask.threadManagerInfo == Success) {
        tm.getFinishedTask(finishedTask);
        checkInfo(finishedTask.threadManagerInfo, true, true);
        checkInfo(finishedTask.taskInfo, true, true);

        std::cout << taskDataLocal[finishedTask.taskIdx].a << "+" << taskDataLocal[finishedTask.taskIdx].b << "=" << taskDataLocal[finishedTask.taskIdx].c << std::endl;
    }

    tm.cleanUp();
}

int main()
{
    errorFunction = customError;

    size_t bufferSize = 5;
    void* taskData = std::malloc(bufferSize * sizeof(TaskData));
    taskFunction taskFunctions[] = { f };

    ThreadManager tm(taskData, taskFunctions, 10, true, bufferSize);
    addTasks(tm, taskData, bufferSize);

    free(taskData);

    return 0;
}
