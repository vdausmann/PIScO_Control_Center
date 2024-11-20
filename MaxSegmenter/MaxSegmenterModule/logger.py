import cv2 as cv
import time
import os
import csv

from threading import Thread
from .utils import ConsumerData


class Logger:
    def __init__(
        self,
        save_crops: bool,
        save_marked_imgs: bool,
        min_area_to_segment: float,
        min_area_to_save: float,
        save_path: str,
        source_path: str,
        equalize_hist: bool,
        clear_save_path: bool,
    ) -> None:
        # settings:
        self.save_crops = save_crops
        self.save_marked_imgs = save_marked_imgs
        self.min_area_to_segment = min_area_to_segment
        self.min_area_to_save = min_area_to_save
        self.save_path = os.path.join(save_path, os.path.basename(source_path))
        self.equalize_hist = equalize_hist

        os.makedirs(self.save_path, exist_ok=True)

        self.csv_save_path = os.path.join(self.save_path, "Data")
        os.makedirs(self.csv_save_path, exist_ok=True)
        with open(os.path.join(self.csv_save_path, f"imgdata.csv"), "a") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["filename", "n_objects_segmented", "n_objects_saved"])
        if self.save_crops:
            self.crop_save_path = os.path.join(self.save_path, "Crops")
            os.makedirs(self.crop_save_path, exist_ok=True)
        if self.save_marked_imgs:
            self.img_save_path = os.path.join(self.save_path, "Images")
            os.makedirs(self.img_save_path, exist_ok=True)

        if clear_save_path:
            for file in os.listdir(self.save_path):
                if os.path.isfile(os.path.join(self.save_path, file)):
                    os.remove(os.path.join(self.save_path, file))
            for file in os.listdir(self.csv_save_path):
                os.remove(os.path.join(self.csv_save_path, file))
            if self.save_crops:
                for file in os.listdir(self.crop_save_path):
                    os.remove(os.path.join(self.crop_save_path, file))
            if self.save_marked_imgs:
                for file in os.listdir(self.img_save_path):
                    os.remove(os.path.join(self.img_save_path, file))

        # log settings
        # log_path = "../LogFiles/Segmenter"
        # with open(log_path + "/test.txt", "w"):
        # ...

    def save_results(self, data: ConsumerData):
        areas = data.areas
        cleaned_img = data.cleaned_img
        filename = data.filename
        crop_counter = 0
        objects_saved = 0

        color_img = cv.cvtColor(cleaned_img, cv.COLOR_GRAY2BGR)

        crop_data: list[list] = []
        for i, bounding_box in enumerate(data.bounding_boxes):
            x, y, w, h = bounding_box
            # resize bounding boxes here:

            if areas[i] >= self.min_area_to_save:
                crop_counter += 1
                objects_saved += 1
                crop_data.append([crop_counter, filename, areas[i], x, y, w, h, 1])
                if self.save_crops:
                    crop = cleaned_img[y : y + h, x : x + h]
                    if self.equalize_hist:
                        crop = cv.equalizeHist(crop)
                    cv.imwrite(
                        os.path.join(
                            self.crop_save_path, f"{filename[:-4]}_{crop_counter}.jpg"
                        ),
                        crop,
                    )

                if self.save_marked_imgs:
                    cv.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 4)

            elif areas[i] >= self.min_area_to_segment:
                crop_counter += 1
                crop_data.append([crop_counter, filename, areas[i], x, y, w, h, 0])

        if self.save_marked_imgs:
            cv.imwrite(
                os.path.join(self.img_save_path, f"{filename[:-4]}.jpg"),
                cv.resize(color_img, (1000, 1000)),
            )

        self.log_img(filename, crop_counter, objects_saved)
        self.log_crop(crop_data, filename)

    def log_img(self, filename, n_objects_segmented, n_objects_saved):
        filepath = os.path.join(self.csv_save_path, f"imgdata.csv")
        data = [[filename, n_objects_segmented, n_objects_saved]]
        Thread(target=self.write_to_csv, args=(filepath, data)).start()

    def log_crop(
        self,
        data: list[list],
        filename: str,
    ):
        filepath = os.path.join(self.csv_save_path, f"{filename[:-4]}_cropdata.csv")
        data = [["ID", "filename", "area", "x", "y", "w", "h", "saved"]] + data
        Thread(target=self.write_to_csv, args=(filepath, data)).start()

    def log_statistic(self, filename: str, duration_detection, duration_saved):
        filepath = os.path.join(self.save_path, f"statistics.csv")
        data = [[filename, duration_detection, duration_saved]]
        Thread(target=self.write_to_csv, args=(filepath, data)).start()

    def write_to_csv(self, filepath: str, data: list[list]):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(data)
