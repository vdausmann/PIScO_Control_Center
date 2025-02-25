#include "threads.hpp"
#include <assert.h>
#include <chrono>
#include <iostream>
#include <thread>

// custom error
constexpr Error ValueNotPos = nextWarning;

// custom error function to allow printing of custom error
std::string customError(Error errorCode)
{
    const std::unordered_map<Error, std::string> errorMap {
        { ValueNotPos, "Value not positive" },
    };
    try {
        return errorMap.at(errorCode);
    } catch (const std::out_of_range& e) {
        return error(errorCode);
    }
}

Error taskFunction(Task* task, int a, int b, int* c, int idx)
{
    try {
        if (b < 0) {
            c[idx] = -1;
            return ValueNotPos;
        }
        c[idx] = a + b;
        std::this_thread::sleep_for(std::chrono::milliseconds(400));
        return Success;
    } catch (std::exception& e) {
        // return std::string("Exception: ") + e.what();
        // task->errorMessage = std::string("Exception: ") + e.what();
        return Runtime;
    }
}

void addTasks(ThreadManager& tm)
{
    int c[10];
    for (int i = 0; i < 10; i++) {
        Task task(i);
        task.initTaskFunction(taskFunction, i, i - 1, c, i);
        if (i == 9) {
            task.softStopThreadManager = true;
        }

        Task finishedTask = tm.addNextTask(task);
        checkError(finishedTask);
    }

    tm.cleanUp();
    for (int i = 0; i < 10; i++)
        std::cout << c[i] << std::endl;
}

int main()
{
    errorFunction = customError;
    ThreadManager tm(5, 5);
    addTasks(tm);

    return 0;
}
