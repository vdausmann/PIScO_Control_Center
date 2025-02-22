#include "reader.hpp"
#include <filesystem>
#include <iostream>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

bool readFile(std::string filename, cv::Mat& image, const Settings* settings)
{
    image = cv::imread(filename, cv::IMREAD_GRAYSCALE);
    if (image.empty()) {
        std::cerr << "Error: Unable to read the image." << std::endl;
        return false;
    }

    // std::cout << "Reading image with size " << image.rows << "x" << image.cols << "" << std::endl;
    if (settings->resize && image.rows != settings->imageHeight && image.cols != settings->imageWidth) {
        // std::cout << "Resizing image" << std::endl;
        cv::resize(image, image, cv::Size(settings->imageWidth, settings->imageHeight));
    }
    return true;
}

void getAllFiles(std::string dir, std::vector<std::string>& files)
{
    // int debugMaxFiles = 20;
    for (const auto& entry : std::filesystem::directory_iterator(dir)) {
        if (entry.is_directory()) {
            continue;
        }
        files.push_back(entry.path().string());
        // if (files.size() >= debugMaxFiles) {
        //     break;
        // }
    }
    // sort files:
    std::sort(files.begin(), files.end());
}

void readNextImageStack(std::vector<std::string>& files, std::vector<cv::Mat>& images, int startPos, int endPos, const Settings* settings)
{
    for (int i = startPos; i < endPos; i++) {
        if (files.empty()) {
            std::cout << "No more files to read." << std::endl;
            break;
        }
        std::string filename = files.back();
        files.pop_back();
        cv::Mat image;
        bool success = readFile(filename, image, settings);
        if (!success) {
            continue;
        }
        images[i] = image;
    }
}

// Einlesen der Bilder in einen Buffer von fester Größe, andere Methoden bekommen nur den Pointer zu den Bildern und müssen irgendwie zurück kommunizieren, wenn sie fertig sind mit den Bildern, um diese aus dem Buffer zu entfernen
