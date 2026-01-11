#include "deconvolution.hpp"
#include "parser.hpp"
#include "types.hpp"
#include <ios>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

torch::Device getDevice()
{
    if (torch::cuda::is_available()) {
        std::cout << "Found CUDA\n";
        return torch::Device(torch::kCUDA);
    } else {
        std::cout << "Could not find CUDA, fall back to CPU\n";
        return torch::Device(torch::kCPU);
    }
}

torch::jit::script::Module loadModel(const torch::Device& device)
{
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

void convertResult(torch::Tensor& output, std::vector<cv::Mat>& imageBuffer,
    size_t startIdx, size_t batchSize)
{
    for (size_t i = 0; i < batchSize; i++) {
        torch::Tensor res = output[i]
                                .squeeze()
                                .clamp(0., 1.)
                                .mul(255.0)
                                .to(torch::kU8)
                                .cpu()
                                .contiguous();

        imageBuffer[startIdx + i] =
            cv::Mat(res.size(0), res.size(1), CV_8UC1, res.data_ptr<uint8_t>()).clone();
    }
}

Error runDeconvolution(std::vector<cv::Mat>& imageBuffer, DeconvolutionModel& model)
{
	try {
		std::cout << "Running deconvolution on " << imageBuffer.size() << " images\n";
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






void deconvolutionWorker(ThreadSafeQueue<CropStack>& deconvQueue,
    ThreadSafeQueue<CropStack>& writerQueue)
{
    DeconvolutionModel model;
    model.init();

	std::vector<cv::Mat> deconvolutionBatchImages;
	std::vector<std::unordered_map<size_t, std::vector<cv::Rect>>> deconvolutionBatchTiles;
	std::vector<cv::Mat> stackImageBuffer;
	std::vector<std::unordered_map<size_t, std::vector<cv::Rect>>> stackTileBuffer;

	while (true) {
		auto ret = deconvQueue.pop_for(1s);
		if (!ret) {
			if (deconvQueue.stop_requested()) {
				std::cout << "Abort detected\n";
				break;
			}
			else if (deconvQueue.closed()) {

				if (!stackImageBuffer.empty()) {
					deconvolutionBatchImages = std::vector(stackImageBuffer.begin(),
							stackImageBuffer.begin() + stackImageBuffer.size());
					deconvolutionBatchTiles = std::vector(stackTileBuffer.begin(),
							stackTileBuffer.begin() + stackImageBuffer.size());

					runDeconvolution(deconvolutionBatchImages, model).check();

					CropStack deconvStack;
					deconvStack.tileMap = deconvolutionBatchTiles;
					deconvStack.stackImages = deconvolutionBatchImages;
					writerQueue.push_for(deconvStack, 1s);
				}

				writerQueue.close();

				std::cout << "Queue drained\n";
				break;
			} else {
				std::cout << "Queue timed out\n";
				writerQueue.request_stop();
				deconvQueue.request_stop();
				break;
			}
		}

		CropStack stack = *ret;
		for (size_t stackIdx = 0; stackIdx < stack.stackImages.size(); stackIdx++) {
			stackImageBuffer.push_back(stack.stackImages[stackIdx]);
			stackTileBuffer.push_back(stack.tileMap[stackIdx]);
		}

		if (stackImageBuffer.size() >= e_deconvBatchSize) {
			deconvolutionBatchImages = std::vector(stackImageBuffer.begin(),
					stackImageBuffer.begin() + e_deconvBatchSize);
			deconvolutionBatchTiles = std::vector(stackTileBuffer.begin(),
					stackTileBuffer.begin() + e_deconvBatchSize);

			runDeconvolution(deconvolutionBatchImages, model).check();

			CropStack deconvStack;
			deconvStack.tileMap = deconvolutionBatchTiles;
			deconvStack.stackImages = deconvolutionBatchImages;
			writerQueue.push_for(deconvStack, 1s);

			deconvolutionBatchImages.clear();
			deconvolutionBatchTiles.clear();
			stackImageBuffer.erase(stackImageBuffer.begin(),
					stackImageBuffer.begin() + e_deconvBatchSize);
			stackTileBuffer.erase(stackTileBuffer.begin(),
					stackTileBuffer.begin() + e_deconvBatchSize);
		}
	}
}
