#include "utils.hpp"
#include <background_correction.hpp>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

//////////////////////////////////////////////////////////////
// External variables:
//////////////////////////////////////////////////////////////
// Paths:
std::string sourcePath;
std::string savePath;

// ThreadManager settings:
Index stackSize;
Index numBufferedStacks;
Index numSegmenterThreads;
Index numReaderThreads;

// Image manipulation settings:
Index imageWidth;
Index imageHeight;
bool resizeToImageWidthHeight;
bool invertImages;
std::string backgroundCorrectionModelStr;
Index numBackgroundImages;

// Segmenter settings:
double minObjectArea;
bool saveContours;
SaveMode saveMode;
bool saveBackgroundCorrectedImages;
bool saveCrops;

// Other:
Index progressBarWidth;
bool enableDetailedPrinting;

// Helper:
std::function<void(const std::vector<cv::Mat>&, cv::Mat&, int, int)> backgroundCorrectionModel;
Index bufferSize;
std::string saveModeStr;
std::string objectSaveFilePath;
std::ofstream objectSaveFile;
//////////////////////////////////////////////////////////////

void print(std::string str, bool newLine, bool ignoreDetailedPrinting)
{
    if (ignoreDetailedPrinting || enableDetailedPrinting) {
        std::cout << str;
        if (newLine) {
            std::cout << std::endl;
        }
    }
}

void error(std::string errorMessage)
{
    throw std::runtime_error(makeRed("Error: " + errorMessage));
}

void warning(std::string warningMessage)
{
    std::cout << makeYellow("Warning: " + warningMessage) << std::endl;
}

void progressBar(Index fileIdx, Index filesSize)
{
    if (progressBarWidth > 0) {
        double progress = double(fileIdx) / filesSize;
        Index pos = Index(std::round(progress * progressBarWidth));
        std::cout << "[\033[34m";
        for (Index i = 0; i < progressBarWidth; i++) {
            if (i < pos)
                std::cout << "#";
            else if (i == pos)
                std::cout << ">\033[0m\033[90m";
            else
                std::cout << "#";
        }
        std::cout << "\033[0m] " << int(progress * 100) << "%\r";
        std::cout.flush();
        if (progress == 1)
            std::cout << std::endl;
    }
}

std::string customInfo(Info errorCode)
{
    const std::unordered_map<Info, std::string> errorMap {
        { EmptyImage, "Empty image" },
        { UnreadableImageFile, "Unreadable image file" },
        { CVRuntime, "OpenCV runtime error" },
        { WriterErrorInvalidSaveMode, "Writer error: invalid save mode" },
        { ReaderFinished, "Reader finished with files" },
    };
    try {
        return errorMap.at(errorCode);
    } catch (const std::out_of_range& e) {
        return info(errorCode);
    }
}

std::unordered_map<std::string, std::string> parseConfigFile(std::string filename)
{
    std::unordered_map<std::string, std::string> settings;

    std::ifstream configFile(filename);
    if (!configFile.is_open()) {
        throw std::runtime_error("Error: Unable to open the configuration file " + filename);
    }

    std::string line, subStr;
    while (std::getline(configFile, line)) {
        subStr = line.substr(0, 2);
        if (subStr == "//" || subStr == "#") {
            continue;
        }
        std::istringstream iss(line);
        std::string key, value;
        if (std::getline(iss, key, '=') && std::getline(iss, value)) {
            // Trim leading and trailing whitespaces from key and value
            key.erase(0, key.find_first_not_of(" \t"));
            key.erase(key.find_last_not_of(" \t") + 1);
            value.erase(0, value.find_first_not_of(" \t"));
            value.erase(value.find_last_not_of(" \t") + 1);

            settings[key] = value;
        }
    }
    configFile.close();
    return settings;
}

void printHelp()
{
    std::cout << "Help" << std::endl;
}

