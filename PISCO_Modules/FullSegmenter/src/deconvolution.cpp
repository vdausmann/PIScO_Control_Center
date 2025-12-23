#include "deconvolution.hpp"
#include "parser.hpp"
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

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

void convertResult(torch::Tensor& output, std::vector<cv::Mat>& imageBuffer, size_t startIdx,
		size_t batchSize)
{
	for (size_t i = 0; i < batchSize; i++) {
		torch::Tensor res = output[i].squeeze().clamp(0., 1.).mul(255.0)
			.to(torch::kU8).cpu().contiguous();

		imageBuffer[startIdx + i] = cv::Mat(res.size(0), res.size(1), CV_8UC1,
				res.data_ptr<uint8_t>()).clone();

	}
}



void groupCrops(const std::unordered_map<size_t, Objects>& objectsMap,
		std::vector<cv::Mat>& cropGroupImages,
		std::unordered_map<size_t, std::vector<Crop>>& tiles) 
{
	tiles.clear();
	cropGroupImages.clear();
	size_t h = 2560;
	size_t w = 2560;
	cv::Mat emptyImage = cv::Mat::zeros(h, w, CV_8U);
	cv::Mat cropGroup = emptyImage.clone();

	size_t padding = 20;
	size_t currentRow = padding;
	size_t currentCol = padding;
	size_t rowSize = 0;
	size_t imageIdx = 0;
	for (auto const& [key, objects]: objectsMap) {
		tiles[key] = std::vector<Crop>{};
		tiles[key].reserve(objects.width.size());
		for (const cv::Mat& crop: objects.crops2D) {

			// wrap column
			if (currentCol + crop.cols + padding >= w) {
				currentCol = padding;
				currentRow += rowSize + padding;
				rowSize = 0;
			}


			// new image
			if (currentRow + crop.rows + padding >= h) {
				cv::bitwise_not(cropGroup, cropGroup);
				cropGroupImages.push_back(cropGroup);
				cropGroup = emptyImage.clone();
				imageIdx++;

				// make new image
				currentRow = padding;
				currentCol = padding;
				rowSize = 0;
			}

			cv::Rect region(currentCol, currentRow, crop.cols, crop.rows);
			crop.copyTo(cropGroup(region));

			Crop cropHelper{imageIdx, region};
			tiles[key].push_back(cropHelper);

			currentCol += crop.cols + padding;
			if (crop.rows > rowSize) rowSize = crop.rows;
		}
	}

	if (!cropGroup.empty()) {
		cv::bitwise_not(cropGroup, cropGroup);
		cropGroupImages.push_back(cropGroup);
	}

	std::cout << "Compressed " << objectsMap.size() << " full images to " << 
		cropGroupImages.size() << " crop images\n";
}




Error runDeconvolution(std::vector<Image>& imageBuffer, DeconvolutionModel& model)
{
	try {
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
				convertResult(yHatBatch, imageBuffer, i + 1 - c, c);

				c = 0;
			}
		}

		std::cout << c << std::endl;

		if (c > 0) {
			torch::Tensor yHatBatch = _runDeconvolution(model.batchTensor, model.model);
			convertResult(yHatBatch, imageBuffer, imageBuffer.size() - c, c);
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(std::string("Error while running deconvolution: ") + e.what());
        return error;
    }

	return Error::Success;
}


Error runDeconvolution(std::vector<cv::Mat>& imageBuffer, DeconvolutionModel& model)
{
	try {
		size_t c = 0;
		for (size_t i = 0; i < imageBuffer.size(); i++) {
			torch::Tensor t = torch::from_blob(
					imageBuffer[i].data, 
					{imageBuffer[i].rows, imageBuffer[i].cols} ,
					torch::kUInt8
			).to(torch::kFloat32).div_(255.0);

			model.batchTensor[c][0].copy_(t);
			c++;

			if (c >= e_deconvBatchSize) {
				torch::Tensor yHatBatch = _runDeconvolution(model.batchTensor, model.model);
				convertResult(yHatBatch, imageBuffer, i + 1 - c, c);
				c = 0;
			}
		}

		if (c > 0) {
			torch::Tensor yHatBatch = _runDeconvolution(model.batchTensor, model.model);
			convertResult(yHatBatch, imageBuffer, imageBuffer.size() - c, c);
		}
    } catch (const std::exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage(std::string("Error while running deconvolution: ") + e.what());
        return error;
    }

	return Error::Success;
}

