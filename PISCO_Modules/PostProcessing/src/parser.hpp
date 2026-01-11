#pragma once
#include "error.hpp"
#include <string>


////////////////////////////////////////////////////////////
/// External variables set by settings file
////////////////////////////////////////////////////////////
extern std::string e_sourceFile;
extern std::string e_savePath;

extern bool e_grayscaleInput;
extern size_t e_imageStackSize;
extern size_t e_nCores;
extern double e_imageThreshold;

extern bool e_useDeconv;
extern size_t e_deconvBatchSize;

extern bool e_saveCrops;
extern size_t e_chunkSize;
extern int e_compressionLevel;


////////////////////////////////////////////////////////////
/// Global variables set by program:
////////////////////////////////////////////////////////////
extern double e_minStdDev;
extern double e_minMean;
extern double e_minArea;

extern std::string e_dateTime;
extern std::string e_profileName;
extern std::string e_imageSourcePath;

////////////////////////////////////////////////////////////
/// Functions:
////////////////////////////////////////////////////////////
void readParameters(char *filename);
void defaultParams();
