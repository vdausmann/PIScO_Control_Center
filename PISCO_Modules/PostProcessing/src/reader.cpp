#include "reader.hpp"
#include "error.hpp"
#include "parser.hpp"
#include "types.hpp"
#include <H5Cpp.h>
#include <H5DataSet.h>
#include <H5DataSpace.h>
#include <H5Exception.h>
#include <H5File.h>
#include <H5Gpublic.h>
#include <H5PredType.h>
#include <cstring>
#include <exception>
#include <iostream>
#include <opencv2/core.hpp>
#include <unordered_map>


Error openFile(H5::H5File& file)
{
	try {
		file.openFile(e_sourceFile, H5F_ACC_RDONLY);
		std::cout << "Successfully opened HDF file '" << e_sourceFile << "'.\n";
		return Error::Success;
    } catch (H5::FileIException& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while opening HDF file '" + e_sourceFile + "': " + e.getDetailMsg());
        return error;
    }
}

Error openGroup(const H5::H5Object& root, H5::Group& group, const std::string& path)
{
	try {
		group = root.openGroup(path);
		return Error::Success;
    } catch (H5::GroupIException& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while opening group at path '" + path + "': " + e.getDetailMsg());
        return error;
    }
}

template<typename T>
Error getData(const H5::H5Object& root, const std::string& path, std::vector<T>& dst, H5::DataType type)
{
	try {
		H5::DataSet dataset = root.openDataSet(path);
		H5::DataSpace dataspace = dataset.getSpace();

		// Get size of 1D dataset
		hsize_t dims[1];
		dataspace.getSimpleExtentDims(dims);

		size_t length = dims[0];
		dst.resize(length);

		dataset.read(dst.data(), type);
		return Error::Success;
	} catch (H5::Exception& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while reading data from path '" + path + "': " + e.getDetailMsg());
        return error;
	}
}


Error getCropImage(size_t& offset, size_t idx, const std::vector<int>& width, 
		const std::vector<int>& height, const std::vector<uint8_t>& pixelValues,
		cv::Mat& dst)
{
	try {
		size_t numPixels = width[idx] * height[idx];
		dst = cv::Mat(height[idx], width[idx], CV_8UC1);
		std::memcpy(dst.data, pixelValues.data() + offset, numPixels);
		offset += numPixels;
	} catch (std::exception& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while converting 1D crop data to 2D image: " +
				std::string(e.what()));
        return error;
	}

	return Error::Success;
}



void groupCrops(const std::unordered_map<size_t, std::vector<cv::Mat>>& cropMap,
		CropStack& stack) 
{
	size_t h = 2560;
	size_t w = 2560;
	cv::Mat emptyImage = cv::Mat::zeros(h, w, CV_8U);
	cv::Mat cropGroup = emptyImage.clone();
	std::unordered_map<size_t, std::vector<cv::Rect>> tileMap;

	size_t padding = 20;
	size_t currentRow = padding;
	size_t currentCol = padding;
	size_t rowSize = 0;
	for (const auto& [imageIdx, crops]: cropMap) {
		tileMap[imageIdx].reserve(crops.size());

		for (const cv::Mat& crop: crops) {

			// wrap column
			if (currentCol + crop.cols + padding >= w) {
				currentCol = padding;
				currentRow += rowSize + padding;
				rowSize = 0;
			}

			// new image
			if (currentRow + crop.rows + padding >= h) {
				cv::bitwise_not(cropGroup, cropGroup);
				stack.stackImages.push_back(cropGroup);
				stack.tileMap.push_back(tileMap);

				cropGroup = emptyImage.clone();
				tileMap.clear();

				// make new image
				currentRow = padding;
				currentCol = padding;
				rowSize = 0;
			}

			cv::Rect region(currentCol, currentRow, crop.cols, crop.rows);
			crop.copyTo(cropGroup(region));

			tileMap[imageIdx].push_back(region);

			currentCol += crop.cols + padding;
			if (crop.rows > rowSize) rowSize = crop.rows;
		}
	}

	if (!cropGroup.empty()) {
		cv::bitwise_not(cropGroup, cropGroup);
		stack.stackImages.push_back(cropGroup);
		stack.tileMap.push_back(tileMap);
	}

	std::cout << "Compressed " << cropMap.size() << " full images to " << 
		stack.stackImages.size() << " crop images\n";
}



void readWorker(ThreadSafeQueue<CropStack>& deconvQueue)
{
	// open HDF source file:
	H5::H5File file;
	openFile(file).check();
	H5::Group root;
	openGroup(file, root, "/").check();
	
	// get image names from HDF file:
	hsize_t numImages = root.getNumObjs();
	std::vector<std::string> imagePaths;
	imagePaths.reserve(numImages);
	for (hsize_t imageIdx = 0; imageIdx < numImages; imageIdx++) {
		std::string imageName = root.getObjnameByIdx(imageIdx);
		H5G_obj_t type = root.getObjTypeByIdx(imageIdx);

		if (type == H5G_GROUP)
			imagePaths.push_back(imageName);
	}

	// generate crop stack:
	size_t numStacks = numImages / e_imageStackSize + (numImages % e_imageStackSize > 0);
	for (size_t imageStackIdx = 0; imageStackIdx < numStacks; imageStackIdx++) {
		size_t startIdx = imageStackIdx * e_imageStackSize;
		size_t stopIdx = std::min(startIdx + e_imageStackSize, numImages);

		std::vector<int> width, height;
		std::vector<uint8_t> pixelValues;
		std::unordered_map<size_t, std::vector<cv::Mat>> cropMap;
		for (size_t imageIdx = startIdx; imageIdx < stopIdx; imageIdx++) {
			H5::Group imageGroup;
			openGroup(root, imageGroup, imagePaths[imageIdx]).check();

			getData(imageGroup, "width", width, H5::PredType::NATIVE_INT).check();
			getData(imageGroup, "height", height, H5::PredType::NATIVE_INT).check();
			getData(imageGroup, "1D_crop_data", pixelValues, H5::PredType::NATIVE_UINT8).check();


			std::vector<cv::Mat> crops;
			crops.resize(width.size());
			size_t offset = 0;
			for (size_t cropIdx = 0; cropIdx < width.size(); cropIdx++) {
				cv::Mat crop;
				getCropImage(offset, cropIdx, width, height, pixelValues, 
						crops[cropIdx]).check();
			}
			cropMap[imageIdx] = crops;
		}

		// group crops to images:
		CropStack stack;
		groupCrops(cropMap, stack);

		// if space in queue, push stack to queue
		bool res = deconvQueue.push_for(stack, 5s);
		if (!res) {
			std::cout << "Timeout on waiting for queue push!\n";
			break;
		}

		std::cout << "Finished group " << startIdx << "-" << stopIdx << std::endl;
	}

	deconvQueue.close();
	file.close();
}
