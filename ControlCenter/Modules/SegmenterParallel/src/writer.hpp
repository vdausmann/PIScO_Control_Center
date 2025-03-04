#pragma once
#include "utils.hpp"

Info writeSegmenterObject(const SegmenterObject& object, const std::vector<std::string>& files, bool newSaveFile);
Info initWriter();
std::string splitLast(const std::string& str, char c);
std::string splitAllBeforeLast(const std::string& str, char c);
