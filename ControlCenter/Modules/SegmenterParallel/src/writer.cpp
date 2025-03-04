#include "writer.hpp"
#include "utils.hpp"
#include <fstream>
#include <iostream>
#include <sstream>

std::string splitLast(const std::string& str, char c)
{
    std::stringstream stream(str);
    std::string segment;
    std::vector<std::string> seglist;
    while (std::getline(stream, segment, c)) {
        seglist.push_back(segment);
    }
    return seglist.back();
}

std::string splitAllBeforeLast(const std::string& str, char c)
{
    std::stringstream stream(str);
    std::string segment;
    std::vector<std::string> seglist;
    while (std::getline(stream, segment, c)) {
        seglist.push_back(segment);
    }
    std::string res = "";
    for (size_t i = 0; i < seglist.size() - 1; i++) {
        res += seglist[i] + ".";
    }
    return res.substr(0, res.size() - 1);
}

Info initWriter()
{
    try {
        objectSaveFile.open(objectSaveFilePath);
        objectSaveFile << "ID, Image filename, x, y, width, height, contour area";
        if (saveContours)
            objectSaveFile << ", contour";
        objectSaveFile << "\n";

        return Success;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

Info initWriter(std::string fileName)
{
    try {
        objectSaveFile.open(objectSaveFilePath + fileName);
        objectSaveFile << "ID, Image filename, x, y, width, height, contour area";
        if (saveContours)
            objectSaveFile << ", contour";
        objectSaveFile << "\n";

        return Success;
    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}

Info writeSegmenterObject(const SegmenterObject& object, const std::vector<std::string>& files, bool newSaveFile)
{
    try {
        std::string filename = splitLast(files[object.fileIdx], '/');
        switch (saveMode) {
            ///////////////////////////////////////////////////////////////////
        case oneFile: // write all objects in one file. Nothing to do here
            break;
            ///////////////////////////////////////////////////////////////////
        case oneFilePerImage: // write all objects from one image to one file
            if (newSaveFile) {
                objectSaveFile.close();
                checkInfo(initWriter(splitAllBeforeLast(filename, '.') + ".dat"));
            }
            break;
            ///////////////////////////////////////////////////////////////////
        case oneFilePerObject: // write all objects in one file each
            objectSaveFile.close();
            checkInfo(initWriter(splitAllBeforeLast(filename, '.') + "_" + std::to_string(object.id) + ".dat"));
            break;
            ///////////////////////////////////////////////////////////////////
        default:
            return WriterErrorInvalidSaveMode;
        }

        // write object data:
        objectSaveFile << object.id << "," << filename << "," << object.boundingRect.x << "," << object.boundingRect.y << "," << object.boundingRect.width << "," << object.boundingRect.height << "," << object.area;
        if (saveContours) {
            objectSaveFile << ",{";
            for (size_t i = 0; i < object.contour.size() - 1; i++) {
                objectSaveFile << object.contour[i].x << ";" << object.contour[i].y << "|";
            }
            objectSaveFile << object.contour[object.contour.size() - 1].x << ";" << object.contour[object.contour.size() - 1].y << "}";
        }
        objectSaveFile << "\n";

    } catch (std::exception& e) {
        std::cout << "Exception: " << e.what() << std::endl;
        return RuntimeError;
    }
    return Unknown;
}
