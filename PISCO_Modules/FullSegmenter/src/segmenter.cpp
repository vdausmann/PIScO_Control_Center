#include "segmenter.hpp"

#include <iostream>
#include <unordered_map>
#include <vector>
#include <chrono>
#include <fstream>
#include <H5Cpp.h>

#include "background_correction.hpp"
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


	// H5::H5File file = H5::H5File(e_savePath + e_profileName + ".h5", H5F_ACC_TRUNC);
	H5::H5File file;
	initH5ProfileFile(file).check();


	std::vector<std::string> files;
	getFiles(files).check();
	std::cout << "Found " << files.size() << " files\n";

	size_t nStacks = 4;
	std::vector<std::vector<std::string>> fileStacks;
	fileStacks.resize(nStacks);
	for (size_t i = 0; i < nStacks - 1; i++) {
		fileStacks[i] = std::vector(files.begin() + i * files.size() / nStacks,
				files.begin() + (i + 1) * files.size() / nStacks);
	}
	fileStacks[nStacks - 1] = std::vector(files.begin() + (nStacks - 1) * files.size() / nStacks,
			files.end());

	auto start = std::chrono::high_resolution_clock::now();
#pragma omp parallel for
	for (size_t i = 0; i < nStacks; i++){
		std::vector<std::string> fileStack = fileStacks[i];
		size_t imageIndex = 0;
		std::vector<Image> imageStack;
		std::unordered_map<size_t, Objects> objects;
		while (imageIndex < fileStack.size()) {
			auto start = std::chrono::high_resolution_clock::now();
			getNextImages(imageStack, fileStack, imageIndex).check();

			correctImages(imageStack).check();
			detection(imageStack, objects).check();

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
