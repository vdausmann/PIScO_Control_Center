#include "segmenter.hpp"
#include "reader.hpp"
#include "threadmanager.hpp"
#include "utils.hpp"
#include "writer.hpp"

#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <mutex>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <string>
#include <vector>

int globalCounter = 0;

Info _read(const size_t& threadId, std::mutex& mutex, void* imageBufferIndices, const size_t& taskIdx, const size_t& taskSize, const std::vector<std::string>& files, Index* fileIndices, Image* imageBuffer)
{
    // cast pointer to right type
    Index* taskPtr = (Index*)imageBufferIndices;

    // get file data
    Index fileIdx = fileIndices[threadId];
    Index filesSize = Index(files.size());
    Index maxFileIdx = (threadId + 1) * filesSize / numReaderThreads;
    if (Index(threadId) == numReaderThreads - 1) // last reader thread should handle all remaining files
        maxFileIdx = filesSize;

    Index stop = fileIdx + Index(stackSize);
    if (stop > maxFileIdx || maxFileIdx - stop < Index(stackSize)) { // handle images that are do not fill a stack.
        stop = maxFileIdx;
    }

    // {
    //     std::unique_lock<std::mutex> lock(mutex);
    //     std::cout << fileIdx << " " << stop << " " << maxFileIdx << std::endl;
    // }

    // iterate over files and read images
    Index imageBufferIndex = taskPtr[taskIdx + 1];
    Index size = 0;
    while (fileIdx < stop) {
        Info info = EmptyImage;
        // read files until succes.
        // TODO: The number of indices can be smaller than the stackSize if not enough images where readable or larger than the stackSize if not enough images would remain to fill a stack. Both cases should be handled correctly
        while (info != Success && fileIdx < maxFileIdx) {
            info = readImage(files[fileIdx], imageBuffer[imageBufferIndex].originalImage);
            checkInfo(info, enableDetailedPrinting, enableDetailedPrinting);
            fileIdx++;
        }
        if (info == Success) {
            imageBuffer[imageBufferIndex].fileIdx = fileIdx - 1;
            imageBufferIndex++;
            size++;
        }
    }
    taskPtr[taskIdx] = size;

    // this worker is finished:
    if (fileIdx >= maxFileIdx) {
        return ThreadManagerThisWorkerFinished;
    }

    fileIndices[threadId] = fileIdx;

    return Success;
}

