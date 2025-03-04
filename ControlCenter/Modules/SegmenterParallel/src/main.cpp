#include "segmenter.hpp"
#include "utils.hpp"
#include <iostream>

int main(int argc, char** argv)
{
#if (DEBUG)
    std::cout << "\033[31mProgram is compiled in DEBUG mode\033[0m" << std::endl;
#endif
    errorFunction = customInfo;
    readParameters(argc, argv);
    runSegmenter();
    return 0;
}
