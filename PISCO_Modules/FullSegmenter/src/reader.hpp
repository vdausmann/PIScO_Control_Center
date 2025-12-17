#pragma once
#include <vector>
#include <string>
#include "types.hpp"
#include "error.hpp"

Error getFiles(std::vector<std::string>& files);
Error getNextImages(std::vector<Image>& imageBuffer, const std::vector<std::string>& files,
		size_t& nextImageIndex);
