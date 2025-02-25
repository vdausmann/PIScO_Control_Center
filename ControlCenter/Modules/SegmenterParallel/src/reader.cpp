#include "reader.hpp"
#include "utils.hpp"
#include <algorithm>
#include <filesystem>
#include <opencv2/core/mat.hpp>
#include <opencv2/imgcodecs.hpp>

void getFiles(std::string path, std::vector<std::string>& files)
{
    for (const auto& entry : std::filesystem::directory_iterator(path)) {
        if (entry.is_directory()) {
            continue;
        }
        files.push_back(entry.path().string());
    }
    std::sort(files.begin(), files.end());
}

Error readImage(std::string filePath, cv::Mat& image)
{
    try {
        image = cv::imread(filePath, cv::IMREAD_GRAYSCALE);
        if (image.empty()) {
            return EmptyImage;
        }
    } catch (cv::Exception& e) {
        return UnreadableImageFile;
    }
    return Success;
}
