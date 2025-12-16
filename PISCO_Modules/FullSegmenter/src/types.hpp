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


struct Objects {
	size_t id;	// source image id

	std::vector<double> width;			// bbox width
	std::vector<double> height;			// bbox height
	std::vector<double> bx;				// bbox x top left
	std::vector<double> by;				// bbox y top left
	std::vector<double> circ;			// circularity
	std::vector<double> area_exc;		// area excluding holes 
	std::vector<double> area_rprops;		// area
	std::vector<double> area_percentage;	// 1 - area_exc / area_rprops
	std::vector<double> major;			// major axis of ellipse
	std::vector<double> minor;			// minor axis of ellipse
	std::vector<double> centroidy;		// y position of center of gravity
	std::vector<double> centroidx;		// x position of center of gravity
	std::vector<double> convexArea;		// area of smallest polygon
	std::vector<double> minIntensity;	// min gray value in object
	std::vector<double> maxIntensity;	// max gray value in object
	std::vector<double> meanIntensity;	// average gray value in object
	std::vector<double> intden;			// integrated density: area_rprops * meanIntensity
	std::vector<double> perimeter;		// length of outside boundary
	std::vector<double> elongation;		// major / minor
	std::vector<double> range;			// maxIntensity - minIntensity
	std::vector<double> perimAreaXC;		// perimeter / area_exc
	std::vector<double> perimMajor;		// perimeter / major
	std::vector<double> circex;		// (4 * pi * area_exc) / perimeter^2
	std::vector<double> angle;			// angle between x axis and major
	std::vector<double> boundingBoxArea;	
	std::vector<double> eccentricity;	
	std::vector<double> equivalentDiameter;
	std::vector<double> eulerNumber;
	std::vector<double> extent;
	std::vector<double> local_centroid_col;
	std::vector<double> local_centroid_row;
	std::vector<double> solidity;


	void reserver(size_t sizeEstimate) {
		width.reserve(sizeEstimate);
		height.reserve(sizeEstimate);
		bx.reserve(sizeEstimate);
		by.reserve(sizeEstimate);
		circ.reserve(sizeEstimate);
		area_exc.reserve(sizeEstimate);
		area_rprops.reserve(sizeEstimate);
		area_percentage.reserve(sizeEstimate);
		major.reserve(sizeEstimate);
		minor.reserve(sizeEstimate);
		centroidy.reserve(sizeEstimate);
		centroidx.reserve(sizeEstimate);
		convexArea.reserve(sizeEstimate);
		minIntensity.reserve(sizeEstimate);
		maxIntensity.reserve(sizeEstimate);
		meanIntensity.reserve(sizeEstimate);
		intden.reserve(sizeEstimate);
		perimeter.reserve(sizeEstimate);
		elongation.reserve(sizeEstimate);
		range.reserve(sizeEstimate);
		perimAreaXC.reserve(sizeEstimate);
		perimMajor.reserve(sizeEstimate);
		circex.reserve(sizeEstimate);
		angle.reserve(sizeEstimate);
		boundingBoxArea.reserve(sizeEstimate);
		eccentricity.reserve(sizeEstimate);
		equivalentDiameter.reserve(sizeEstimate);
		eulerNumber.reserve(sizeEstimate);
		extent.reserve(sizeEstimate);
		local_centroid_col.reserve(sizeEstimate);
		local_centroid_row.reserve(sizeEstimate);
		solidity.reserve(sizeEstimate);
	}

	void shrinkToFit()
	{
		width.shrink_to_fit();
		height.shrink_to_fit();
		bx.shrink_to_fit();
		by.shrink_to_fit();
		circ.shrink_to_fit();
		area_exc.shrink_to_fit();
		area_rprops.shrink_to_fit();
		area_percentage.shrink_to_fit();
		major.shrink_to_fit();
		minor.shrink_to_fit();
		centroidy.shrink_to_fit();
		centroidx.shrink_to_fit();
		convexArea.shrink_to_fit();
		minIntensity.shrink_to_fit();
		maxIntensity.shrink_to_fit();
		meanIntensity.shrink_to_fit();
		intden.shrink_to_fit();
		perimeter.shrink_to_fit();
		elongation.shrink_to_fit();
		range.shrink_to_fit();
		perimAreaXC.shrink_to_fit();
		perimMajor.shrink_to_fit();
		circex.shrink_to_fit();
		angle.shrink_to_fit();
		boundingBoxArea.shrink_to_fit();
		eccentricity.shrink_to_fit();
		equivalentDiameter.shrink_to_fit();
		eulerNumber.shrink_to_fit();
		extent.shrink_to_fit();
		local_centroid_col.shrink_to_fit();
		local_centroid_row.shrink_to_fit();
		solidity.shrink_to_fit();
	}
};

struct SegmenterObject {
	size_t id;	// source image id
	std::vector<cv::Point> contour;	// contour of object
	cv::Rect boundingBox;
	double area;


	double width;			// bbox width
	double height;			// bbox height
	double bx;				// bbox x top left
	double by;				// bbox y top left
	double circ;			// circularity
	double area_exc;		// area excluding holes 
	double area_rprops;		// area
	double area_percentage;	// 1 - area_exc / area_rprops
	double major;			// major axis of ellipse
	double minor;			// minor axis of ellipse
	double centroidy;		// y position of center of gravity
	double centroidx;		// x position of center of gravity
	double convexArea;		// area of smallest polygon
	double minIntensity;	// min gray value in object
	double maxIntensity;	// max gray value in object
	double meanIntensity;	// average gray value in object
	double intden;			// integrated density: area_rprops * meanIntensity
	double perimeter;		// length of outside boundary
	double elongation;		// major / minor
	double range;			// maxIntensity - minIntensity
	double perimAreaXC;		// perimeter / area_exc
	double perimMajor;		// perimeter / major
	double circex;		// (4 * pi * area_exc) / perimeter^2
	double angle;			// angle between x axis and major
	double boundingBoxArea;	
	double eccentricity;	
	double equivalentDiameter;
	double eulerNumber;
	double extent;
	double local_centroid_col;
	double local_centroid_row;
	double solidity;
};
