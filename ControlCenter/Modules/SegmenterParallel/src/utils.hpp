#pragma once
#include "threads.hpp"
#include <functional>
#include <opencv2/core/mat.hpp>
#include <string>

constexpr Error EmptyImage = nextWarning;
constexpr Error UnreadableImageFile = nextWarning + 1;

constexpr Error CVRuntime = nextError;

std::string customError(Error errorCode);

extern std::string sourcePath;
extern std::string savePath;
extern bool enablePrinting;
extern int stackSize;
extern int numBufferedStacks;
extern int numThreads;
extern int imageWidth;
extern int imageHeight;
extern bool resizeToImageWidthHeight;
extern bool invertImages;
extern std::string backgroundCorrectionModelStr;

extern std::function<void(const cv::Mat*, cv::Mat&, int, int)> backgroundCorrectionModel;

extern int bufferSize;

void readParameters(int argc, char* argv[], std::string inputFile);
