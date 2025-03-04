#pragma once
#include <cstdint>
#include <functional>
#include <string>

// Error/Information handling:
typedef int16_t Info;
// Success is encoded as 0
// Warnings have positive values below 128.
// Infos have positive values above 128.
// Errors have negative values.
// This conventions can easialy
constexpr Info Success = 0;

// Infos
constexpr Info ThreadManagerFinished = 128;
constexpr Info ThreadManagerThisWorkerFinished = 129;
constexpr Info nextInfo = 130;

// Warnings
constexpr Info ThreadManagerMaxTasksReached = 1;
constexpr Info nextWarning = 2;

// Errors
constexpr Info Unknown = -1;
constexpr Info RuntimeError = -2;
constexpr Info nextError = -3;

std::string info(Info infoCode);
extern std::function<std::string(Info)> errorFunction;
void checkInfo(const Info& errorCode, bool printWarnings = true, bool printInfo = true);

std::string makeRed(std::string str);
std::string makeYellow(std::string str);
