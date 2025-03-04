#include "info.hpp"
#include "reader.hpp"
#include "threadmanager.hpp"
#include "utils.hpp"
#include "writer.hpp"

#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <string>
#include <vector>

// TODO: Implementierung von numBackgroundImages, was es ermöglicht, einen background nur für einen Teil des stacks zu berechnen
// TODO: Implement support for stacks smaller than the stackSize

int globalCounter = 0;

void readStackToBuffer(const std::vector<std::string>& files, size_t& fileIdx, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int bufferIdx)
{
    std::string file;
    for (int i = 0; i < stackSize; i++) {
        Info result;
        do {
            file = files[fileIdx];
            fileIdx++;
            result = readImage(file, imageBuffer[bufferIdx]);
            originalImageBuffer[bufferIdx] = imageBuffer[bufferIdx].clone();
            if (result != Success)
                print(customInfo(result) + " in " + file);
        } while (result != Success);
        bufferIdx++;
    }
}

Info readStackToBuffer(const std::vector<std::string>* files, size_t* fileIdx, int* fileIdxBuffer, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int bufferIdx)
{
    try {
        size_t fileIdxVal = fileIdx[0];
        std::string file;
        for (int i = 0; i < stackSize; i++) {
            Info result;
            do {
                file = files->at(fileIdxVal);

                result = readImage(file, imageBuffer[bufferIdx]);
                if (saveBackgroundCorrectedImages)
                    originalImageBuffer[bufferIdx] = imageBuffer[bufferIdx].clone();
                fileIdxBuffer[bufferIdx] = fileIdxVal;

                fileIdxVal++;

                if (result != Success) {
                    print(customInfo(result) + " in " + file);
                }
                checkInfo(result, enableDetailedPrinting, enableDetailedPrinting);

            } while (result != Success);
            bufferIdx++;
        }
        fileIdx[0] = fileIdxVal;
    } catch (cv::Exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Success;
}

// This taskFunction reads one image stack to the buffer
Info readerTaskFunction(Task* task, std::mutex& taskMutex, size_t id, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int* fileIdxBuffer, int startPos, const std::vector<std::string>* files, size_t* fileIdx)
{
    try {
        std::unique_lock<std::mutex> lock(taskMutex);
        if (fileIdx[0] < files->size()) {
            return readStackToBuffer(files, fileIdx, fileIdxBuffer, imageBuffer, originalImageBuffer, startPos);
        } else {
            return ReaderFinished;
        }
    } catch (cv::Exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

Info finishSegmenterTask(std::mutex& taskMutex, cv::Mat* originalImageBuffer, int* fileIdxBuffer, int startPos, const std::vector<std::string>* files, std::vector<std::vector<SegmenterObject>>& objects)
{
    try {
        {
            std::unique_lock<std::mutex> lock(taskMutex);
            for (int i = 0; i < stackSize; i++) {
                bool newImage = true;
                for (const SegmenterObject& object : objects[i]) {
                    writeSegmenterObject(object, files, newImage);
                    newImage = false;
                }

                cv::Mat img;
                if (saveBackgroundCorrectedImages || saveCrops)
                    img = originalImageBuffer[startPos + i];

                if (saveBackgroundCorrectedImages) {
                    std::string path = savePath + "/" + splitAllBeforeLast(splitLast(files->at(fileIdxBuffer[startPos + i]), '/'), '.') + ".png";
                    cv::imwrite(path, img);
                }

                if (saveCrops) {
                    std::string path = savePath + "/crops/" + splitAllBeforeLast(splitLast(files->at(fileIdxBuffer[startPos + i]), '/'), '.');
                    for (const SegmenterObject& object : objects[i]) {
                        cv::imwrite(path + "_" + std::to_string(object.id) + ".png", img(object.boundingRect));
                    }
                }

                globalCounter++;
                progressBar(globalCounter, files->size());
            }
        }
        return Success;
    } catch (cv::Exception& e) {
        // always print exceptions!
        std::cout << "Exception: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

Info detection(cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int bufferStartPos, std::vector<cv::Mat>& backgrounds, int* fileIdxBuffer, std::vector<std::vector<SegmenterObject>>& objects)
{
    try {
        std::vector<std::vector<cv::Point>> contours;
        cv::Mat background;
        size_t backgroundsSize = backgrounds.size();
        for (int i = 0; i < stackSize; i++) {
            background = backgrounds[i % backgroundsSize];
            cv::absdiff(background, imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i]);
            std::vector<SegmenterObject> objectsOnImage;
            if (saveBackgroundCorrectedImages || saveCrops)
                originalImageBuffer[bufferStartPos + i] = imageBuffer[bufferStartPos + i].clone();
            cv::threshold(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i], 0, 255, cv::THRESH_TRIANGLE);
            cv::findContours(imageBuffer[bufferStartPos + i], contours, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);
            int id = 0;
            for (size_t j = 0; j < contours.size(); j++) {
                // check if object is large enough to be saved
                double area = cv::contourArea(contours[j]);
                if (area < minObjectArea)
                    continue;
                SegmenterObject object;
                object.fileIdx = fileIdxBuffer[bufferStartPos + i];
                object.contour = contours[j];
                object.boundingRect = cv::boundingRect(contours[j]);
                object.area = area;
                object.id = id;
                id++;
                objectsOnImage.push_back(object);
            }
            objects.push_back(objectsOnImage);
            contours.clear();
        }
        return Success;
    } catch (cv::Exception& e) {
        std::cout << "Exception in taskSegmenterFunction: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception in taskSegmenterFunction: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

Info taskSegmenterFunction(Task* task, std::mutex& taskMutex, size_t id, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, int bufferStartPos, const std::vector<std::string>* files, int* fileIdxBuffer)
{

    try {
        // print("Received segmenter task starting at " + std::to_string(bufferStartPos) + " with fileIdx " + std::to_string(fileIdx));
        for (int i = 0; i < stackSize; i++) {
            if (resizeToImageWidthHeight)
                cv::resize(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i], cv::Size(imageWidth, imageHeight));
            if (invertImages)
                cv::bitwise_not(imageBuffer[bufferStartPos + i], imageBuffer[bufferStartPos + i]);
        }

        std::vector<cv::Mat> backgrounds;
        int start, end;
        if (numBackgroundImages == stackSize) { // background only needs to be computed once
            backgrounds.resize(1);
            backgroundCorrectionModel(imageBuffer, backgrounds[0], bufferStartPos, bufferStartPos + stackSize);
        } else {
            backgrounds.resize(stackSize);
            for (int i = 0; i < stackSize; i++) {
                // compute background for every image. The background consits of the numBufferedStacks / 2 images to the left and right, if possible
                if (numBackgroundImages < stackSize) {
                    if (i > numBackgroundImages / 2) {
                        if (i < stackSize - numBackgroundImages / 2) {
                            start = i - numBackgroundImages / 2;
                            end = start + numBackgroundImages;
                        } else {
                            end = stackSize;
                            start = end - numBackgroundImages;
                        }
                    } else {
                        start = 0;
                        end = numBackgroundImages;
                    }
                    print("index " + std::to_string(i) + "start " + std::to_string(start) + " end " + std::to_string(end), true, true);
                    backgroundCorrectionModel(imageBuffer, backgrounds[i], start, end);
                }
            }
        }

        std::vector<std::vector<SegmenterObject>> objects;
        Info result = detection(imageBuffer, originalImageBuffer, bufferStartPos, backgrounds, fileIdxBuffer, objects);
        checkInfo(result);

        // finish task
        result = finishSegmenterTask(taskMutex, originalImageBuffer, fileIdxBuffer, bufferStartPos, files, objects);
        checkInfo(result);
        objects.clear();

        // clean up
        backgrounds.clear();
        return Success;
    } catch (cv::Exception& e) {
        std::cout << "Exception in taskSegmenterFunction: " << e.what() << std::endl;
        return CVRuntime;
    } catch (std::exception& e) {
        std::cout << "Exception in taskSegmenterFunction: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

void segmenterLoop(const std::vector<std::string>& files, int* fileIdxBuffer, cv::Mat* imageBuffer, cv::Mat* originalImageBuffer, ThreadManager& tmSegmenter)
{
    Task finishedReaderTask;
    int bufferIdx = 0;
    size_t fileIdx = 0;

    ThreadManager tmReader(numBufferedStacks, 1);
    tmReader.getFinishedTask(finishedReaderTask);

    // start reader tasks:
    while (finishedReaderTask.emptyTask) {
        checkInfo(finishedReaderTask, enableDetailedPrinting, enableDetailedPrinting);
        bufferIdx = finishedReaderTask.getTaskId() * stackSize;
        Task task(bufferIdx);
        task.initTaskFunction(readerTaskFunction, imageBuffer, originalImageBuffer, fileIdxBuffer, bufferIdx, &files, &fileIdx);
        finishedReaderTask = tmReader.addNextTask(task);
    }
    // first reader task is finished, thus a segmenter task can be started:
    checkInfo(finishedReaderTask, enableDetailedPrinting, enableDetailedPrinting);

    Task finishedSegmenterTask;
    tmSegmenter.getFinishedTask(finishedSegmenterTask);
    while (true) {
        bufferIdx = finishedReaderTask.getTaskId();
        print("Finished reader task with id " + std::to_string(bufferIdx));

        Task segmenterTask(bufferIdx);
        segmenterTask.initTaskFunction(taskSegmenterFunction, imageBuffer, originalImageBuffer, bufferIdx, &files, fileIdxBuffer);
        finishedSegmenterTask = tmSegmenter.addNextTask(segmenterTask);
        checkInfo(finishedSegmenterTask, enableDetailedPrinting, enableDetailedPrinting);
        print("segmenterTask send with id " + std::to_string(bufferIdx));

        // only start reader task if valid segmenter task is finished
        if (finishedSegmenterTask.emptyTask) {
            print("Segmenter task finished with empty task");
            Info info = tmReader.getFinishedTaskBlocking(finishedReaderTask);
            checkInfo(info);
        } else {
            print("segmenterTask finished with id " + std::to_string(finishedSegmenterTask.getTaskId()));

            // get finished reader task.
            Info info = tmReader.getFinishedTaskBlocking(finishedReaderTask);
            checkInfo(info, enableDetailedPrinting, enableDetailedPrinting);

            if (finishedReaderTask.infoCode == ReaderFinished) {
                // send stop task:
                Task task = stopTask();
                task.initTaskFunction([](Task*, std::mutex&) { return EmptyTask; });
                finishedReaderTask = tmReader.addNextTask(task);
                checkInfo(finishedReaderTask, enableDetailedPrinting, enableDetailedPrinting);
                break;
            }

            Task readerTask(finishedSegmenterTask.getTaskId());
            readerTask.initTaskFunction(readerTaskFunction, imageBuffer, originalImageBuffer, fileIdxBuffer, finishedSegmenterTask.getTaskId(), &files, &fileIdx);
            // finishedReaderTask = tmReader.addNextTask(readerTask);
            tmReader.addNextTaskNotBlocking(readerTask);
            // checkInfo(finishedReaderTask, enableDetailedPrinting, enableDetailedPrinting);
        }
        print("\n\n");
    }
    // std::cout << "Finished loop" << std::endl;
    tmReader.cleanUp();
}

void runSegmenter()
{
    auto start = std::chrono::high_resolution_clock::now();
    if (saveMode == oneFile)
        checkInfo(initWriter());

    std::vector<std::string> files;
    getFiles(sourcePath, files);
    print("Found " + std::to_string(files.size()) + " files");

    cv::Mat* originalImageBuffer = nullptr;
    if (saveBackgroundCorrectedImages || saveCrops)
        originalImageBuffer = new cv::Mat[bufferSize]; // Images in this buffer will not be changed
    cv::Mat* imageBuffer = new cv::Mat[bufferSize];
    int* fileIdxBuffer = new int[bufferSize];

    // ThreadManager tmSegmenter(numBufferedStacks, numThreads);
    ThreadManager tmSegmenter(numBufferedStacks < numThreads ? numBufferedStacks : numThreads, numThreads - 1);

    // run segmenter loop
    segmenterLoop(files, fileIdxBuffer, imageBuffer, originalImageBuffer, tmSegmenter);

    // send stop signal
    Task finishedTask;
    Task task = stopTask();
    task.initTaskFunction([](Task*, std::mutex&) { return EmptyTask; });
    finishedTask = tmSegmenter.addNextTask(task);
    checkInfo(finishedTask);

    // wait for threads to finish
    tmSegmenter.finishThreads();

    // finish remaining tasks
    Info result = Success;
    while (result == Success && !finishedTask.emptyTask) {
        // int bufferIdx = finishedTask.getTaskId();
        // progressBar(fileIndices[bufferIdx], files.size());
        // print("Finished task with id " + std::to_string(bufferIdx) + " and file index " + std::to_string(fileIndices[bufferIdx]));
        result = tmSegmenter.getFinishedTask(finishedTask);
        checkInfo(finishedTask, false);
    }

    // progressBar(files.size(), files.size());

    // clean up
    objectSaveFile.close();
    tmSegmenter.cleanUp();
    delete[] originalImageBuffer;
    delete[] imageBuffer;
    delete[] fileIdxBuffer;

    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    duration /= 1000;
    print("Duration of segmenter: " + std::to_string(duration) + "s", true, true);
    print("Avg. time per image: " + std::to_string(duration / files.size()) + "s", true, true);
}
