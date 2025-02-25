#include "reader.hpp"
#include <algorithm>
#include <filesystem>
#include <iostream>
#include <opencv2/core/mat.hpp>
#include <opencv2/imgcodecs.hpp>

void getFiles(std::string path, std::vector<std::string>& files)
{
    int debugMaxFiles = 60;
    for (const auto& entry : std::filesystem::directory_iterator(path)) {
        if (entry.is_directory()) {
            continue;
        }
        files.push_back(entry.path().string());

        // if (files.size() >= debugMaxFiles)
        //     break;
    }

    // sort files:
    std::sort(files.begin(), files.end());
}

std::optional<ReaderError> readImage(std::string filePath, cv::Mat& image)
{
    try {
        image = cv::imread(filePath, cv::IMREAD_GRAYSCALE);
        if (image.empty()) {
            return ReaderError::emptyImage;
        }
    } catch (cv::Exception& e) {
        return ReaderError::unreadableImageFile;
    }
    return {};
}
