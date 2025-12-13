#include "parser.hpp"
#include "segmenter.hpp"

int main(int argc, char** argv) {
#if (DEBUG)
    std::cout << makeRed("Program is compiled in DEBUG mode") << std::endl;
#endif

	if (argc > 1) {
		readParameters(argv[1]);
	} else {
		defaultParams();
	}

	segmentProfile();
}
