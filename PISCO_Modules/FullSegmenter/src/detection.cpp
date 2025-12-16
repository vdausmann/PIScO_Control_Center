#include "detection.hpp"
#include "error.hpp"
#include "parser.hpp"
#include "types.hpp"
#include <cmath>
#include <iostream>
#include <opencv2/core/mat.hpp>
#include <opencv4/opencv2/core.hpp>
#include <opencv4/opencv2/imgproc.hpp>


void computeRegionProps(const std::vector<cv::Point>& contour, Objects& objects)
{
	// TODO: this needs better handling!
	try {
		cv::Rect bbox = cv::boundingRect(contour);
		objects.width.push_back(bbox.width);
		objects.height.push_back(bbox.height);
		objects.bx.push_back(bbox.x);
		objects.by.push_back(bbox.y);
		objects.boundingBoxArea.push_back(bbox.area());

		objects.area_exc.push_back(cv::contourArea(contour));

		cv::Mat mask = cv::Mat::zeros(bbox.height, bbox.width, CV_8U);
		cv::drawContours(mask, std::vector<std::vector<cv::Point>>{contour}, -1, 255,
				cv::FILLED, cv::LINE_8, cv::noArray(), INT_MAX, cv::Point(-bbox.x, -bbox.y));

		cv::Mat filled = mask.clone();
		cv::floodFill(filled, cv::Point(0, 0), 255);
		cv::bitwise_not(filled, filled);
		cv::Mat filledMask = mask | filled;
		objects.area_rprops.push_back(cv::countNonZero(filledMask));

		objects.area_percentage.push_back(1 - (objects.area_exc.back()
					/ objects.area_rprops.back()));

		objects.perimeter.push_back(cv::arcLength(contour, true));


		objects.circ.push_back((4.0 * CV_PI * objects.area_rprops.back()) / 
				(objects.perimeter.back() * objects.perimeter.back()));
		objects.circex.push_back((4.0 * CV_PI * objects.area_exc.back()) /
				(objects.perimeter.back() * objects.perimeter.back()));

		cv::Moments m = cv::moments(contour);
		objects.centroidx.push_back(m.m10 / m.m00);
		objects.centroidy.push_back(m.m01 / m.m00);


		// needs at least 5 points!
		cv::RotatedRect ellipse = cv::fitEllipse(contour);
		objects.major.push_back(std::max(ellipse.size.width, ellipse.size.height));
		objects.minor.push_back(std::min(ellipse.size.width, ellipse.size.height));
		objects.angle.push_back(ellipse.angle + 90.0);
											  
		objects.eccentricity.push_back(std::sqrt(1.0 - (objects.minor.back() * 
						objects.minor.back()) / (objects.major.back() * objects.major.back())));
	} catch (const std::exception& e) {
	}
}

Error detection(std::vector<Image>& imageBuffer, 
		std::unordered_map<size_t, Objects>& detectedObjects)
{

	for (Image& image: imageBuffer){
		try {
			cv::Mat thresh;
			image.detectionThreshold = cv::threshold(image.img, thresh, e_imageThreshold,
					255, cv::THRESH_BINARY);

			std::vector<std::vector<cv::Point>> contours;
			cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_NONE);

			// std::cout << "Found " << contours.size() << " objects\n";

			Objects objects;
			objects.reserver(contours.size());
			objects.id = image.id;
			for (const std::vector<cv::Point>& contour: contours) {
				double area = cv::contourArea(contour);
				if (area < e_minArea)
					continue;

				computeRegionProps(contour, objects);
			}
			objects.shrinkToFit();
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
