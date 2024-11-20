from dataclasses import dataclass, field
import numpy as np
from typing import List


@dataclass
class Data:
    def get_tuple(self):
        return tuple(v for v in self.__dict__.values())

    def __str__(self):
        s = ""
        for key in self.__dict__.keys():
            s += f"{key}: {self.__dict__[key]}, "
        return s


# will be send from producer to consumer
@dataclass
class ProducerData(Data):
    finished: bool = False
    filename: str = ""
    read_at: float = 0
    corrected_img: np.ndarray = field(default_factory= lambda: np.zeros(0))
    original_img_mean: float = 0
    resized: bool = False


# will be send from consumer to logger
@dataclass
class ConsumerData(Data):
    filename: str = ""
    read_at: float = 0
    segmented_at: float = 0
    cleaned_img: np.ndarray = field(default_factory= lambda: np.zeros(0))
    bounding_boxes: list[tuple[int, int, int, int]] = field(default_factory=lambda: [])
    areas: list[float] = field(default_factory=lambda: [])


@dataclass
class Message:
    def get_tuple(self):
        return tuple(v for v in self.__dict__.values())

    def __str__(self):
        s = ""
        for key in self.__dict__.keys():
            s += f"{key}: {self.__dict__[key]}, "
        return s


@dataclass
class ImgMessage(Message):
    finished: int = 0
    filename: str = ""
    corrected: np.ndarray | None = None
    org_mean: float = 0
    n_objects: int = 0
    starting_time: float = 0
    received_at: float = 0
    finished_at: float = 0

    def __str__(self):
        return f"File {self.filename}: Total time: {self.finished_at - self.starting_time}, producer time: {self.received_at - self.starting_time}, {self.n_objects} objects found"


@dataclass
class CropMessage(Message):
    org_img_fn: str = ""
    crop_fn: str = ""
    bounding_box: tuple[int, int, int, int] = (0, 0, 0, 0)
    area: float = 0


@dataclass
class SummaryMessage(Message):
    total_time: float = 0
    avg_time: float = 0
    n_imgs_segmented: int = 0


def print_message(app, message: str):
    if app is None:
        print(message)
    else:
        app.print(message)
