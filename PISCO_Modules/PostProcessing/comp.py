import h5py 
import numpy as np
import matplotlib.pyplot as plt



file_deconv = "./Results/M202_046-01_PISCO2_20240727-0334_Images-PNG.h5"
file_nodeconv = "./Results/M202_046-01_PISCO2_20240727-0334_Images-PNG_no_deconv.h5"


total_number_objects = 0
areas_deconv = []
with h5py.File(file_deconv, "r") as f:
    print(f[list(f.keys())[0]].keys())
    for key in f:
        group = f[key]
        if not isinstance(group, h5py.Group):
            continue

        area_data = group["area_rprops"]
        if not isinstance(area_data, h5py.Dataset):
            continue

        areas_deconv.extend(np.log10(area_data))
        total_number_objects += len(area_data)


total_number_objects_nodeconv = 0
areas_nodeconv = []
with h5py.File(file_nodeconv, "r") as f:
    for key in f:
        group = f[key]
        if not isinstance(group, h5py.Group):
            continue

        area_data = group["area_rprops"]
        if not isinstance(area_data, h5py.Dataset):
            continue

        areas_nodeconv.extend(np.log10(area_data))
        total_number_objects_nodeconv += len(area_data)

print(total_number_objects, total_number_objects_nodeconv)
# hist_deconv = np.histogram(areas_deconv)
# hist_nodeconv = np.histogram(areas_nodeconv)

plt.hist(areas_deconv, 500)
plt.hist(areas_nodeconv, 500, alpha=0.5)
plt.yscale("log")
plt.xlabel("$\\log_{10}(A)$")
plt.show()
