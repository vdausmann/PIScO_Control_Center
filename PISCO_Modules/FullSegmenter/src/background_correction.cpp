#include "background_correction.hpp"

#include <opencv4/opencv2/highgui.hpp>
#include <opencv4/opencv2/imgproc.hpp>
#include <opencv4/opencv2/core.hpp>


Error correctImages(std::vector<Image>& imageBuffer)
{
	// compute the background via min-max algorithm:
	cv::Mat background;
	try {
		std::vector<cv::Mat> backgroundImages;
		backgroundImages.resize(imageBuffer.size() - 1);
		for (size_t i = 0; i < imageBuffer.size() - 1; i++) {
			cv::min(imageBuffer[i].img, imageBuffer[i + 1].img, backgroundImages[i]);
		}
		background = backgroundImages[0];
		for (size_t i = 1; i < backgroundImages.size(); i++) {
			cv::max(background, backgroundImages[i], background);
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(std::string("Error while computing the background: ") + e.what());
        return error;
    }

	// correct the images
	try {
		for (Image& image: imageBuffer){
			cv::absdiff(image.img, background, image.img);

			cv::Scalar mean, stddev;
			cv::meanStdDev(image.img, mean, stddev);
			image.meanCorrected = mean[0];
			image.stddevCorrected = stddev[0];
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(std::string("Error while subtrackting the background: ") + e.what());
        return error;
    }

	return Error::Success;
}
