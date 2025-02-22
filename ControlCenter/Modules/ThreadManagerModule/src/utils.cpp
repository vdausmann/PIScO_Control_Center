#include "utils.hpp"
#include <csignal>
#include <fstream>
#include <iostream>
#include <sstream>
#include <unordered_map>

void setDefault(Settings& settings)
{
    settings.imageWidth = 1000;
    settings.imageHeight = 1000;
    settings.resize = true;
}

std::unordered_map<std::string, std::string> parseConfigFile(std::string filename)
{
    std::unordered_map<std::string, std::string> settings;

    std::ifstream configFile(filename);
    if (!configFile.is_open()) {
        std::cerr << "Error: Unable to open the configuration file." << std::endl;
        raise errno;
    }

    std::string line;
    while (std::getline(configFile, line)) {
        if (line.substr(0, 2) == "//") {
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

void readParameterInt(std::unordered_map<std::string, std::string> config, int& parameter, std::string name, int defaultValue)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        std::cout << "Parameter " + name + " not found in the config file, using default value: " + std::to_string(defaultValue) + "." << std::endl;
        parameter = defaultValue;
    } else {
        parameter = std::stoi(config[name]);
        std::cout << "Found Parameter " + name + " of type int with value " + std::to_string(parameter) << std::endl;
    }
}

void readParameterDouble(std::unordered_map<std::string, std::string> config, double& parameter, std::string name, double defaultValue)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        std::cout << "Parameter " + name + " not found in the config file, using default value: " + std::to_string(defaultValue) + "." << std::endl;
        parameter = defaultValue;
    } else {
        parameter = std::stod(config[name]);
        std::cout << "Found Parameter " + name + " of type double with value " + std::to_string(parameter) << std::endl;
    }
}

void readParameterBool(std::unordered_map<std::string, std::string> config, bool& parameter, std::string name, bool defaultValue)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        std::cout << "Parameter " + name + " not found in the config file, using default value: " + std::to_string(defaultValue) + "." << std::endl;
        parameter = defaultValue;
    } else {
        parameter = (config[name] == "true");
        std::cout << "Found Parameter " + name + " of type bool with value " + std::to_string(parameter) << std::endl;
    }
}

void readParameterString(std::unordered_map<std::string, std::string> config, std::string& parameter, std::string name, std::string defaultValue)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        std::cout << "Parameter " + name + " not found in the config file, using default value: " + defaultValue + "." << std::endl;
        parameter = defaultValue;
    } else {
        parameter = config[name];
        std::cout << "Found Parameter " + name + " of type string with value " + parameter << std::endl;
    }
}

Settings readConfig(std::string filename)
{
    std::unordered_map<std::string, std::string> config = parseConfigFile(filename);
    Settings settings;

    readParameterInt(config, settings.imageWidth, "imageWidth", 1000);
    readParameterInt(config, settings.imageHeight, "imageHeight", 1000);
    readParameterBool(config, settings.resize, "resize", true);
    readParameterBool(config, settings.invertImage, "invertImage", true);
    readParameterInt(config, settings.nBackgroundImages, "nBackgroundImages", 5);
    readParameterInt(config, settings.stackSize, "stackSize", 10);
    readParameterInt(config, settings.stackBufferSizeMultiplier, "stackBufferSizeMultiplier", 3);
    readParameterInt(config, settings.nThreads, "nThreads", 2);
    readParameterString(config, settings.sourceDir, "sourceDir", "./");
    readParameterString(config, settings.outDir, "outDir", "./");

    return settings;
}
