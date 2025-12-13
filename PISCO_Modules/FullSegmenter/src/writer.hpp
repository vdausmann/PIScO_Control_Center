#pragma once
#include <vector>
#include <string>
#include <fstream>
#include <H5Cpp.h>
#include <unordered_map>
#include "error.hpp"
#include "types.hpp"


Error initH5ProfileFile(H5::H5File& file);
void writeData(std::unordered_map<size_t, std::vector<SegmenterObject>>& objectData,
		const std::vector<Image>& imageStack , const H5::H5File& file, 
		const std::vector<std::string>& files);




std::ofstream initProgressFile();
std::ofstream initObjectFile();
std::ofstream initImageFile();

void writeProgress(const std::vector<std::string>& files,
		const std::vector<Image>& imageStack, std::ofstream& progressFile);

void writeObjectData(const std::unordered_map<size_t, std::vector<SegmenterObject>>& objectData,
		std::ofstream& objectFile);

void writeImageData(const std::vector<Image>& imageStack, std::ofstream& imageFile);