// Function to parse command-line arguments
std::unordered_map<std::string, std::string> parseCommandLineArgs(int argc, char* argv[])
{
    std::unordered_map<std::string, std::string> params;
    std::string key;
    std::string str;
    // find config file path as first argument
    if (argc < 2) {
        // throw std::runtime_error("Error: Input file not found. Specify as first argument, i.e. ./SegmenterParallel <input_file_path>");
        params["config"] = "input.ini";
    } else {
        params["config"] = std::string(argv[1]);
    }

    for (int i = 2; i < argc; i++) {
        str = argv[i];
        if (str.rfind("--", 0) == 0) { // found key
            key = str.substr(2);

            // this key is without value
            if (i + 1 < argc && std::string(argv[i + 1]).rfind("--", 0) == 0) {
                if (key == "help")
                    printHelp();
            }
        } else { // found value
            params[key] = str;
        }
    }
    return params;
}

void readParameterIndex(std::unordered_map<std::string, std::string>& fileConfig, std::unordered_map<std::string, std::string>& commandLineConfig, Index& parameter, std::string name)
{
    auto foundKey = commandLineConfig.find(name);
    if (foundKey == commandLineConfig.end()) {
        foundKey = fileConfig.find(name);
        if (foundKey == fileConfig.end()) {
            throw std::runtime_error(makeRed("Error: " + name + " not found in the config file."));
        }
        parameter = std::stoi(fileConfig[name]);
    } else {
        parameter = std::stoi(commandLineConfig[name]);
    }
    print("Found Parameter " + name + " of type int with value " + std::to_string(parameter), true, true);
}

void readParameterDouble(std::unordered_map<std::string, std::string>& fileConfig, std::unordered_map<std::string, std::string>& commandLineConfig, double& parameter, std::string name)
{
    auto foundKey = commandLineConfig.find(name);
    if (foundKey == commandLineConfig.end()) {
        foundKey = fileConfig.find(name);
        if (foundKey == fileConfig.end()) {
            throw std::runtime_error(makeRed("Error: " + name + " not found in the config file."));
        }
        parameter = std::stod(fileConfig[name]);
    } else {
        parameter = std::stod(commandLineConfig[name]);
    }
    print("Found Parameter " + name + " of type double with value " + std::to_string(parameter), true, true);
}

void readParameterBool(std::unordered_map<std::string, std::string>& fileConfig, std::unordered_map<std::string, std::string>& commandLineConfig, bool& parameter, std::string name)
{
    auto foundKey = commandLineConfig.find(name);
    std::string value;
    if (foundKey == commandLineConfig.end()) {
        foundKey = fileConfig.find(name);
        if (foundKey == fileConfig.end()) {
            throw std::runtime_error(makeRed("Error: " + name + " not found in the config file."));
        }
        value = fileConfig[name];
    } else {
        value = commandLineConfig[name];
    }
    std::transform(value.begin(), value.end(), value.begin(),
        [](unsigned char c) { return std::tolower(c); });
    if (value == "true")
        parameter = true;
    else if (value == "false")
        parameter = false;
    else
        throw std::runtime_error(makeRed("Error: Invalid value for " + name));
    print("Found Parameter " + name + " of type bool with value " + std::to_string(parameter), true, true);
}

void readParameterString(std::unordered_map<std::string, std::string>& fileConfig, std::unordered_map<std::string, std::string>& commandLineConfig, std::string& parameter, std::string name)
{
    auto foundKey = commandLineConfig.find(name);
    if (foundKey == commandLineConfig.end()) {
        foundKey = fileConfig.find(name);
        if (foundKey == fileConfig.end()) {
            throw std::runtime_error(makeRed("Error: " + name + " not found in the config file."));
        }
        parameter = fileConfig[name];
    } else {
        parameter = commandLineConfig[name];
    }
    print("Found Parameter " + name + " of type string with value " + parameter, true, true);
}

