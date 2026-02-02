#include "reader.hpp"
#include "error.hpp"
#include "parser.hpp"

#include <iostream>
#include <filesystem>
#include <algorithm>
#include <opencv2/imgproc.hpp>
#include <string>
#include <opencv4/opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>



/*
 *	Finds all valid image files in the externally given source path. Valid image files
 *	are ending with either png, tif or jpg. The files are sorted by name and pushed to 
 *	the files vector.
 */
Error getFiles(std::vector<std::string>& files)
{
    try {
        for (const auto& entry : std::filesystem::directory_iterator(e_sourcePath)) {
            if (entry.is_directory()) {
                continue;
            }
            std::string path = entry.path().string();
            std::string filetype = path.substr(path.size() - 3, path.size());
            if (filetype == "png" || filetype == "tif" || filetype == "jpg") {
                files.push_back(path);
            }
        }
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage("Error on getting files from directory '" + e_sourcePath +
                         "'. Error: \n" + e.what());
        return error;
    }

    std::sort(files.begin(), files.end());
    return Error::Success;
}


/*
 *	Helper function to read images into memory.
 */
Error readImage(Image& image, const std::string& filename)
{
    cv::ImreadModes colorMode =
        e_grayscaleInput ? cv::IMREAD_GRAYSCALE : cv::IMREAD_COLOR;

    try {
        image.img = cv::imread(filename, colorMode);
    } catch (const cv::Exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(e.what());
        return error;
    }

    if (image.img.empty()) {
        Error error = Error::EmptyImage;
        error.addMessage("Empty image at '" + filename);
        return error;
    }

	if (image.img.cols > 2560 || image.img.rows > 2560) {
		cv::resize(image.img, image.img, cv::Size(2560, 2560));
	}
	// check for corrupted image:
	cv::Scalar mean, stddev;
	cv::meanStdDev(image.img, mean, stddev);
    if (stddev[0] < e_minStdDev || mean[0] < e_minMean) {
        Error error = Error::CorruptedImage;
        error.addMessage("Corrupted image at '" + filename);
        return error;
	}

	// TODO: adapt to color images:
	image.meanOrg = mean[0];
	image.stddevOrg = stddev[0];

    return Error::Success;
}


/*
 *	Reads a stack of images into the imageBuffer. The number of images per stack is given
 *	by the external parameter e_imageStackSize.
 */
Error getNextImages(std::vector<Image>& imageBuffer, const std::vector<std::string>& files,
		size_t& nextImageIndex)
{
    try {
		imageBuffer.clear();
		size_t stackSize = e_imageStackSize;
		if (files.size() - nextImageIndex - e_imageStackSize < e_imageStackSize)
			stackSize = files.size() - nextImageIndex;

		imageBuffer.reserve(stackSize);
		while (nextImageIndex < files.size() && imageBuffer.size() < stackSize) {
			Image image;
			Error error = readImage(image, files[nextImageIndex]);

			// empty or corrupted images are treated as warnings
			if (error == Error::Success) {	
				image.id = nextImageIndex;
				imageBuffer.push_back(image);
			} else {
				error.check();
			}
			nextImageIndex++;
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage("Error on getting files from directory '" + e_sourcePath +
                         "'. Error: \n" + e.what());
        return error;
    }
	return Error::Success;
}
