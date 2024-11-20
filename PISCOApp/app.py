import tkinter as tk
import customtkinter as ctk
import pickle
from pathlib import Path


from segmenter_frame import SegmenterFrame
from evaluation_frame import EvaluationFrame
from camera_frame import CameraFrame
from metadata_frame    import MetadataFrame

from sidebar import Sidebar 


ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class PiscoAPP(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PISCO Segmenter")
        width, height = 2200, 1000
        self.geometry(f"{2200}x{1000}")

        ###################################################
        # sidebar:
        self.sidebar = ctk.CTkFrame(
            self, width=200, height=height - 27, corner_radius=10
        )
        self.sidebar.place(x=5, y=22)
        Sidebar(self.sidebar, self).pack()

        ###################################################
        # tabview:
        self.tabview = ctk.CTkTabview(
            self, width=width - 220, height=height - 310, corner_radius=10
        )
        self.tabview.add("Metadata")
        self.tabview.place(x=205, y=5)
        self.tabview.add("Segmenter")
        self.tabview.add("Camera")
        self.tabview.add("Evaluation")




    
        

        self.segmenter_frame = SegmenterFrame(self.tabview.tab("Segmenter"))
        self.segmenter_frame.pack()

        self.camera_frame = CameraFrame(self.tabview.tab("Camera"))
        self.camera_frame.pack()

        self.evaluation_frame = EvaluationFrame(self.tabview.tab("Evaluation"))
        self.evaluation_frame.pack()

        self.metadata_frame = MetadataFrame(self.tabview.tab("Metadata"))
        self.metadata_frame.pack()

        ###################################################
        # output:
        self.output_box = ctk.CTkTextbox(self, width=width - 220, height=height - 310)
        self.output_box.place(x=205, y=height - 600)

        # load settings
        self.load_settings()
       

    def print(self, message: str):
        self.output_box.configure(state="normal")
        self.output_box.insert(tk.END, message.strip() + "\n")
        self.output_box.configure(state="disabled")
        self.output_box.see("end")

    def save_settings(self):
        segmenter_settings = self.segmenter_frame.get_settings()
        evaluation_settings = self.evaluation_frame.get_settings()
        metadata_settings = self.metadata_frame.get_settings()
        
        root_dir = Path(__file__).resolve().parent.parent
        settingsfilnm=root_dir / "app_default_settings.pickle"
        
        with open(settingsfilnm, "wb") as f:
            pickle.dump([segmenter_settings, evaluation_settings,metadata_settings], f)
            print([segmenter_settings, evaluation_settings,metadata_settings])
            print("Settings saved")

    def load_settings(self):
        root_dir = Path(__file__).resolve().parent.parent
        settingsfilnm=root_dir / "app_default_settings.pickle"
        with open(settingsfilnm, "rb") as f:
        
        ## change back for ship
        
        #with open("/home/pisco-controller/Desktop/PISCO_Software/app_default_settings.pickle", "rb") as f:
            settings = pickle.load(f)
        print(settings)
        self.segmenter_frame.set_settings(settings[0])
        self.evaluation_frame.set_settings(settings[1])
        self.metadata_frame.set_settings(settings[2])
        print("Settings loaded")


if __name__ == "__main__":
    a = PiscoAPP()
    a.mainloop()
