import numpy as np
from dataclasses import dataclass

@dataclass
class Image:
    fname: str
    data: np.ndarray
    color_code: int

