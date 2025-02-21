#pragma once
#include <opencv4/opencv2/core.hpp>

void minMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
void minMaxMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
void averageMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
void rollingAverageMethod(cv::Mat& backgroundSum, cv::Mat& background, const cv::Mat& oldImage, const cv::Mat& newImage, int numBackgroundImages);
void medianMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos);
