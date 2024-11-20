import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
import os
from PIL import Image
import torch.nn.functional as F
import cv2
from tqdm import tqdm
import numpy as np
from concurrent.futures import ProcessPoolExecutor

class UnlabelledImageDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_dir = img_dir
        self.img_names = sorted(os.listdir(img_dir))
        self.transform = transform

    def __len__(self):
        return len(self.img_names)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_names[idx])
        image = Image.open(img_path).convert('L')
        if self.transform:
            image = self.transform(image)
        return image, 0  # Return a dummy label

transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((1272, 1272)),  # define the desired height and width
    transforms.ToTensor()
])

def make_video():
    #dataset = UnlabelledImageDataset('/mnt/m181_pisco1/M181-175-1_CTD-050_00deg00S-019deg00W_20220509-0543/PNG/', transform=transform)
    dataset = UnlabelledImageDataset('/home/plankton/Data/M181_test_set', transform=transform)
    dataloader = DataLoader(dataset, batch_size=1, num_workers=4)  # adjust batch_size and num_workers as needed
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # Define the video writer (make sure to match the height and width in the transform)
    #video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, (1272,1272))
    video = cv2.VideoWriter('/home/plankton/Videos/test_video.mp4', fourcc, 30, (1272,1272))

    # Iterate over the DataLoader
    for image, _ in tqdm(dataloader):
        # Convert the tensor back to a numpy array
        image = image.squeeze().numpy() * 255  # remove batch dimension, convert to numpy, and scale to [0, 255]

        # Convert the data type to unsigned 8-bit integer
        image = image.astype(np.uint8)

        # Add an extra dimension to make the image shape (height, width, 1)
        image = np.expand_dims(image, axis=2)

        # Write the image to the video
        # OpenCV expects a shape of (height, width, channels), so we need to transpose from (channels, height, width)
        video.write(image)

    # Close the video file
    cv2.destroyAllWindows()
    video.release()

def read_and_resize(image):
    img = cv2.imread(os.path.join(image_folder, image))
    img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
    min_val = np.min(img)
    max_val = np.max(img)

    img = (img - min_val)/ (max_val - min_val) *255
    img = img.astype('uint8')
    #print(img.shape)

    #img = cv2.clip(img, 0, 255)

    #print(image)

    #img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)

    # # Extract relevant information from the file name ***M181***
    #info = image.split('_')
    #date = info[0].split('-')[0]
    #time = info[0].split('-')[1]
    #pressure = info[1]
    #temperature = info[2].split('.')[0]+'.'+info[2].split('.')[1]
    #temperature = info[2].split('_')[0]

    #MSM126 info: MSM126_005-03_PISCO2_0851.32dbar-32.64N-016.68W-10.65C_20240211-07172070
    # # # Extract relevant information from the file name
    info = image.split('_')
    #print(info)
    date = info[4].split('-')[0]
    time = info[4].split('-')[1].split('.')[0]
    pressure = info[3]
    # #temperature = info[2].split('.')[0]+'.'+info[2].split('.')[1]

    ###Heincke
    #  # Extract relevant information from the file name
    # info = image.split('_')
    # #print(info)
    # date = info[4]
    # time = str(info[5].split('.')[:2])
    # pressure = info[3].split('-')[0]
    # #temperature = info[2].split('.')[0]+'.'+info[2].split('.')[1]



    # Add the information as text on the image
    font = cv2.FONT_HERSHEY_DUPLEX
    fontScale = 0.5
    #fontColor = (255, 255, 255)  # White color
    fontColor = (0, 0, 0)  # Black color
    lineType = 1
    x_offset = 10
    y_offset = 30
    line_height = 15

    cv2.putText(img, f"Date: {date}", (x_offset, y_offset), font, fontScale, fontColor, lineType)
    cv2.putText(img, f"Time: {time}", (x_offset, y_offset + line_height), font, fontScale, fontColor, lineType)
    cv2.putText(img, f"Pressure: {pressure}", (x_offset, y_offset + 2 * line_height), font, fontScale, fontColor, lineType)
    #cv2.putText(img, f"Temperature: {temperature}", (x_offset, y_offset + 3 * line_height), font, fontScale, fontColor, lineType)

    return img

def timesort(file):
    try:
        return (int(file.split("_")[4][:8]+file.split("_")[4][9:17] ))
    except IndexError:
        return (int(file.split("_")[0][:8]+file.split("_")[0][9:17] ))

def list_images(image_folder):
    # Get a list of all the image files
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg") or img.endswith(".bmp")]

    # Sort the images by number in their name (optional)
    #images.sort(key = lambda x: x.split('-')[1].split('_')[0])
    # images.sort(key = lambda x: x.split('_')[3].split('-')[0])
    images.sort(key=timesort)
    return images

def make_video_pool(image_folder, result_folder):

    images = list_images(image_folder)
    print('list created')
    height = 640#1280
    width = 640#1280
    video = cv2.VideoWriter(result_folder, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width,height))

    #try with for loop
    for image in tqdm(images):
        im = read_and_resize(image)
        #print(im.shape)
        video.write(im)

    ## Create a ProcessPoolExecutor
    # with ProcessPoolExecutor() as executor:
    #     ##Get a future for each image
    #     futures = [executor.submit(read_and_resize, image) for image in images]
    #     print('images resized...')

    #     ##Get the shape from the first image
    #     height, width, layers = futures[0].result().shape

    #     ##Define the video writer
    #     video = cv2.VideoWriter(result_folder, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width,height))

    #     ##Add each (resized) image to the video
    #     for future in tqdm(futures):
    #        video.write(future.result())

    # Close the video file
    cv2.destroyAllWindows()
    video.release()




if __name__ == "__main__":
        # Define the path to your image folder
    #image_folder = '/home/plankton/Results/M181/M181-175-1_CTD-050_00deg00S-019deg00W_20220509-0543/Images/'
    image_folder = '/home/pisco-controller/M202/20240730/20240730-2259_M202_071-1_PISCO2_png_Segmentation_results/Images'
    result_folder = '/home/pisco-controller/M202/20240730/20240730-2259_M202_071-1_PISCO2_png_Segmentation_results/video_contrast_stretch.mp4'
    make_video_pool(image_folder=image_folder, result_folder=result_folder)

    # Call the function to make the video
    #root_path = '/media/plankton/30781fe1-cea5-4503-ae00-1986beb935d2/Segmentation_results/M181/results_240328/'
    #for folder in tqdm(os.listdir(root_path)):
    #    if '°' in folder:
    #        image_folder = os.path.join(root_path, folder, 'Images')
    #        result_folder = os.path.join(root_path, folder, 'segmented_profile_video.mp4')
    #        make_video_pool(image_folder=image_folder, result_folder=result_folder)


