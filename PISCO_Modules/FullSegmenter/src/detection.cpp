#include "detection.hpp"
#include "error.hpp"
#include "parser.hpp"
#include "types.hpp"
#include <iostream>
#include <opencv4/opencv2/core.hpp>
#include <opencv4/opencv2/imgproc.hpp>


void computeRegionProps()
{
}

Error detection(std::vector<Image>& imageBuffer, 
		std::unordered_map<size_t, std::vector<SegmenterObject>>& detectedObjects)
{

	for (Image& image: imageBuffer){
		try {
			cv::Mat thresh;
			image.detectionThreshold = cv::threshold(image.img, thresh, e_imageThreshold,
					255, cv::THRESH_BINARY);

			std::vector<std::vector<cv::Point>> contours;
			cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

			// std::cout << "Found " << contours.size() << " objects\n";

			std::vector<SegmenterObject> objects;
			for (std::vector<cv::Point>& contour: contours) {
				double area = cv::contourArea(contour);
				if (area < e_minArea)
					continue;

				cv::Rect boundingBox = cv::boundingRect(contour);

				SegmenterObject object;
				object.contour = contour;
				object.id = image.id;
				object.boundingBox = boundingBox;
				object.area = area;
				objects.push_back(object);
				// double perimeter = cv::arcLength(contour, true);
			}
			detectedObjects[image.id] = objects;
		} catch (const std::exception& e) {
			Error error = Error::RuntimeError;
			error.addMessage(std::string("Error while detecting objects on image " +
						std::to_string(image.id) + ": ") + e.what());
			return error;
		}
	}


	return Error::Success;
}
