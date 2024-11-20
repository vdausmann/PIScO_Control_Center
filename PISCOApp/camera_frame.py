import tkinter as tk
import customtkinter as ctk


class CameraFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Camera").pack()
