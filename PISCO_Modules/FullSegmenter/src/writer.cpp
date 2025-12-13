#include "writer.hpp"
#include "types.hpp"
#include "parser.hpp"
#include <H5PredType.h>
#include <H5public.h>
#include <fstream>
#include <ctime>
#include <iostream>

////////////////////////////////////////////////////////////////////////////////////////
/// Helper functions for HDF writer:
////////////////////////////////////////////////////////////////////////////////////////
///
// Helper: write a string attribute
void writeStringAttribute(H5::H5Object& obj, 
                          const std::string& attr_name, 
                          const std::string& value)
{
	H5::StrType strdatatype(H5::PredType::C_S1, H5T_VARIABLE);

	H5::DataSpace dataspace(H5S_SCALAR);

	H5::Attribute attribute = obj.createAttribute(
        attr_name, strdatatype, dataspace
    );

    attribute.write(strdatatype, value);
}

// Helper: write a numeric attribute
template <typename T>
void writeScalarAttribute(H5::H5Object& obj,
                          const std::string& attr_name,
                          const T& value)
{
	H5::DataSpace dataspace(H5S_SCALAR);
	H5::Attribute attribute = obj.createAttribute(
        attr_name,
        H5::PredType::NATIVE_DOUBLE,
        dataspace
    );

    double tmp = static_cast<double>(value);
    attribute.write(H5::PredType::NATIVE_DOUBLE, &tmp);
}
////////////////////////////////////////////////////////////////////////////////////////



Error initH5ProfileFile(H5::H5File& file)
{
	try {
		// create file name like the profile:
		file = H5::H5File(e_savePath + e_profileName + ".h5", H5F_ACC_TRUNC);

		// write some segmentation metadata etc. in the files attributes
		time_t rawtime;
		struct tm * timeinfo;
		char buffer[80];

		time (&rawtime);
		timeinfo = localtime(&rawtime);

		strftime(buffer,sizeof(buffer),"%d-%m-%Y %H:%M:%S",timeinfo);
		std::string datetime(buffer);
		writeStringAttribute(file, "Date and time of Segmentation", datetime);
		writeStringAttribute(file, "Profile name", e_profileName);
		writeStringAttribute(file, "Image Source Path", e_sourcePath);
		// TODO: write more
		std::cout << "File id: " << file.getId() << std::endl;

    } catch (H5::Exception& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while initializing HDF file: " + e.getDetailMsg());
        return error;
    }

	return Error::Success;
}


void writeData(std::unordered_map<size_t, std::vector<SegmenterObject>>& objectData,
		const std::vector<Image>& imageStack , const H5::H5File& file, 
		const std::vector<std::string>& files)
{
	for (const Image& image: imageStack) {
		std::string filename = files[image.id];
		size_t idx = filename.find_last_of('/');
		filename = filename.substr(idx + 1, filename.size());
		filename = "/" + filename.substr(0, filename.size() - 4);
		std::cout << "Creating group for file " << filename << std::endl;
		H5::Group group = file.createGroup(filename);

		size_t numObjects = objectData[image.id].size();
		std::vector<double> areas, x, y, w, h;
		areas.reserve(numObjects);
		x.reserve(numObjects);
		y.reserve(numObjects);
		w.reserve(numObjects);
		h.reserve(numObjects);
		for (const SegmenterObject& object: objectData[image.id]) {
			areas.push_back(object.area);
			x.push_back(object.boundingBox.x);
			y.push_back(object.boundingBox.y);
			w.push_back(object.boundingBox.width);
			h.push_back(object.boundingBox.height);
		}

		hsize_t dims[1] = { numObjects };
		H5::DataSpace dataspace(1, dims);

		H5::DataSet dataset = group.createDataSet("Areas", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(areas.data(), H5::PredType::NATIVE_DOUBLE);

		dataset = group.createDataSet("Bounding Box x", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(x.data(), H5::PredType::NATIVE_DOUBLE);

		dataset = group.createDataSet("Bounding Box y", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(y.data(), H5::PredType::NATIVE_DOUBLE);

		dataset = group.createDataSet("Bounding Box Width", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(w.data(), H5::PredType::NATIVE_DOUBLE);

		dataset = group.createDataSet("Bounding Box Height", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(h.data(), H5::PredType::NATIVE_DOUBLE);
	}
}




////////////////////////////////////////////////////////////////////////////////////////
/// CSV writer functions:
////////////////////////////////////////////////////////////////////////////////////////
std::ofstream initProgressFile() 
{
	return std::ofstream(e_savePath + e_profileName + "_progress.dat");
}

std::ofstream initObjectFile() 
{
	std::ofstream file(e_savePath + e_profileName + "_object_data.dat");
	file << "Image ID,Object Area," 
		<< "Bounding Box x,Bounding Box y,Bounding Box width,Bounding Box height\n";
	return file;
}

std::ofstream initImageFile() 
{
	std::ofstream file(e_savePath + e_profileName + "_image_data.dat");
	file << "Image ID,Mean,Stddev,Bg Corrected Mean,Bg Corrected Stddev\n";
	return file;
}


void writeProgress(const std::vector<std::string>& files,
		const std::vector<Image>& imageStack, std::ofstream& progressFile)
{
	for (const Image& img: imageStack) {
		progressFile << files[img.id] << "\n";
	}
}

void writeObjectData(const std::unordered_map<size_t, std::vector<SegmenterObject>>& objectData,
		std::ofstream& objectFile)
{
	for (auto const& [id, objects]: objectData) {
		for (const SegmenterObject& object: objects) {
			objectFile << object.id << "," << object.area << "," << object.boundingBox.x 
				<< "," << object.boundingBox.y << "," << object.boundingBox.width 
				<< "," << object.boundingBox.height 
				<< "\n";
		}
	}
}

void writeImageData(const std::vector<Image>& imageStack, std::ofstream& imageFile)
{
	for (const Image& img: imageStack) {
		imageFile << img.id << "," << img.meanOrg << "," << img.stddevOrg << ","
			<< img.meanCorrected << "," << img.stddevCorrected << "," 
			<< img.detectionThreshold
			<< "\n";
	}
}
