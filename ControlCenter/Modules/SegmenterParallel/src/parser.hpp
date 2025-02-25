#pragma once
#include <string>

extern std::string sourcePath;
extern std::string savePath;
extern bool enablePrinting;
extern int stackSize;
extern int numBufferedStacks;
extern int numThreads;

extern int bufferSize;

void readParameters(int argc, char* argv[], std::string inputFile);
