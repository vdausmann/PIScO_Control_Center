#include "parser.hpp"
#include "post_processing.hpp"
#include <iostream>
#include <H5Cpp.h>

int main(int argc, char** argv) {
#if (DEBUG)
    std::cout << makeRed("Program is compiled in DEBUG mode") << std::endl;
#endif

	// HDF error handling:
	H5::Exception::dontPrint();

	if (argc > 1) {
		readParameters(argv[1]);
	} else {
		defaultParams();
	}

	runPostProcessing();
}
