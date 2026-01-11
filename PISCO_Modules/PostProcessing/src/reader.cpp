#include "reader.hpp"
#include "parser.hpp"
#include <H5Attribute.h>
#include <H5DataType.h>
#include <H5Exception.h>
#include <H5Group.h>
#include <H5PredType.h>
#include <cstdint>
#include <cstring>
#include <iostream>

Error openHDFFile(H5::H5File& file)
{
    try {
        file.openFile(e_sourceFile, H5F_ACC_RDONLY);
        // std::cout << e_sourceFile << " opened successfully\n";
    } catch (const H5::FileIException& e) {
        Error error = Error::RuntimeError;
        error.addMessage(
            "Error loading HDF file'" + e_sourceFile + "'. Error: \n" + e.getDetailMsg());
        return error;
    }
    return Error::Success;
}

bool hasAttribute(const H5::H5Object& obj, const std::string& name)
{
    return H5Aexists(obj.getId(), name.c_str()) > 0;
}

bool readAttribute(const H5::H5Object& obj, const std::string& name, void* dst,
    const H5::DataType& type)
{
    try {
        H5::Exception::dontPrint();

        if (H5Aexists(obj.getId(), name.c_str()) <= 0) {
            std::cout << "Could not find attribute '" << name << "'\n";
            return false;
        }

        H5::Attribute attr = obj.openAttribute(name);
        attr.read(type, dst);
        return true;
    } catch (const H5::Exception& e) {
        std::cout << "HDF5 error while reading attribute '" << name
                  << "': " << e.getDetailMsg() << std::endl;
        return false;
    }
}

bool readStringAttribute(const H5::H5Object& obj, const std::string& name,
    std::string& out)
{
    try {
        H5::Exception::dontPrint();

        if (H5Aexists(obj.getId(), name.c_str()) <= 0)
            return false;

        H5::Attribute attr = obj.openAttribute(name);
        H5::StrType stype = attr.getStrType();

        // Variable-length string
        if (stype.isVariableStr()) {
            char* cstr = nullptr;
            attr.read(stype, &cstr);
            if (!cstr)
                return false;
            out = cstr;
            free(cstr);
            return true;
        }

        // Fixed-length string
        size_t len = stype.getSize();
        std::vector<char> buf(len + 1, 0);  // +1 for null terminator
        attr.read(stype, buf.data());
        out = std::string(buf.data());
        return true;
    } catch (...) {
        return false;
    }
}

Error readAttributes(const H5::H5File& file)
{
    try {
        H5::StrType strDataType(H5::PredType::C_S1, H5T_VARIABLE);
        strDataType.setCset(H5T_CSET_UTF8);
        // reading settings from file:
		std::cout << "------------------------------\n";
        std::cout << "Extracted the following settings from HDF file: " << std::endl;

        if (readStringAttribute(file, "Date and Time of Segmentation", e_dateTime)) {
            std::cout << "\tFound attribute dateTime=" << e_dateTime << "\n";
        }

        if (readStringAttribute(file, "Image Source Path", e_imageSourcePath)) {
            std::cout << "\tFound attribute imageSourcePath=" << e_imageSourcePath << "\n";
        }

        if (readStringAttribute(file, "Profile Name", e_profileName)) {
            std::cout << "\tFound attribute profileName=" << e_profileName << "\n";
        }

        if (readAttribute(file, "Setting: minArea", &e_minArea,
                H5::PredType::NATIVE_DOUBLE)) {
            std::cout << "\tFound attribute minArea=" << e_minArea << std::endl;
        }

        if (readAttribute(file, "Setting: minMean", &e_minMean,
                H5::PredType::NATIVE_DOUBLE)) {
            std::cout << "\tFound attribute minMean=" << e_minMean << std::endl;
        }

        if (readAttribute(file, "Setting: minStdDev", &e_minStdDev,
                H5::PredType::NATIVE_DOUBLE)) {
            std::cout << "\tFound attribute minStdDev=" << e_minStdDev << std::endl;
        }

		std::cout << "------------------------------\n";
    } catch (const H5::Exception& e) {
        Error error = Error::RuntimeError;
        error.addMessage("Error on reading settings. Error: \n" + e.getDetailMsg());
        return error;
    }
    return Error::Success;
}


std::vector<std::string> getImagePathsFromHDF(const H5::Group& group)
{
    std::vector<std::string> subgroups;
    hsize_t n = group.getNumObjs();

    for (hsize_t i = 0; i < n; i++) {
        std::string name = group.getObjnameByIdx(i);
        H5G_obj_t type = group.getObjTypeByIdx(i);

        if (type == H5G_GROUP) {
            subgroups.push_back(name);
        }
    }
    return subgroups;
}


void getCrop(size_t idx, size_t& offset, const std::vector<int>& widths,
		const std::vector<int>& heights, const std::vector<uint8_t>& crop1DData,
		cv::Mat& dst)
{
	int width = widths[idx];
	int height = heights[idx];
	size_t numPixels = width * height;

	dst = cv::Mat(height, width, CV_8UC1);
	std::memcpy(dst.data, crop1DData.data() + offset, numPixels);
		
	offset += numPixels;
}


void getAllCropsFromImage(const H5::Group& group, std::vector<Crop>& crops)
{
	H5::DataSet dataset = group.openDataSet("1D_crop_data");
	H5::DataSpace space = dataset.getSpace();
	int ndims = space.getSimpleExtentNdims();
	std::vector<hsize_t> dims(ndims);
	space.getSimpleExtentDims(dims.data());

	std::vector<uint8_t> crop1DData(dims[0]);
	dataset.read(crop1DData.data(), H5::PredType::NATIVE_UINT8);


	dataset = group.openDataSet("width");
	space = dataset.getSpace();
	ndims = space.getSimpleExtentNdims();
	space.getSimpleExtentDims(dims.data());

	std::vector<int> widths(dims[0]);
	dataset.read(widths.data(), H5::PredType::NATIVE_INT);
	dataset = group.openDataSet("height");
	std::vector<int> heights(dims[0]);
	dataset.read(heights.data(), H5::PredType::NATIVE_INT);

	crops.reserve(widths.size());

	size_t offset = 0;
	size_t idx = 0;
	while (offset < crop1DData.size()) {
		Crop crop;
		getCrop(idx, offset, widths, heights, crop1DData, crop.image);
		idx++;

		crops.push_back(crop);
	}
}
