#pragma once
#include "info.hpp"
#include <opencv2/core/mat.hpp>
#include <string>
#include <vector>

Info readImage(std::string filePath, cv::Mat& image);
void getFiles(std::string path, std::vector<std::string>& files);
