#include "background_correction.hpp"
#include <opencv2/core.hpp>
#include <opencv2/core/mat.hpp>

void checkErrors(int bufferStartPos, int bufferEndPos)
{
    if (bufferStartPos >= bufferEndPos)
        throw std::invalid_argument("Buffer start position must be less than buffer end position.");
}

/* Min-Method for background correction. Computes the pixelwise minimum of the images in the buffer, starting at position bufferStartPos and ending at position bufferEndPos. The Min-Method can efficiently compute a near perfect background for images with dark background and bright objects (e.g. inverted PISCO images). For a perfect background, the real background of each pixel needs to be visible only once in all images. */
void minMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    background = imageBuffer[bufferStartPos].clone();
    for (int i = bufferStartPos + 1; i < bufferEndPos; i++) {
        cv::min(background, imageBuffer[i], background);
    }
}

/* Min-Max-Method for background correction. Same as the Min-Method, but with an additional calculation of the pairwise maximum of the images before computing the minimum. This reduces the artefacts from diffraction of the objects, which can be brighter (darker in the inverted images) than the background. */
void minMaxMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    cv::Mat helper;
    cv::max(imageBuffer[bufferStartPos], imageBuffer[bufferStartPos + 1], background);
    for (int i = bufferStartPos + 2; i < bufferEndPos; i += 2) {
        cv::max(imageBuffer[i], imageBuffer[i + 1], helper);
        cv::min(background, helper, background);
    }
    helper.release();
}

/* Average-Method for background correction. Computes the pixelwise average of the images in the buffer, starting at position bufferStartPos and ending at position bufferEndPos. The Average-Method is fast, but lacks accuracy. Using more images to compute the background ensures a higher accuracy. */
void averageMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    cv::Mat helper;
    helper = imageBuffer[bufferStartPos].clone();
    helper.convertTo(helper, CV_64F);
    for (int i = bufferStartPos + 1; i < bufferEndPos; i++) {
        cv::add(helper, imageBuffer[i], helper, cv::noArray(), CV_64F);
    }
    cv::divide(helper, double(bufferEndPos - bufferStartPos), helper);
    helper.convertTo(background, CV_8U);
    helper.release();
}

/* Rolling Average-Method for background correction. Same as Average-Method, but more efficiently if an additional rolling background sum is stored. First, oldImage is subtracted from the background sum, then the new image is added and the background will be computed from the rolling sum. */
void rollingAverageMethod(cv::Mat& backgroundSum, cv::Mat& background, const cv::Mat& oldImage, const cv::Mat& newImage, int numBackgroundImages)
{
    cv::subtract(backgroundSum, oldImage, backgroundSum, cv::noArray(), CV_64F);
    cv::add(backgroundSum, newImage, backgroundSum, cv::noArray(), CV_64F);
    cv::divide(backgroundSum, numBackgroundImages, background, 1, CV_64F);
    background.convertTo(background, CV_8U);
}

void medianMethod(const std::vector<cv::Mat>& imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    int rows = imageBuffer[0].rows;
    int cols = imageBuffer[0].cols;
    int channels = imageBuffer[0].channels();
    if (channels > 1)
        throw std::invalid_argument("Median method does not support color images.");

    int N = bufferEndPos - bufferStartPos;

    // Convert grayscale images to a single channel 3D matrix: (N, rows*cols)
    cv::Mat imageStack(N, rows * cols, imageBuffer[0].type());
    for (int i = 0; i < N; ++i) {
        if (imageBuffer[i].rows != rows || imageBuffer[i].cols != cols || imageBuffer[i].type() != imageBuffer[0].type()) {
            throw std::invalid_argument("All images must have the same size and type.");
        }
        imageBuffer[i].reshape(1, 1).copyTo(imageStack.row(i)); // Flatten and copy
    }
    // Sort along the first axis (depth)
    cv::sort(imageStack, imageStack, cv::SORT_EVERY_COLUMN);
    int medianIndex = N / 2;
    cv::Mat medianFlattened = imageStack.row(medianIndex);
    background = medianFlattened.reshape(channels, rows);
}

void minMethodPtr(const cv::Mat* imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    background = imageBuffer[bufferStartPos].clone();
    for (int i = bufferStartPos + 1; i < bufferEndPos; i++) {
        cv::min(background, imageBuffer[i], background);
    }
}

/* Min-Max-Method for background correction. Same as the Min-Method, but with an additional calculation of the pairwise maximum of the images before computing the minimum. This reduces the artefacts from diffraction of the objects, which can be brighter (darker in the inverted images) than the background. */
void minMaxMethodPtr(const cv::Mat* imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    cv::Mat helper;
    cv::max(imageBuffer[bufferStartPos], imageBuffer[bufferStartPos + 1], background);
    for (int i = bufferStartPos + 2; i < bufferEndPos; i += 2) {
        cv::max(imageBuffer[i], imageBuffer[i + 1], helper);
        cv::min(background, helper, background);
    }
    helper.release();
}

/* Average-Method for background correction. Computes the pixelwise average of the images in the buffer, starting at position bufferStartPos and ending at position bufferEndPos. The Average-Method is fast, but lacks accuracy. Using more images to compute the background ensures a higher accuracy. */
void averageMethodPtr(const cv::Mat* imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    cv::Mat helper;
    helper = imageBuffer[bufferStartPos].clone();
    helper.convertTo(helper, CV_64F);
    for (int i = bufferStartPos + 1; i < bufferEndPos; i++) {
        cv::add(helper, imageBuffer[i], helper, cv::noArray(), CV_64F);
    }
    cv::divide(helper, double(bufferEndPos - bufferStartPos), helper);
    helper.convertTo(background, CV_8U);
    helper.release();
}

void medianMethodPtr(const cv::Mat* imageBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    checkErrors(bufferStartPos, bufferEndPos);
    int rows = imageBuffer[0].rows;
    int cols = imageBuffer[0].cols;
    int channels = imageBuffer[0].channels();
    if (channels > 1)
        throw std::invalid_argument("Median method does not support color images.");

    int N = bufferEndPos - bufferStartPos;

    // Convert grayscale images to a single channel 3D matrix: (N, rows*cols)
    cv::Mat imageStack(N, rows * cols, imageBuffer[0].type());
    for (int i = 0; i < N; ++i) {
        if (imageBuffer[i].rows != rows || imageBuffer[i].cols != cols || imageBuffer[i].type() != imageBuffer[0].type()) {
            throw std::invalid_argument("All images must have the same size and type.");
        }
        imageBuffer[i].reshape(1, 1).copyTo(imageStack.row(i)); // Flatten and copy
    }
    // Sort along the first axis (depth)
    cv::sort(imageStack, imageStack, cv::SORT_EVERY_COLUMN);
    int medianIndex = N / 2;
    cv::Mat medianFlattened = imageStack.row(medianIndex);
    background = medianFlattened.reshape(channels, rows);
}
