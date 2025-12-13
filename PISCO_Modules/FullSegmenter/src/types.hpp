#pragma once
#include <opencv2/core/mat.hpp>
#include <opencv2/core/types.hpp>
#include <vector>


struct Image {
	cv::Mat img;
	size_t id;	// image id

	double meanOrg = -1;
	double stddevOrg = -1;
	double meanCorrected = -1;
	double stddevCorrected = -1;
	double detectionThreshold = -1;
};


struct SegmenterObject {
	size_t id;	// source image id
	std::vector<cv::Point> contour;	// contour of object
	cv::Rect boundingBox;
	double area;


	// double width;
	// double height;
	// double bx;
	// double by;
	// double circ;
	// double area_exc;
	// double area_rprops;
	// double area_percentage;
	// double major;
	// double minor;
	// double centroidy;
	// double centroidx;
	// double convexArea;
	// double minIntensity;
	// double maxIntensity;
	// double meanIntensity;
	// double intden;
	// double perimeter;
	// double elongation;
	// double range;
	// double perimAreaXC;
	// double perimMajor;
	// double circelEx;
	// double angle;
	// double boundingBoxArea;
	// double eccentricity;
	// double equivalentDiameter;
	// double eulerNumber;
	// double extent;
	// double local_centroid_col;
	// double local_centroid_row;
	// double solidity;
};
