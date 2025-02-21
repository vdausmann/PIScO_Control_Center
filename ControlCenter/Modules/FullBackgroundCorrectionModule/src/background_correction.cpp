#include "background_correction.hpp"

/* Min-Method for background correction. Computes the pixelwise minimum of the images in the buffer, starting at position bufferStartPos and ending at position bufferEndPos. The Min-Method can efficiently compute a near perfect background for images with dark background and bright objects (e.g. inverted PISCO images). For a perfect background, the real background of each pixel needs to be visible only once in all images. */
void minMethod(const std::vector<cv::Mat>& threadLocalBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    background = threadLocalBuffer[bufferStartPos].clone();
    for (int i = bufferStartPos + 1; i < bufferEndPos; i++) {
        cv::min(background, threadLocalBuffer[i], background);
    }
}

/* Min-Max-Method for background correction. Same as the Min-Method, but with an additional calculation of the pairwise maximum of the images before computing the minimum. This reduces the artefacts from diffraction of the objects, which can be brighter (darker in the inverted images) than the background. */
void minMaxMethod(const std::vector<cv::Mat>& threadLocalBuffer, cv::Mat& background, int bufferStartPos, int bufferEndPos)
{
    cv::Mat helper;
    cv::max(threadLocalBuffer[bufferStartPos], threadLocalBuffer[bufferStartPos + 1], background);
    for (int i = bufferStartPos + 2; i < bufferEndPos; i += 2) {
        cv::max(threadLocalBuffer[i], threadLocalBuffer[i + 1], helper);
        cv::min(background, helper, background);
    }
    helper.release();
}
