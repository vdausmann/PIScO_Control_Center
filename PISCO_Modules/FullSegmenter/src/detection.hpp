#pragma once
#include <unordered_map>
#include <vector>

#include "error.hpp"
#include "types.hpp"

Error detection(std::vector<Image>& imageBuffer, 
		std::unordered_map<size_t, std::vector<SegmenterObject>>& detectedObjects);
