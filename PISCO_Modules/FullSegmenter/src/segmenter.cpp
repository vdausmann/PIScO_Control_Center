#include "segmenter.hpp"

#include <c10/core/DeviceType.h>
#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <string>
#include <unordered_map>
#include <vector>
#include <chrono>
#include <fstream>
#include <H5Cpp.h>

#include "background_correction.hpp"
#include "deconvolution.hpp"
#include "writer.hpp"
#include "parser.hpp"
#include "detection.hpp"
#include "reader.hpp"
#include "types.hpp"


void segmentProfile()
{
	// create save files
	std::ofstream progressFile = initProgressFile();
	std::ofstream objectFile = initObjectFile();
	std::ofstream imgFile = initImageFile();


	H5::H5File file;
	initH5ProfileFile(file).check();


	std::vector<std::string> files;
	getFiles(files).check();
	std::cout << "Found " << files.size() << " files\n";

	std::vector<std::vector<std::string>> fileStacks;
	fileStacks.resize(e_nCores);
	for (size_t i = 0; i < e_nCores - 1; i++) {
		fileStacks[i] = std::vector(files.begin() + i * files.size() / e_nCores,
				files.begin() + (i + 1) * files.size() / e_nCores);
	}
	fileStacks[e_nCores - 1] = std::vector(files.begin() + (e_nCores - 1) * files.size() / e_nCores,
			files.end());


	DeconvolutionModel model;
	if (e_useDeconv) {
		model.init();
	}

	auto start = std::chrono::high_resolution_clock::now();
#pragma omp parallel for
	for (size_t i = 0; i < e_nCores; i++){
		std::vector<std::string> fileStack = fileStacks[i];
		size_t imageIndex = 0;
		std::vector<Image> imageStack;
		while (imageIndex < fileStack.size()) {
			auto start = std::chrono::high_resolution_clock::now();
			getNextImages(imageStack, fileStack, imageIndex).check();

			correctImages(imageStack).check();

			if (e_useDeconv) {
#pragma omp critical
				{
					runDeconvolution(imageStack, model).check();
				}
			}

			std::unordered_map<size_t, Objects> objects;
			std::vector<cv::Mat> cropGroupImages;
			std::unordered_map<size_t, std::vector<Crop>> tiles;

			detection(imageStack, objects).check();

<<<<<<< HEAD
			//groupCrops(objects, cropGroupImages, tiles);
=======
			// groupCrops(objects, cropGroupImages, tiles);
>>>>>>> e9e48b5ef95daacc15e6e40b0797124571002e64
// 			if (e_useDeconv) {
// #pragma omp critical
// 				{
// 					runDeconvolution(cropGroupImages, model).check();

					// for (size_t i = 0; i < cropGroupImages.size(); i++) {
					// 	cv::cvtColor(cropGroupImages[i], cropGroupImages[i], 
					// 			cv::COLOR_GRAY2BGR);
					// }
					//
					// for (const auto& [key, crops]: tiles) {
					// 	for (const Crop& crop: crops) {
					// 		cv::rectangle(cropGroupImages[crop.cropGroupImageIdx], 
					// 				crop.tile, cv::Scalar(0, 0, 255), 2);
					// 	}
					// }
					//
					// for (size_t i = 0; i < cropGroupImages.size(); i++) {
					// 	cv::imwrite("Results/temp/" + std::to_string(imageStack[0].id) +
					// 			"_" + std::to_string(i) + "_no_deconv.png", cropGroupImages[i]);
					// }
				// }
			// }

			// for (const auto& [key, crops]: tiles) {
			// 	for (const Crop& crop: crops) {
			// 		cv::rectangle(cropGroupImages[crop.cropGroupImageIdx], 
			// 				crop.tile, cv::Scalar(0, 0, 255), 2);
			// 	}
			// }


#pragma omp critical
{
			writeData(objects, imageStack, fileStack);
			// writeImageData(imageStack, imgFile);
			// writeObjectData(objects, objectFile);
			writeProgress(fileStack, imageStack, progressFile);
}

			auto end = std::chrono::high_resolution_clock::now();
			double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() / 1000.;
			std::cout << "Finished reading stack of size " << imageStack.size() << ", took " << duration << "s" << std::endl;
		}
	}
	auto end = std::chrono::high_resolution_clock::now();
	double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() / 1000.;
	std::cout << "Total time: " << duration << "s" << std::endl;
}
