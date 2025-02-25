#include "parser.hpp"
#include <csignal>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <unordered_map>

std::string sourcePath;
std::string savePath;
bool enablePrinting;
int stackSize;
int numBufferedStacks;
int numThreads;

int bufferSize;

void print(std::string str, bool newLine)
{
    if (enablePrinting) {
        std::cout << str;
        if (newLine) {
            std::cout << std::endl;
        }
    }
}

std::unordered_map<std::string, std::string> parseConfigFile(std::string filename)
{
    std::unordered_map<std::string, std::string> settings;

    std::ifstream configFile(filename);
    if (!configFile.is_open()) {
        throw std::runtime_error("Error: Unable to open the configuration file.");
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

void readParameterInt(std::unordered_map<std::string, std::string> config, int& parameter, std::string name)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        throw std::runtime_error("Error: " + name + " not found in the config file.");
    }
    parameter = std::stoi(config[name]);
    print("Found Parameter " + name + " of type int with value " + std::to_string(parameter), true);
}

void readParameterDouble(std::unordered_map<std::string, std::string> config, double& parameter, std::string name)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        throw std::runtime_error("Error: " + name + " not found in the config file.");
    }
    parameter = std::stod(config[name]);
    print("Found Parameter " + name + " of type double with value " + std::to_string(parameter), true);
}

void readParameterBool(std::unordered_map<std::string, std::string> config, bool& parameter, std::string name)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        throw std::runtime_error("Error: " + name + " not found in the config file.");
    }
    parameter = (config[name] == "true");
    print("Found Parameter " + name + " of type bool with value " + std::to_string(parameter), true);
}

void readParameterString(std::unordered_map<std::string, std::string> config, std::string& parameter, std::string name)
{
    auto foundKey = config.find(name);
    if (foundKey == config.end()) {
        throw std::runtime_error("Error: " + name + " not found in the config file.");
    }
    parameter = config[name];
    print("Found Parameter " + name + " of type string with value " + parameter, true);
}

void readParameters(int argc, char* argv[], std::string inputFilePath)
{
    std::unordered_map<std::string, std::string> config = parseConfigFile(inputFilePath);

    std::cout << "----------------------------\n";
    readParameterBool(config, enablePrinting, "enablePrinting");
    readParameterString(config, sourcePath, "sourcePath");
    readParameterString(config, savePath, "savePath");
    readParameterInt(config, stackSize, "stackSize");
    readParameterInt(config, numBufferedStacks, "numBufferedStacks");
    readParameterInt(config, numThreads, "numThreads");

    bufferSize = stackSize * numBufferedStacks;
    std::cout << "----------------------------\n\n";
}
