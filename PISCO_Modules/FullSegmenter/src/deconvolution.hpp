#pragma once
#include <torch/script.h>
#include <torch/cuda.h>
#include <vector>

#include "types.hpp"
#include "error.hpp"

struct DeconvolutionModel {
	torch::Device device = torch::kCPU;
	torch::jit::script::Module model;
	torch::Tensor batchTensor;

	void init();
};

Error runDeconvolution(std::vector<Image>& imageBuffer, DeconvolutionModel& model);
