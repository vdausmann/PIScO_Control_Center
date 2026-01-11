#pragma once
#include <torch/script.h>
#include <torch/cuda.h>
#include <vector>

#include "types.hpp"

struct DeconvolutionModel {
	torch::Device device = torch::kCPU;
	torch::jit::script::Module model;
	torch::Tensor batchTensor;

	void init();
};

void deconvolutionWorker(ThreadSafeQueue<CropStack>& deconvQueue, 
		ThreadSafeQueue<CropStack>& writerQueue);
