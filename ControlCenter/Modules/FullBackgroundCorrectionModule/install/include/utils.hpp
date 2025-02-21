#pragma once
#include <string>

struct Settings {
    int imageWidth;
    int imageHeight;
    bool resize;
    int nBackgroundImages;
    int stackSize;
    int stackBufferSizeMultiplier;
    int nThreads;
    std::string sourceDir;
};

void setDefault(Settings& settings);
Settings readConfig(std::string filename);
