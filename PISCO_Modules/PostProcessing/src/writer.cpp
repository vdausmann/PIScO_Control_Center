#include "writer.hpp"
#include "types.hpp"
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <string>

void writeWorker(ThreadSafeQueue<CropStack>& writerQueue)
{
	size_t imageIdx = 0;
	while (true) {
		auto ret = writerQueue.pop_for(5s);
		if (!ret) {
			if (writerQueue.stop_requested()) {
				std::cout << "Abort detected\n";
				break;
			}
			else if (writerQueue.closed()) {
				std::cout << "Queue drained\n";
				break;
			} else {
				std::cout << "Writer Queue timed out\n";
				break;
			}
		}

		CropStack stack = *ret;

		for (size_t stackIdx = 0; stackIdx < stack.stackImages.size(); stackIdx++) {
			cv::Mat img = stack.stackImages[stackIdx];
			cv::bitwise_not(img, img);
			for (const auto& [key, regions]: stack.tileMap[stackIdx]) {
				for (const cv::Rect& region: regions) {
					cv::threshold(img(region), img(region), 10, 255, cv::THRESH_BINARY);
				}
			}

			// cv::cvtColor(stack.stackImages[stackIdx], stack.stackImages[stackIdx], cv::COLOR_GRAY2BGR);
			// for (const auto& [key, regions]: stack.tileMap[stackIdx]) {
			// 	for (const cv::Rect& region: regions) {
			// 		cv::rectangle(stack.stackImages[stackIdx], region, 
			// 				cv::Scalar(0, 0, 255), 1);
			// 	}
			// }

			cv::imwrite("Results/" + std::to_string(imageIdx) + ".png", stack.stackImages[stackIdx]);
			std::cout << "Image written to " << "Results/" + std::to_string(imageIdx) + ".png\n";
			imageIdx++;
		}
	}
}