Info finishSegmenterTask(std::mutex& mutex, Image* imageBuffer, Index startPos, Index size, const std::vector<std::string>& files, const std::vector<std::vector<SegmenterObject>>& objects)
{
    try {
        if (saveMode == oneFile) {
            std::unique_lock<std::mutex> lock(mutex);
            for (Index i = 0; i < size; i++) {
                bool newImage = true;
                for (const SegmenterObject& object : objects[i]) {
                    writeSegmenterObject(object, files, newImage);
                    newImage = false;
                }
            }
        } else {
            for (Index i = 0; i < size; i++) {
                bool newImage = true;
                for (const SegmenterObject& object : objects[i]) {
                    writeSegmenterObject(object, files, newImage);
                    newImage = false;
                }
            }
        }
        for (Index i = 0; i < size; i++) {
            cv::Mat img;
            if (saveBackgroundCorrectedImages || saveCrops)
                img = imageBuffer[startPos + i].originalImage;

            if (saveBackgroundCorrectedImages) {
                std::string path = savePath + "/" + splitAllBeforeLast(splitLast(files[imageBuffer[startPos + i].fileIdx], '/'), '.') + ".png";
                cv::imwrite(path, img);
            }

            if (saveCrops) {
                std::string path = savePath + "/crops/" + splitAllBeforeLast(splitLast(files[imageBuffer[startPos + i].fileIdx], '/'), '.');
                for (const SegmenterObject& object : objects[i]) {
                    cv::imwrite(path + "_" + std::to_string(object.id) + ".png", img(object.boundingRect));
                }
            }

            {
                std::unique_lock<std::mutex> lock(mutex);
                globalCounter++;
                progressBar(globalCounter, files.size());
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

Info _detection(Image* imageBuffer, Index startPos, Index size, const std::vector<cv::Mat>& backgrounds, std::vector<std::vector<SegmenterObject>>& objects)
{
    try {
        std::vector<std::vector<cv::Point>> contours;
        cv::Mat background;
        Index backgroundsSize = backgrounds.size();
        for (Index i = 0; i < size; i++) {
            background = backgrounds[i % backgroundsSize];
            cv::absdiff(background, imageBuffer[startPos + i].workingImage, imageBuffer[startPos + i].workingImage);
            std::vector<SegmenterObject> objectsOnImage;

            if (saveBackgroundCorrectedImages || saveCrops)
                imageBuffer[startPos + i].originalImage = imageBuffer[startPos + i].workingImage.clone();

            cv::threshold(imageBuffer[startPos + i].workingImage, imageBuffer[startPos + i].workingImage, 0, 255, cv::THRESH_TRIANGLE);
            cv::findContours(imageBuffer[startPos + i].workingImage, contours, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE);

            int id = 0;
            for (Index j = 0; j < Index(contours.size()); j++) {
                // check if object is large enough to be saved
                double area = cv::contourArea(contours[j]);
                if (area < minObjectArea)
                    continue;
                SegmenterObject object;
                object.fileIdx = imageBuffer[startPos + i].fileIdx;
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

Info _segment(const size_t& threadId, std::mutex& mutex, void* imageBufferIndices, const size_t& taskIdx, const size_t& taskSize, Image* imageBuffer, const std::vector<std::string>& files)
{
    Index* taskPtr = (Index*)imageBufferIndices;
    Index size = taskPtr[taskIdx];
    Index startPos = taskPtr[taskIdx + 1];

    std::vector<cv::Mat> workingImages;
    for (Index i = 0; i < size; i++) {
        imageBuffer[startPos + i].workingImage = imageBuffer[startPos + i].originalImage.clone();
        if (resizeToImageWidthHeight) {
            cv::resize(imageBuffer[startPos + i].workingImage, imageBuffer[startPos + i].workingImage, cv::Size(imageWidth, imageHeight));
        }
        if (invertImages) {
            cv::bitwise_not(imageBuffer[startPos + i].workingImage, imageBuffer[startPos + i].workingImage);
        }
        workingImages.push_back(imageBuffer[startPos + i].workingImage);
    }

    std::vector<cv::Mat> backgrounds;
    int start, end;
    if (numBackgroundImages == size) { // background only needs to be computed once
        backgrounds.resize(1);
        backgroundCorrectionModel(workingImages, backgrounds[0], 0, size);
    } else {
        backgrounds.resize(size);
        for (Index i = 0; i < size; i++) {
            // compute background for every image. The background consits of the numBufferedStacks / 2 images to the left and right, if possible
            if (numBackgroundImages < size) {
                if (i > numBackgroundImages / 2) {
                    if (i < size - numBackgroundImages / 2) {
                        start = i - numBackgroundImages / 2;
                        end = start + numBackgroundImages;
                    } else {
                        end = size;
                        start = end - numBackgroundImages;
                    }
                } else {
                    start = 0;
                    end = numBackgroundImages;
                }
                // print("index " + std::to_string(i) + "start " + std::to_string(start) + " end " + std::to_string(end), true, true);
                backgroundCorrectionModel(workingImages, backgrounds[i], start, end);
            }
        }
    }

    std::vector<std::vector<SegmenterObject>> objects;
    Info result = _detection(imageBuffer, startPos, size, backgrounds, objects);
    checkInfo(result, enableDetailedPrinting, enableDetailedPrinting);

    // finish task
    result = finishSegmenterTask(mutex, imageBuffer, startPos, size, files, objects);
    checkInfo(result, enableDetailedPrinting, enableDetailedPrinting);
    objects.clear();

    // clean up
    backgrounds.clear();
    workingImages.clear();

    return Success;
}

void _taskLoop(const std::vector<std::string>& files)
{
    Index* fileIndices = new Index[numReaderThreads];
    // Index* bufferIndices = new Index[numBufferedStacks * (2 * stackSize + 1)]; // memory layout: { size1, i11, i12, ..., i1N, size2, i21, ... }
    Index* bufferIndices = new Index[numBufferedStacks * 2]; // memory layout: { size1, start1, size2, start2, ... }
                                                             //
    // allocate memory for image buffer. Double the size to allow for stack overflows. This is wastefull of memory, but should be fine as only pointers are stored. The images are not allocated before reading.
    Image* imageBuffer = new Image[2 * bufferSize];

    // allocate memory for buffer and prepare first tasks
    for (Index i = 0; i < numBufferedStacks; i++) {
        bufferIndices[i * 2] = 0;
        bufferIndices[i * 2 + 1] = i * 2 * stackSize;
        // bufferIndices[i * (2 * stackSize + 1)] = 0;
        // for (int j = 0; j < 2 * stackSize; j++) {
        //     bufferIndices[i * (2 * stackSize + 1) + j + 1] = i * 2 * stackSize + j;
        // }
    }

    taskFunction readerFunction = [files, imageBuffer, fileIndices](const size_t& threadId, std::mutex& mutex, void* indices, const size_t& taskIdx, const size_t& taskSize) { return _read(threadId, mutex, indices, taskIdx, taskSize, files, fileIndices, imageBuffer); };
    taskFunction segmenterFunction = [imageBuffer, files](const size_t& threadId, std::mutex& mutex, void* indices, const size_t& taskIdx, const size_t& taskSize) { return _segment(threadId, mutex, indices, taskIdx, taskSize, imageBuffer, files); };

    taskFunction functions[] = { readerFunction, segmenterFunction };

    for (Index i = 0; i < numReaderThreads; i++) {
        fileIndices[i] = files.size() / numReaderThreads * i;
    }

    ThreadManager tmReader(bufferIndices, functions, numReaderThreads, true, numBufferedStacks);
    ThreadManager tmSegmenter(bufferIndices, functions, numSegmenterThreads, true, numBufferedStacks);

    // initialize reader tasks
    Info info;
    for (Index i = 0; i < numBufferedStacks; i++) {
        Task task;
        task.taskIdx = 2 * i;
        task.size = 1;
        task.funcIdx = 0;

        info = tmReader.addTask(task);
        checkInfo(info, enableDetailedPrinting, enableDetailedPrinting);
    }

    Task finishedTask;
    Index counter = 0;
    while (counter < numReaderThreads) {
        tmReader.getFinishedTask(finishedTask);
        checkInfo(finishedTask.threadManagerInfo, enableDetailedPrinting, enableDetailedPrinting);
        checkInfo(finishedTask.taskInfo, enableDetailedPrinting, enableDetailedPrinting);

        if (finishedTask.taskInfo == ThreadManagerThisWorkerFinished)
            counter++;

        Task segmenterTask;
        segmenterTask.taskIdx = finishedTask.taskIdx;
        segmenterTask.size = 1;
        segmenterTask.funcIdx = 1;

        info = tmSegmenter.addTask(segmenterTask);
        checkInfo(info, enableDetailedPrinting, enableDetailedPrinting);

        //////////////////////////////////////////7
        tmSegmenter.getFinishedTask(finishedTask);
        checkInfo(finishedTask.threadManagerInfo, enableDetailedPrinting, enableDetailedPrinting);
        checkInfo(finishedTask.taskInfo, enableDetailedPrinting, enableDetailedPrinting);

        Task readerTask;
        readerTask.taskIdx = finishedTask.taskIdx;
        readerTask.size = 1;
        readerTask.funcIdx = 0;

        info = tmReader.addTask(readerTask);
        checkInfo(info, enableDetailedPrinting, enableDetailedPrinting);
    }

    tmReader.finishThreads();
    tmSegmenter.finishThreads();
    do {
        tmSegmenter.getFinishedTask(finishedTask);
        checkInfo(finishedTask.threadManagerInfo, enableDetailedPrinting, enableDetailedPrinting);
        checkInfo(finishedTask.taskInfo, enableDetailedPrinting, enableDetailedPrinting);
    } while (finishedTask.threadManagerInfo == Success);

    tmReader.cleanUp();
    tmSegmenter.cleanUp();

    // clean up
    delete[] bufferIndices;
    delete[] fileIndices;
    // for (int i = 0; i < 2 * bufferSize; i++) {
    //     imageBuffer[i].workingImage.release();
    //     imageBuffer[i].originalImage.release();
    // }
    delete[] imageBuffer;
}

void runSegmenter()
{
    auto start = std::chrono::high_resolution_clock::now();
    if (saveMode == oneFile)
        checkInfo(initWriter(), enableDetailedPrinting, enableDetailedPrinting);

    std::vector<std::string> files;
    getFiles(sourcePath, files);
    print("Found " + std::to_string(files.size()) + " files");

    if (numReaderThreads * stackSize > Index(files.size())) {
        print(makeYellow("Not enough images to fill all reader threads. Decrease the number of reader threads."), true, true);
    }

    _taskLoop(files);

    // clean up
    objectSaveFile.close();

    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    duration /= 1000;
    print("Duration of segmenter: " + std::to_string(duration) + "s", true, true);
    print("Avg. time per image: " + std::to_string(duration / files.size()) + "s", true, true);
}
