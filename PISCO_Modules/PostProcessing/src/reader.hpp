#pragma once
#include "types.hpp"
#include <queue>
#include <mutex>


void readWorker(ThreadSafeQueue<CropStack>& deconvQueue);

