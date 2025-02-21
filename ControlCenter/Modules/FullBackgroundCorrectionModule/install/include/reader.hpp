#pragma once
#include "utils.hpp"
#include <opencv2/core.hpp>

bool readFile(std::string filename, cv::Mat& image, const Settings* settings);
void getAllFiles(std::string dir, std::vector<std::string>& files);
void readNextImageStack(std::vector<std::string>& files, std::vector<cv::Mat>& images, int indexOffset, const Settings* settings);
