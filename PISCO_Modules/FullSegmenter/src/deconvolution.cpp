#include "deconvolution.hpp"
#include "parser.hpp"
#include <c10/core/DeviceType.h>
#include <chrono>

torch::Device getDevice() {
	if (torch::cuda::is_available()) {
		std::cout << "Found CUDA\n";
		return torch::Device(torch::kCUDA);
	} else {
		std::cout << "Could not find CUDA, fall back to CPU\n";
		return torch::Device(torch::kCPU);
	}
}

torch::jit::script::Module loadModel(
    const torch::Device& device
) {
	std::string path;
	std::cout << "Loading model...\n";
	if (torch::cuda::is_available()) {
		path = "lucyd_cuda.pt";
	} else {
		path = "lucyd.pt";
	}

    torch::jit::script::Module model = torch::jit::load(path, device);
    model.to(device);
    model.eval();

	std::cout << "Finished loading model...\n";
    return model;
}

void DeconvolutionModel::init()
{
	device = getDevice();
	model = loadModel(device);
	const int H = 2560;
	const int W = 2560;
	batchTensor = torch::empty({int(e_deconvBatchSize), 1, H, W},
			torch::TensorOptions().dtype(torch::kFloat32).device(device));
}


torch::Tensor _runDeconvolution(torch::Tensor& input, torch::jit::script::Module& model)
{
	torch::NoGradGuard noGrad;
	// std::cout << "Forward pass...\n";
	auto output = model.forward({input});
	auto outTuple = output.toTuple();

	return outTuple->elements()[0].toTensor();
}

void convertResult(torch::Tensor& output, std::vector<Image>& imageBuffer, size_t startIdx,
		size_t batchSize)
{
	// std::cout << "Converting results...\n";
	for (size_t i = 0; i < batchSize; i++) {
		torch::Tensor res = output[i].squeeze().clamp(0., 1.).mul(255.0)
			.to(torch::kU8).cpu().contiguous();

		imageBuffer[startIdx + i].img = cv::Mat(res.size(0), res.size(1), CV_8UC1,
				res.data_ptr<uint8_t>()).clone();

	}
}

Error runDeconvolution(std::vector<Image>& imageBuffer, DeconvolutionModel& model)
{
	try {
		std::vector<torch::Tensor> batch;
		size_t c = 0;
		for (size_t i = 0; i < imageBuffer.size(); i++) {
			torch::Tensor t = torch::from_blob(
					imageBuffer[i].img.data, 
					{imageBuffer[i].img.rows, imageBuffer[i].img.cols} ,
					torch::kUInt8
			).to(torch::kFloat32).div_(255.0);

			model.batchTensor[c][0].copy_(t);
			c++;

			if (c >= e_deconvBatchSize) {
				torch::Tensor yHatBatch = _runDeconvolution(model.batchTensor, model.model);
				convertResult(yHatBatch, imageBuffer, i + 1 - c, c - 1);

				batch.clear();
				c = 0;
			}
		}

		if (batch.size() > 0) {
			torch::Tensor yHatBatch = _runDeconvolution(model.batchTensor, model.model);
			convertResult(yHatBatch, imageBuffer, imageBuffer.size() - c, c);

			batch.clear();
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(std::string("Error while running deconvolution: ") + e.what());
        return error;
    }

	return Error::Success;
}

