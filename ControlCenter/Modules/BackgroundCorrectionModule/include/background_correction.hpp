#pragma once
#include "utils.hpp"
#include <opencv4/opencv2/core.hpp>

void minMethod(const std::vector<cv::Mat>& threadLocalBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
void minMaxMethod(const std::vector<cv::Mat>& threadLocalBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
