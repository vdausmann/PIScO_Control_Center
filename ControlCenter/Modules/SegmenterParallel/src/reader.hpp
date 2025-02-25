#pragma once
#include <opencv2/core/mat.hpp>
#include <optional>
#include <string>
#include <vector>

enum class ReaderError {
    emptyImage,
    unreadableImageFile,
};

std::optional<ReaderError> readImage(std::string filePath, cv::Mat& image);
void getFiles(std::string path, std::vector<std::string>& files);
