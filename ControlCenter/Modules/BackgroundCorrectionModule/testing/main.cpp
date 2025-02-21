#include "background_correction.hpp"
#include <chrono>
#include <cstdio>
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

int main()
{
    std::string inputPath = "/home/tim/Documents/ArbeitTestData/M197_PELAGIOS_Schnitt.mov";

    cv::VideoCapture cap(inputPath);
    cv::Mat frame, background, img;
    int numBackgroundImages = 10;
    std::vector<cv::Mat> buffer;
    buffer.resize(numBackgroundImages);
    char key;

    if (!cap.isOpened())
        throw "Could not open video file";

    int idx = 0;
    while (true) {
        auto start = std::chrono::high_resolution_clock::now();
        cap >> frame;
        if (frame.empty() || key == 'q')
            break;

        cv::cvtColor(frame, frame, cv::COLOR_BGR2GRAY);
        cv::resize(frame, frame, cv::Size(500, 500));

        if (img.empty())
            img = cv::Mat(frame.rows, 2 * frame.cols, CV_8U);

        buffer[idx % numBackgroundImages] = frame;

        if (idx < numBackgroundImages)
            background = frame;
        else {
            // averageMethod(buffer, background, 0, numBackgroundImages - 1);
            // minMethod(buffer, background, 0, numBackgroundImages - 1);
            minMaxMethod(buffer, background, 0, numBackgroundImages - 1);
            // medianMethod(buffer, background, 0, numBackgroundImages - 1);
        }

        frame.copyTo(img(cv::Rect(0, 0, frame.cols, frame.rows)));
        background.copyTo(img(cv::Rect(frame.cols, 0, frame.cols, frame.rows)));

        auto end = std::chrono::high_resolution_clock::now();
        double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        std::cout << "Duration of frame: " << duration << "ms" << std::endl;

        cv::imshow("Video", img);
        key = cv::waitKey(1);
        idx++;
    }

    return 0;
}
