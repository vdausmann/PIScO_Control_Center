import tkinter as tk
import customtkinter as ctk
from tkinter.filedialog import askdirectory


class EvaluationFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.profile_path = tk.StringVar(self, "")
        self.size_of_depth_bins = tk.StringVar(self, "0")
        self.size_of_area_bins = tk.StringVar(self, "0")
        self.only_saved = tk.BooleanVar(self, False)

        self.settings = {
            "profile_path": self.profile_path,
            "size_of_depth_bins": self.size_of_depth_bins,
            "size_of_area_bins": self.size_of_area_bins,
            "only_saved": self.only_saved,
        }

        # profile_path
        ctk.CTkLabel(self, text="Profile path:").grid(row=0, column=0)
        ctk.CTkButton(
            self,
            text="Choose folder",
            width=100,
            command=lambda: self.choose_folder(self.profile_path),
        ).grid(row=1, column=0, pady=5, padx=5)

        # size_of_depth_bins
        ctk.CTkLabel(self, text="Size of depth bins:").grid(
            row=0, column=1, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.size_of_depth_bins).grid(
            row=1, column=1, pady=5, padx=5
        )

        # size_of_area_bins
        ctk.CTkLabel(self, text="Size of area bins:").grid(
            row=0, column=2, pady=5, padx=5
        )
        ctk.CTkEntry(self, width=60, textvariable=self.size_of_area_bins).grid(
            row=1, column=2, pady=5, padx=5
        )

        # only_saved
        ctk.CTkLabel(self, text="Only saved:").grid(row=0, column=3, pady=5, padx=5)
        ctk.CTkCheckBox(self, text="", variable=self.only_saved).grid(
            row=1, column=3, pady=5, padx=5
        )

    def get_settings(self):
        return {key: self.settings[key].get() for key in self.settings.keys()}

    def set_settings(self, settings: dict):
        for key in settings:
            self.settings[key].set(settings[key])

    def choose_folder(self, var):
        dir = askdirectory()
        var.set(dir)
