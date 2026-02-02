#include "writer.hpp"
#include "types.hpp"
#include "parser.hpp"
#include <H5Fpublic.h>
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

void writeIntAttribute(H5::H5Object& obj, const std::string& attr_name, int value)
{
	H5::DataSpace dataspace(H5S_SCALAR);
	H5::Attribute attribute = obj.createAttribute(
        attr_name,
        H5::PredType::NATIVE_INT,
        dataspace
    );

    attribute.write(H5::PredType::NATIVE_INT, &value);
}


Error incrementAttribute(H5::H5File& file, const std::string& attrName)
{
    try {
        H5::Attribute attr;
        H5::DataSpace scalarSpace(H5S_SCALAR);
        int value = 0;

        // Check if the attribute exists
        if (H5Aexists(file.getId(), attrName.c_str())) {
            attr = file.openAttribute(attrName);

            attr.read(H5::PredType::NATIVE_INT, &value);
            value += 1;
            attr.write(H5::PredType::NATIVE_INT, &value);
        } else {
            value = 1;
            attr = file.createAttribute(attrName, H5::PredType::NATIVE_INT, scalarSpace);
            attr.write(H5::PredType::NATIVE_INT, &value);
        }
		return Error::Success;
    } catch (H5::Exception& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while initializing HDF file: " + e.getDetailMsg());
        return error;
    }
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
		writeStringAttribute(file, "Date and Time of Segmentation", datetime);
		writeStringAttribute(file, "Profile Name", e_profileName);
		writeStringAttribute(file, "Image Source Path", e_sourcePath);
		writeScalarAttribute(file, "Setting: imageStackSize", e_imageStackSize);
		writeScalarAttribute(file, "Setting: minArea", e_minArea);
		writeScalarAttribute(file, "Setting: minMean", e_minMean);
		writeScalarAttribute(file, "Setting: minStdDev", e_minStdDev);

		// TODO: write more
		std::cout << "File id: " << file.getId() << std::endl;
		file.close();

    } catch (H5::Exception& e) {
		Error error = Error::RuntimeError;
		error.addMessage("Error while initializing HDF file: " + e.getDetailMsg());
        return error;
    }

	return Error::Success;
}


void writeData(std::unordered_map<size_t, Objects>& objectData,
		const std::vector<Image>& imageStack, 
		const std::vector<std::string>& files)
{
	// only open the file when writing to it and closing it directly after as a safety
	// feature.
	H5::H5File file = H5::H5File(e_savePath + e_profileName + ".h5", H5F_ACC_RDWR);
	for (const Image& image: imageStack) {
		std::string filename = files[image.id];
		size_t idx = filename.find_last_of('/');
		filename = filename.substr(idx + 1, filename.size());
		filename = "/" + filename.substr(0, filename.size() - 4);
		// std::cout << "Creating group for file " << filename << std::endl;
		H5::Group group = file.createGroup(filename);
		writeScalarAttribute(group, "Detection Threshold", image.detectionThreshold);
		writeScalarAttribute(group, "Mean Original", image.meanOrg);
		writeScalarAttribute(group, "Mean corrected", image.meanCorrected);
		writeScalarAttribute(group, "Stddev Original", image.stddevOrg);
		writeScalarAttribute(group, "Stddev corrected", image.stddevCorrected);

		Objects objects = objectData[image.id];
		size_t numObjects = objects.width.size();
		hsize_t dims[1] = { numObjects };
		H5::DataSpace dataspace(1, dims);

		writeIntAttribute(group, "Number of objects", objects.width.size());

		H5::DataSet dataset = group.createDataSet("width", H5::PredType::NATIVE_INT, dataspace);
		dataset.write(objects.width.data(), H5::PredType::NATIVE_INT);
		dataset = group.createDataSet("height", H5::PredType::NATIVE_INT, dataspace);
		dataset.write(objects.height.data(), H5::PredType::NATIVE_INT);
		dataset = group.createDataSet("bx", H5::PredType::NATIVE_INT, dataspace);
		dataset.write(objects.bx.data(), H5::PredType::NATIVE_INT);
		dataset = group.createDataSet("by", H5::PredType::NATIVE_INT, dataspace);
		dataset.write(objects.by.data(), H5::PredType::NATIVE_INT);

		dataset = group.createDataSet("circ", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.circ.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("area_exc", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.area_exc.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("area_rprops", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.area_rprops.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("area%", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.area_percentage.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("major", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.major.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("minor", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.minor.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("centroid_x", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.centroidx.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("centroid_y", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.centroidy.data(), H5::PredType::NATIVE_DOUBLE);
		// dataset = group.createDataSet("convex_area", H5::PredType::NATIVE_DOUBLE, dataspace);
		// dataset.write(objects.convexArea.data(), H5::PredType::NATIVE_DOUBLE);
		// dataset = group.createDataSet("min_intensity", H5::PredType::NATIVE_DOUBLE, dataspace);
		// dataset.write(objects.minIntensity.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("perimeter", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.perimeter.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("circex", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.circex.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("angle", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.angle.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("boundingBoxArea", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.boundingBoxArea.data(), H5::PredType::NATIVE_DOUBLE);
		dataset = group.createDataSet("eccentricity", H5::PredType::NATIVE_DOUBLE, dataspace);
		dataset.write(objects.eccentricity.data(), H5::PredType::NATIVE_DOUBLE);

		if (e_saveCrops) {
			size_t numPixels = objects.crops.size();
			// std::cout << "Writing " << numPixels << " pixel values\n";
			hsize_t cropDims[1] = { numPixels };
			dataspace = H5::DataSpace(1, cropDims);

			if (numPixels >= e_chunkSize) { 
				H5::DSetCreatPropList plist;
				hsize_t chunk[1] = {e_chunkSize};
				plist.setChunk(1, chunk);
				plist.setShuffle();
				plist.setDeflate(e_compressionLevel);
				dataset = group.createDataSet("1D_crop_data", H5::PredType::NATIVE_UINT8, 
						dataspace, plist);
			} else {
				dataset = group.createDataSet("1D_crop_data", H5::PredType::NATIVE_UINT8, 
						dataspace);
			}
			dataset.write(objects.crops.data(), H5::PredType::NATIVE_UINT8);
		}

		incrementAttribute(file, "Number of images:").check();
	}
	file.close();
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
