#pragma once
#include "info.hpp"
#include <functional>
#include <opencv2/core/mat.hpp>
#include <string>
#include <strings.h>

//////////////////////////////////////////////////////////////
// Type definitions:
//////////////////////////////////////////////////////////////

typedef size_t Index;

// SegmenterObject contains information about a single object found in an image.
struct SegmenterObject {
    std::vector<cv::Point> contour; // Vector of points that enclose the object
    cv::Rect boundingRect; // Bounding rect of the object in the (resized) image. If the image was resized, the bounding box for the original image can be computed with the imageSize that will be saved
    Index fileIdx; // File index of the image the object was found on.
    float area;
    uint32_t id;

    SegmenterObject()
        : contour()
        , boundingRect()
        , fileIdx(0)
        , area(0)
        , id(0)
    {
    }
};

// helper struct to encapsulate the segmenter task data
struct Image {
    cv::Mat workingImage;
    cv::Mat originalImage;
    Index fileIdx;

    ~Image()
    {
        workingImage.release();
        originalImage.release();
    }
};

// Helper enum to determine how the segmenter should save the objects
enum SaveMode : char {
    oneFile,
    oneFilePerImage,
    oneFilePerObject,
};
//////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////
// External variables:
//////////////////////////////////////////////////////////////
// Paths:
extern std::string sourcePath;
extern std::string savePath;

// ThreadManager settings:
extern Index stackSize;
extern Index numBufferedStacks;
extern Index numSegmenterThreads;
extern Index numReaderThreads;

// Image manipulation settings:
extern Index imageWidth;
extern Index imageHeight;
extern bool resizeToImageWidthHeight;
extern bool invertImages;
extern std::string backgroundCorrectionModelStr;
extern Index numBackgroundImages;

// Segmenter settings:
extern double minObjectArea;
extern bool saveContours;
extern bool saveBackgroundCorrectedImages;
extern bool saveCrops;
extern SaveMode saveMode;

// Other:
extern Index progressBarWidth;
extern bool enableDetailedPrinting;

// Helper:
extern std::function<void(const std::vector<cv::Mat>&, cv::Mat&, int, int)> backgroundCorrectionModel;
extern Index bufferSize;
extern std::string saveModeStr;
extern std::string objectSaveFilePath;
extern std::ofstream objectSaveFile;
//////////////////////////////////////////////////////////////

// Custom infos
constexpr Info EmptyImage = nextWarning;
constexpr Info UnreadableImageFile = nextWarning + 1;

constexpr Info ReaderFinished = nextInfo;

constexpr Info CVRuntime = nextError;
constexpr Info WriterErrorInvalidSaveMode = nextError + 1;

std::string customInfo(Info errorCode);

void readParameters(int argc, char* argv[]);
void print(std::string str, bool newLine = true, bool ignoreDetailedPrinting = false);
void progressBar(Index fileIdx, Index filesSize);