void readParameters(int argc, char* argv[])
{
    // read parameters from command line and input file
    std::unordered_map<std::string, std::string> commandLineConfig = parseCommandLineArgs(argc, argv);
    std::unordered_map<std::string, std::string> fileConfig = parseConfigFile(commandLineConfig["config"]);

    print("--------------------------------------------------------------------", true, true);
    readParameterBool(fileConfig, commandLineConfig, enableDetailedPrinting, "enableDetailedPrinting");
    readParameterString(fileConfig, commandLineConfig, sourcePath, "sourcePath");
    readParameterString(fileConfig, commandLineConfig, savePath, "savePath");
    readParameterIndex(fileConfig, commandLineConfig, stackSize, "stackSize");
    readParameterIndex(fileConfig, commandLineConfig, numBufferedStacks, "numBufferedStacks");
    readParameterIndex(fileConfig, commandLineConfig, numSegmenterThreads, "numSegmenterThreads");
    readParameterIndex(fileConfig, commandLineConfig, numReaderThreads, "numReaderThreads");
    readParameterIndex(fileConfig, commandLineConfig, imageWidth, "imageWidth");
    readParameterIndex(fileConfig, commandLineConfig, imageHeight, "imageHeight");
    readParameterBool(fileConfig, commandLineConfig, resizeToImageWidthHeight, "resizeToImageWidthHeight");
    readParameterBool(fileConfig, commandLineConfig, invertImages, "invertImages");
    readParameterString(fileConfig, commandLineConfig, backgroundCorrectionModelStr, "backgroundCorrectionModel");
    readParameterIndex(fileConfig, commandLineConfig, progressBarWidth, "progressBarWidth");
    readParameterDouble(fileConfig, commandLineConfig, minObjectArea, "minObjectArea");
    readParameterBool(fileConfig, commandLineConfig, saveContours, "saveContours");
    readParameterBool(fileConfig, commandLineConfig, saveBackgroundCorrectedImages, "saveBackgroundCorrectedImages");
    readParameterBool(fileConfig, commandLineConfig, saveCrops, "saveCrops");
    readParameterIndex(fileConfig, commandLineConfig, numBackgroundImages, "numBackgroundImages");

    readParameterString(fileConfig, commandLineConfig, saveModeStr, "saveMode");

    if (saveModeStr == "oneFile") {
        saveMode = oneFile;
        objectSaveFilePath = savePath + "/objects.dat";
    } else if (saveModeStr == "oneFilePerImage") {
        objectSaveFilePath = savePath + "/objects_img_";
        saveMode = oneFilePerImage;
    } else if (saveModeStr == "oneFilePerObject") {
        saveMode = oneFilePerObject;
        objectSaveFilePath = savePath + "/object_";
    } else {
        throw std::runtime_error(makeRed("Error: Invalid value for parameter saveMode: " + saveModeStr));
    }

    if (backgroundCorrectionModelStr == "minMaxMethod") {
        backgroundCorrectionModel = minMaxMethod;
    } else if (backgroundCorrectionModelStr == "minMethod") {
        backgroundCorrectionModel = minMethod;
    } else if (backgroundCorrectionModelStr == "averageMethod") {
        backgroundCorrectionModel = averageMethod;
    } else if (backgroundCorrectionModelStr == "medianMethod") {
        backgroundCorrectionModel = medianMethod;
    } else {
        throw std::runtime_error(makeRed("Error: Invalid value for parameter backgroundCorrectionModel: " + backgroundCorrectionModelStr));
    }

    // create crop directory if needed
    if (saveCrops && !std::filesystem::is_directory(savePath + "/crops"))
        std::filesystem::create_directory(savePath + "/crops");

    // check values:
    // if (numSegmenterThreads < 1)
    //     error("Invalid value for parameter numThreads: " + std::to_string(numSegmenterThreads) + ". At least two threads are needed.");
    // if (numSegmenterThreads > numBufferedStacks)
    //     warning("Number of threads is larger than number of buffered stacks. Only numBufferedStacks can run at the same time.");

    if (backgroundCorrectionModelStr == "minMaxMethod" && numBackgroundImages % 2 != 0) {
        warning("For the minMaxMethod, the number of background images needs to be even. numBackgroundImages will be set to " + std::to_string(numBackgroundImages - 1));
        numBackgroundImages--;
    }
    if (numBackgroundImages > stackSize || numBackgroundImages <= 0) {
        warning("Invalid value for parameter numBackgroundImages: " + std::to_string(numBackgroundImages) + ". This value needs to be smaller or equal to the stack size and larger than zero: " + std::to_string(stackSize) + ". numBufferedStacks will be set to stackSize.");
        numBackgroundImages = stackSize;
    }

    bufferSize = stackSize * numBufferedStacks;
    print("--------------------------------------------------------------------\n", true, true);
}
