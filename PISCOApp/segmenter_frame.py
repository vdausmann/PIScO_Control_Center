import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory


class SegmenterFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # setting variables
        self.source_folder = tk.StringVar(self, "")
        self.save_crops = tk.BooleanVar(self, False)
        self.save_marked_imgs = tk.BooleanVar(self, False)
        self.min_area_to_segment = tk.StringVar(self, "0")
        self.min_area_to_save = tk.StringVar(self, "0")
        self.save_path = tk.StringVar(self, "")
        self.equalize_hist = tk.BooleanVar(self, False)
        self.resize = tk.BooleanVar(self, False)
        self.clear_save_path = tk.BooleanVar(self, False)
        self.bg_size = tk.StringVar(self, "1")
        self.max_threads = tk.StringVar(self, "1")
        self.n_sigma = tk.StringVar(self, "1")
        self.n_cores = tk.StringVar(self, "1")
        self.mask_imgs = tk.BooleanVar(self, False)
        self.mask_radius_offset = tk.StringVar(self, "0")

        self.settings = {
            "source_folder": self.source_folder,
            "save_crops": self.save_crops,
            "save_marked_imgs": self.save_marked_imgs,
            "min_area_to_segment": self.min_area_to_segment,
            "min_area_to_save": self.min_area_to_save,
            "save_path": self.save_path,
            "equalize_hist": self.equalize_hist,
            "resize": self.resize,
            "clear_save_path": self.clear_save_path,
            "bg_size": self.bg_size,
            "max_threads": self.max_threads,
            "n_sigma": self.n_sigma,
            "n_cores": self.n_cores,
            "mask_imgs": self.mask_imgs,
            "mask_radius_offset": self.mask_radius_offset,
        }

        # source folder
        ctk.CTkLabel(self, text="Source folder:").grid(row=0, column=0)
        ctk.CTkButton(
            self,
            text="Choose folder",
            width=100,
            command=lambda: self.choose_folder(self.source_folder),
        ).grid(row=1, column=0, pady=5, padx=5)

        # save_crops
        ctk.CTkLabel(self, text="Save crops:").grid(row=0, column=1, pady=5, padx=5)
        ctk.CTkCheckBox(self, text="", variable=self.save_crops).grid(
            row=1, column=1, pady=5, padx=5
        )

        # save_marked_imgs
        ctk.CTkLabel(self, text="Save marked imgs:").grid(
            row=0, column=2, pady=5, padx=5
        )
        ctk.CTkCheckBox(self, text="", variable=self.save_marked_imgs).grid(
            row=1, column=2, pady=5, padx=5
        )

        # min_area_to_segment
        ctk.CTkLabel(self, text="Min area to segment:").grid(
            row=0, column=5, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.min_area_to_segment).grid(
            row=1, column=5, pady=5, padx=5
        )

        # min_area_to_save
        ctk.CTkLabel(self, text="Min area to save:").grid(
            row=0, column=4, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.min_area_to_save).grid(
            row=1, column=4, pady=5, padx=5
        )

        # save_path
        ctk.CTkLabel(self, text="Save path").grid(row=2, column=0, pady=5, padx=5)
        ctk.CTkButton(
            self,
            text="Choose folder",
            width=100,
            command=lambda: self.choose_folder(self.save_path),
        ).grid(row=3, column=0, pady=5, padx=5)

        # equalize_hist
        ctk.CTkLabel(self, text="Equalize hist:").grid(row=2, column=1, pady=5, padx=5)
        ctk.CTkCheckBox(self, text="", variable=self.equalize_hist).grid(
            row=3, column=1, pady=5, padx=5
        )

        # resize
        ctk.CTkLabel(self, text="Resize:").grid(row=2, column=2, pady=5, padx=5)
        ctk.CTkCheckBox(self, text="", variable=self.resize).grid(
            row=3, column=2, pady=5, padx=5
        )

        # clear_save_path
        ctk.CTkLabel(self, text="Clear save path:").grid(
            row=2, column=3, pady=5, padx=5
        )
        ctk.CTkCheckBox(self, text="", variable=self.clear_save_path).grid(
            row=3, column=3, pady=5, padx=5
        )

        # mask_imgs
        ctk.CTkLabel(self, text="Mask imgs:").grid(row=0, column=3, pady=5, padx=5)
        ctk.CTkCheckBox(self, text="", variable=self.mask_imgs).grid(
            row=1, column=3, pady=5, padx=5
        )

        # bg_size
        ctk.CTkLabel(self, text="Bg size:").grid(row=2, column=4, pady=5, padx=5)
        ctk.CTkEntry(self, width=60, textvariable=self.bg_size).grid(
            row=3, column=4, pady=5, padx=5
        )

        # max_threads
        ctk.CTkLabel(self, text="Max threads:").grid(row=2, column=5, pady=5, padx=5)
        ctk.CTkEntry(self, width=60, textvariable=self.max_threads).grid(
            row=3, column=5, pady=5, padx=5
        )

        # n_sigma
        ctk.CTkLabel(self, text="n_sigma:").grid(row=0, column=6, pady=5, padx=5)
        ctk.CTkEntry(self, width=60, textvariable=self.n_sigma).grid(
            row=1, column=6, pady=5, padx=5
        )

        # n_cores
        ctk.CTkLabel(self, text="n_cores:").grid(row=2, column=6, pady=5, padx=5)
        ctk.CTkEntry(self, width=60, textvariable=self.n_cores).grid(
            row=3, column=6, pady=5, padx=5
        )

        # mask_radius_offset
        ctk.CTkLabel(self, text="mask radius offset:").grid(
            row=0, column=7, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.mask_radius_offset).grid(
            row=1, column=7, pady=5, padx=5
        )

    def get_settings(self):
        return {key: self.settings[key].get() for key in self.settings.keys()}

    def set_settings(self, settings: dict):
        for key in settings:
            self.settings[key].set(settings[key])

    def choose_folder(self, var):
        dir = askdirectory()
        var.set(dir)
