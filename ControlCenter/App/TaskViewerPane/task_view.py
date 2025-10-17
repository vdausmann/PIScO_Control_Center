from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

from TaskManagerServer.Backend.types import Task, TaskTemplate

from .server_client import ServerClient
from .metadata_view import MetadataView
from .modules_view import ModulesView


class TaskView(QWidget):

    def __init__(self, task: Task | TaskTemplate, client: ServerClient, parent=None) -> None:
        super().__init__(parent)

        self.task = task
        self.client = client

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLineEdit(self.task.name)
        self.name_label.setText("Task Name")
        self.name_label.selectAll()
        main_layout.addWidget(self.name_label, 1)

        self.task_id_label: QLabel | None = None
        if isinstance(self.task, Task):
            self.task_id_label = QLabel(self.task.task_id)
            main_layout.addWidget(self.task_id_label, 1)

        ## Metadata
        self.metadata_view = MetadataView(self.task.meta_data, self.client)
        main_layout.addWidget(self.metadata_view, 10)

        ## Modules
        if isinstance(self.task, Task):
            self.modules_view = ModulesView(self.task.task_id, [], self.client)
        else:
            self.modules_view = ModulesView("", self.task.modules, self.client)
        main_layout.addWidget(self.modules_view, 10)
