#pragma once
#include <H5Cpp.h>
#include <H5File.h>
#include <vector>
#include <opencv4/opencv2/core.hpp>
#include "error.hpp"
#include "types.hpp"

Error openHDFFile(H5::H5File& file);
Error readAttributes(const H5::H5File& file);
std::vector<std::string> getImagePathsFromHDF(const H5::Group& group);
void getAllCropsFromImage(const H5::Group& group, std::vector<Crop>& crops);
