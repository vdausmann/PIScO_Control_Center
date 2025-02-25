#include "segmenter.hpp"
#include "background_correction.hpp"
#include "reader.hpp"
#include "threads.hpp"
#include "utils.hpp"

#include <iostream>
#include <map>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <vector>

// TODO: implement a crop data writer, which can either write all data to one file, all crop data from one image to one file or to one file for each crop
// TODO: implement thread task for saving data as it seems to slow down the execution. Implementation could be done with an additional thread manager using only one thread

void readStackToBuffer(const std::vector<std::string>& files, int& fileIdx, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int bufferIdx)
{
    std::string file;
    for (int i = 0; i < stackSize; i++) {
        Error result;
        do {
            file = files[fileIdx];
            fileIdx++;
            result = readImage(file, originalImageBuffer[bufferIdx]);
            imageBuffer[bufferIdx] = originalImageBuffer[bufferIdx].clone();
            if (result != Success)
                std::cout << customError(result) << " in " << file << std::endl;
        } while (result != Success);
        bufferIdx++;
    }
}

Error taskFunction(Task* task, cv::Mat* imageBuffer, int bufferStartPos, std::vector<std::vector<cv::Point>>* contours)
{
    if (task->emptyTask) {
        return EmptyTask;
    }

    try {
        printf("Received task starting at %d\n", bufferStartPos);
        for (int i = 0; i < stackSize; i++) {
            if (resizeToImageWidthHeight)
                cv::resize(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i], cv::Size(imageWidth, imageHeight));
            if (invertImages)
                cv::bitwise_not(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i]);
        }

        cv::Mat background;
        backgroundCorrectionModel(imageBuffer, background, bufferStartPos, bufferStartPos + stackSize);

        for (int i = 0; i < stackSize; i++) {
            cv::absdiff(background, imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i]);
            cv::threshold(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i], 0, 255, cv::THRESH_TRIANGLE);
            cv::findContours(imageBuffer[bufferStartPos + i], contours[bufferStartPos + i], cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);
        }

        background.release();
        return Success;
    } catch (cv::Exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return Runtime;
    }
    return Unknown;
}

std::string splitLast(const std::string& str, char c)
{
    std::stringstream stream(str);
    std::string segment;
    std::vector<std::string> seglist;
    while (std::getline(stream, segment, c)) {
        seglist.push_back(segment);
    }
    return seglist.back();
}

std::string splitAllBeforeLast(const std::string& str, char c)
{
    std::stringstream stream(str);
    std::string segment;
    std::vector<std::string> seglist;
    while (std::getline(stream, segment, c)) {
        seglist.push_back(segment);
    }
    std::string res = "";
    for (int i = 0; i < seglist.size() - 1; i++) {
        res += seglist[i] + ".";
    }
    return res.substr(0, res.size() - 1);
}

Error finishTask(cv::Mat* originalImageBuffer, int startPos, std::vector<std::vector<cv::Point>>* contours, const std::vector<std::string>& files, int fileIdx)
{
    try {
        for (int i = 0; i < stackSize; i++) {
            // std::cout << "Showing task with id " << startPos + i << std::endl;
            if (resizeToImageWidthHeight)
                cv::resize(originalImageBuffer[startPos + i], originalImageBuffer[startPos + i], cv::Size(imageWidth, imageHeight));
            cv::cvtColor(originalImageBuffer[startPos + i], originalImageBuffer[startPos + i], cv::COLOR_GRAY2BGR);
            cv::drawContours(originalImageBuffer[startPos + i], contours[startPos + i], -1, cv::Scalar(0, 255, 0));
            // cv::imshow("Image", originalImageBuffer[startPos + i]);
            // cv::waitKey(50);

            std::string path = savePath + "/" + splitAllBeforeLast(splitLast(files[fileIdx + i], '/'), '.') + ".png";
            // std::cout << path << std::endl;
            cv::imwrite(path, originalImageBuffer[startPos + i]);
        }
        return Success;
    } catch (cv::Exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return Runtime;
    }
    return Unknown;
}

void segmenterLoop(int& fileIdx, const std::vector<std::string>& files, std::map<int, int>& fileIndices, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, ThreadManager& tm, std::vector<std::vector<cv::Point>>* contours)
{
    Task finishedTask;
    int bufferIdx = 0;
    tm.getFinishedTask(finishedTask);

    // load first image stack
    readStackToBuffer(files, fileIdx, imageBuffer, originalImageBuffer, bufferIdx);

    while (fileIdx < files.size()) {
        printf("File idx: %d\n", fileIdx);
        if (!finishedTask.emptyTask) {
            bufferIdx = finishedTask.getTaskId();
            Error result = finishTask(originalImageBuffer, bufferIdx, contours, files, fileIndices[bufferIdx]);
            checkError(result);
            printf("Finished task with id %d\n", bufferIdx);
        } else {
            // handling of ThreadManager initial tasks
            bufferIdx = finishedTask.getTaskId() * stackSize;
        }

        fileIndices[bufferIdx] = fileIdx;
        printf("Filling buffer from index %d\n", bufferIdx);
        readStackToBuffer(files, fileIdx, imageBuffer, originalImageBuffer, bufferIdx);

        Task task(bufferIdx);
        task.initTaskFunction(taskFunction, imageBuffer, bufferIdx, contours);

        finishedTask = tm.addNextTask(task);

        checkError(finishedTask, enablePrinting);
    }
}

void runSegmenter()
{
    std::vector<std::string> files;
    getFiles(sourcePath, files);
    printf("Found %ld files\n", files.size());

    cv::Mat* originalImageBuffer = new cv::Mat[bufferSize]; // Images in this buffer will not be changed
    cv::Mat* imageBuffer = new cv::Mat[bufferSize];
    std::map<int, int> fileIndices;

    std::vector<std::vector<cv::Point>>* contours = new std::vector<std::vector<cv::Point>>[bufferSize];

    int bufferIdx = 0;
    int fileIdx = 0;

    ThreadManager tm(numBufferedStacks, numThreads);

    // run segmenter loop
    segmenterLoop(fileIdx, files, fileIndices, imageBuffer, originalImageBuffer, tm, contours);

    // send stop signal
    Task finishedTask;
    Task task = stopTask();
    task.initTaskFunction(taskFunction, originalImageBuffer, 0, contours);
    finishedTask = tm.addNextTask(task);

    // wait for threads to finish
    tm.finishThreads();

    // finish remaining tasks
    Error result = tm.getFinishedTask(finishedTask);
    while (result == Success && !finishedTask.emptyTask) {
        bufferIdx = finishedTask.getTaskId();
        // printf("Finished task with id %d\n", bufferIdx);
        Error error = finishTask(originalImageBuffer, bufferIdx, contours, files, fileIndices[bufferIdx]);
        checkError(error);
        result = tm.getFinishedTask(finishedTask);
    }

    std::cout << "Finished background correction" << std::endl;
    tm.cleanUp();
}
