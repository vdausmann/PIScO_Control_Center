#include "segmenter.hpp"
#include "utils.hpp"

int main(int argc, char** argv)
{
    errorFunction = customError;
    readParameters(argc, argv, "input.ini");
    runSegmenter();
    return 0;
}
