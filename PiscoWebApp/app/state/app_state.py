from pathlib import Path
from typing import Optional

class AppState:
    def __init__(self):
        self.selected_hdf_file: Optional[Path] = None

app_state = AppState()
