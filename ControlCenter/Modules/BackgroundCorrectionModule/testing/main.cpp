#include "background_correction.hpp"
#include <chrono>
#include <cstdio>
#include <iostream>
#include <opencv2/core/mat.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

int main()
{
    std::string inputPath = "/home/tim/Documents/ArbeitTestData/M197_PELAGIOS_Schnitt.mov";

    cv::VideoCapture cap(inputPath);
    cv::Mat frame, background, img, videoImg, backgroundSum;
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

        if (img.empty()) {
            img = cv::Mat(frame.rows, 3 * frame.cols, CV_8U);
            backgroundSum = cv::Mat(frame.rows, frame.cols, CV_64F);
        }

        buffer[idx % numBackgroundImages] = frame;

        if (idx < numBackgroundImages) {
            background = frame;
            // cv::add(frame, backgroundSum, backgroundSum, cv::noArray(), CV_64F);
        } else {
            // averageMethod(buffer, background, 0, numBackgroundImages - 1);
            // minMethod(buffer, background, 0, numBackgroundImages - 1);
            minMaxMethod(buffer, background, 0, numBackgroundImages - 1);
            // medianMethod(buffer, background, 0, numBackgroundImages - 1);
            // rollingAverageMethod(backgroundSum, background, buffer[(idx + numBackgroundImages - 1) % numBackgroundImages], frame, numBackgroundImages);
        }

        frame.copyTo(img(cv::Rect(0, 0, frame.cols, frame.rows)));
        background.copyTo(img(cv::Rect(frame.cols, 0, frame.cols, frame.rows)));
        cv::absdiff(frame, background, frame);
        frame.copyTo(img(cv::Rect(2 * frame.cols, 0, frame.cols, frame.rows)));

        cv::resize(img, videoImg, cv::Size(1500, 500));
        cv::putText(videoImg, "Frame", cv::Point(10, 20), cv::FONT_HERSHEY_SIMPLEX, 0.5, 255);
        cv::putText(videoImg, "Background", cv::Point(510, 20), cv::FONT_HERSHEY_SIMPLEX, 0.5, 255);
        cv::putText(videoImg, "Difference", cv::Point(1010, 20), cv::FONT_HERSHEY_SIMPLEX, 0.5, 255);

        auto end = std::chrono::high_resolution_clock::now();
        double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        std::cout << "Duration of frame: " << duration << "ms" << std::endl;

        cv::imshow("Video", videoImg);
        key = cv::waitKey(1);
        idx++;
    }

    return 0;
}
