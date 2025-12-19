#include "parser.hpp"
#include "error.hpp"
#include <exception>
#include <fstream>
#include <iostream>
#include <sstream>
#include <unordered_map>


////////////////////////////////////////////////////////////
/// Helper macros
////////////////////////////////////////////////////////////
#define VAR_NAME(x) #x

////////////////////////////////////////////////////////////
/// Helper functions
////////////////////////////////////////////////////////////
std::unordered_map<std::string, std::string> parseConfigFile(std::string filename)
{
    std::unordered_map<std::string, std::string> settings;

    std::ifstream configFile(filename);
    if (!configFile.is_open()) {
        throw std::runtime_error(
            "Error: Unable to open the configuration file " + filename);
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

			auto pos = value.find('#');
			if (pos != std::string::npos)
				value.erase(pos);
            value.erase(0, value.find_first_not_of(" \t"));
            value.erase(value.find_last_not_of(" \t") + 1);

            settings[key] = value;
        }
    }
    configFile.close();
    return settings;
}

template <typename T>
Error convert_parameter(const std::string& value, T& parameter, std::string& type)
{
	try {
		if constexpr (std::is_same_v<T, int>) {
			parameter = std::stoi(value);
			type = "int";
		} else if constexpr (std::is_same_v<T, size_t>) {
			parameter = size_t(std::stoi(value));
			type = "size_t";
		} else if constexpr (std::is_same_v<T, double>) {
			parameter = std::stod(value);
			type = "double";
		} else if constexpr (std::is_same_v<T, bool>) {
			parameter = value == "true";
			type = "bool";
		} else if constexpr (std::is_same_v<T, std::string>) {
			parameter = value;
			type = "string";
		// } else if constexpr (std::is_same_v<T, SomeStruct>) {
		// 	parameter = SomeStructFromString(value);
		// 	type = "SomeStruct";
		} else {
			Error error = Error::ConversionError;
			error.addMessage("Unsupported type in convert_parameter");
			return error;
        }
	} catch (const std::exception& e) {
		Error error = Error::ConversionError;
		error.addMessage(std::string("Error while converting value, exception: ") + e.what());
		return error;
	}
	return Error::Success;
}

template <typename T>
void readParameter(std::unordered_map<std::string, std::string>& fileConfig, T& parameter, std::string name)
{
	name = name.erase(0, 2);
    auto foundKey = fileConfig.find(name);
    if (foundKey == fileConfig.end()) {
        throw std::runtime_error("Error: " + name + " not found in the config file.");
    }
	std::string type;
    convert_parameter<T>(fileConfig[name], parameter, type).check();
    std::cout << "Found Parameter " + name + " of type " + type +
                     " with value " + fileConfig[name]
              << std::endl;
}


////////////////////////////////////////////////////////////
/// External variables set by settings file
////////////////////////////////////////////////////////////
std::string e_sourcePath;
std::string e_savePath;

bool e_warningsAsError;
bool e_grayscaleInput;
double e_minStdDev;
double e_minMean;
size_t e_imageStackSize;
size_t e_nCores;
double e_imageThreshold;
double e_minArea;

bool e_useDeconv;
size_t e_deconvBatchSize;

bool e_saveCrops;
size_t e_chunkSize;
int e_compressionLevel;

std::string e_profileName;

////////////////////////////////////////////////////////////
/// Functions
////////////////////////////////////////////////////////////
void readParameters(char* filename)
{
    std::unordered_map<std::string, std::string> fileConfig = parseConfigFile(filename);
    std::cout << "########################################\n";

	readParameter(fileConfig, e_sourcePath, VAR_NAME(e_sourcePath));
	readParameter(fileConfig, e_savePath, VAR_NAME(e_savePath));

	readParameter(fileConfig, e_warningsAsError, VAR_NAME(e_warningsAsError));
	readParameter(fileConfig, e_grayscaleInput, VAR_NAME(e_grayscaleInput));
	readParameter(fileConfig, e_minStdDev, VAR_NAME(e_minStdDev));
	readParameter(fileConfig, e_minMean, VAR_NAME(e_minMean));
	readParameter(fileConfig, e_imageStackSize, VAR_NAME(e_imageStackSize));
	readParameter(fileConfig, e_nCores, VAR_NAME(e_nCores));
	readParameter(fileConfig, e_imageThreshold, VAR_NAME(e_imageThreshold));
	readParameter(fileConfig, e_minArea, VAR_NAME(e_minArea));
	readParameter(fileConfig, e_deconvBatchSize, VAR_NAME(e_deconvBatchSize));
	readParameter(fileConfig, e_useDeconv, VAR_NAME(e_useDeconv));
	readParameter(fileConfig, e_saveCrops, VAR_NAME(e_saveCrops));
	readParameter(fileConfig, e_chunkSize, VAR_NAME(e_chunkSize));
	readParameter(fileConfig, e_compressionLevel, VAR_NAME(e_compressionLevel));

	if (e_savePath.back() != '/')
		e_savePath += "/";

	size_t idx = e_sourcePath.find_last_of('/');
	e_profileName = e_sourcePath.substr(idx + 1, e_sourcePath.size());
	std::cout << "Profile name: " << e_profileName << std::endl;

    std::cout << "########################################\n";
}

void defaultParams()
{
}
