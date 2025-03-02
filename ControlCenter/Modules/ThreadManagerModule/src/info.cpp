#include "info.hpp"
#include <iostream>
#include <stdexcept>

std::string makeRed(std::string str)
{
    std::string helper = "\033[31m" + str + "\033[0m";
    return helper;
}

std::string makeYellow(std::string str)
{
    std::string helper = "\033[33m" + str + "\033[0m";
    return helper;
}

std::string makeBlue(std::string str)
{
    std::string helper = "\033[34m" + str + "\033[0m";
    return helper;
}

std::string info(Info infoCode)
{
    const std::unordered_map<Info, std::string> errorMap {
        { Success, "Success" },
        { ThreadManagerFinished, "ThreadManager has finished" },
        { ThreadManagerMaxTasksReached, "Maximum number of tasks reached" },
        { RuntimeError, "Runtime error" },
        { Unknown, "Unknown error" },
    };

    try {
        return errorMap.at(infoCode);
    } catch (const std::out_of_range& e) {
        return "Invalid error code: " + std::to_string(infoCode);
    }
}

std::function<std::string(Info)> errorFunction = info;

void checkInfo(const Info& infoCode, bool printWarnings, bool printInfo)
{
    // warning
    if (infoCode > 0 && printWarnings)
        std::cout << makeYellow("Warning: " + errorFunction(infoCode)) << std::endl;
    // info
    else if (infoCode > 127 && printInfo)
        std::cout << makeBlue("Info: " + errorFunction(infoCode)) << std::endl;
    // error
    else if (infoCode < 0)
        std::cout << makeRed("Error: " + errorFunction(infoCode)) << std::endl;
}
