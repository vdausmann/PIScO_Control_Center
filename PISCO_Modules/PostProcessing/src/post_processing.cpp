#include "post_processing.hpp"
#include "deconvolution.hpp"
#include "reader.hpp"
#include "writer.hpp"
#include "types.hpp"
#include <chrono>

void runPostProcessing()
{
	auto start = std::chrono::high_resolution_clock::now();
	// create worker threads:
	ThreadSafeQueue<CropStack> deconvQueue(2);
	ThreadSafeQueue<CropStack> writerQueue(2);


	std::thread readerThread(readWorker, std::ref(deconvQueue));
	std::thread deconvThread(deconvolutionWorker, std::ref(deconvQueue), std::ref(writerQueue));
	std::thread writerThread(writeWorker, std::ref(writerQueue));



	readerThread.join();
	deconvThread.join();
	writerThread.join();

	auto end = std::chrono::high_resolution_clock::now();
	double duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
	duration /= 1000.;
	std::cout << "Total running time: " << duration << "s\n";
	std::cout << "Avg. running time per image: " << duration / 109. << "s\n";
}
