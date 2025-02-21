#pragma once
#include <string>

struct Settings {
    int imageWidth;
    int imageHeight;
    bool resize;
    bool invertImage;
    int nBackgroundImages;
    int stackSize;
    int stackBufferSizeMultiplier;
    int nThreads;
    std::string sourceDir;
    std::string outDir;
};

void setDefault(Settings& settings);
Settings readConfig(std::string filename);
