#include "parser.hpp"
#include "segmenter.hpp"

int main(int argc, char** argv)
{
    readParameters(argc, argv, "input.ini");
    runSegmenter();
    return 0;
}
