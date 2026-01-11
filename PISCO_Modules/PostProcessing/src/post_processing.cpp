#include "post_processing.hpp"
#include "deconvolution.hpp"
#include "parser.hpp"
#include "reader.hpp"
#include "types.hpp"
#include <H5Cpp.h>
#include <H5File.h>
#include <H5Group.h>
#include <iostream>


void runPostProcessing()
{
	// load hdf5 file:
	H5::H5File file_s;
	openHDFFile(file_s).check();
	readAttributes(file_s).check();

	// determine number of images and make crop groups (parallel):
	H5::Group root = file_s.openGroup("/");
	std::vector<std::string> images = getImagePathsFromHDF(root);
	std::cout << "Found " << images.size() << " images in HDF file.\n";
	file_s.close();
	
	// run deconvolution on group images:
	size_t imageStackSize = 10;
	int numStacks = images.size() / imageStackSize + 1 * (images.size() % imageStackSize > 0);
#pragma omp parallel for
	for (int stack = 0; stack < numStacks; stack++) {
		try {
			H5::H5File file(e_sourceFile, H5F_ACC_RDONLY);
		} catch (const H5::FileIException& e) {
			std::cout << "Error loading HDF file'" + e_sourceFile + "'. Error: \n" + e.getDetailMsg() << std::endl;
		}
	}
		// H5::Group root = file.openGroup("/");
//
		// size_t startIdx = stack * imageStackSize;
		// size_t stopIdx = startIdx + imageStackSize;
		// if (stopIdx >= images.size()) stopIdx = images.size();

		// std::vector<std::string> imageStack(images.begin() + startIdx, images.begin() + stopIdx);
		// std::cout << "Image stack has size " << imageStack.size() << std::endl;
		// std::cout << "Stack: " << startIdx << "-" << stopIdx << std::endl;
		//
		// std::unordered_map<size_t, std::vector<Crop>> tiles;
		// for (size_t i = startIdx; i < stopIdx; i++) {
		// 	std::vector<Crop> cropStack;
		// 	H5::Group imageGroup = root.openGroup(images[i]);
			// getAllCropsFromImage(imageGroup, cropStack);
			// tiles.insert(i, cropStack);
		// }
		// std::vector<cv::Mat> cropGroupImages;
		// groupCrops(cropGroupImages, tiles);
//
		// file.close();
	// }

	// for each crop bbox: compute contour, add to list (parallel):
	// ...

	// update crop data in hdf file (write new hdf file?):
	// ...
	
	file_s.close();
}
