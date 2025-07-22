import sys
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListView, QLabel, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QScrollArea, QSizePolicy, QSpacerItem, QComboBox,
    QMenu, QStackedWidget
)
from PySide6.QtCore import (
    Qt, QAbstractListModel, QModelIndex, Signal, Slot, QObject, QSize
)
from PySide6.QtGui import QColor, QPalette, QAction, QIcon

# --- Data Models ---

class Module:
    """Represents a single module within a task."""
    def __init__(self, name: str, settings: dict = None):
        self.name = name
        self.settings = settings if settings is not None else {}

    def to_dict(self):
        return {"name": self.name, "settings": self.settings}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], data.get("settings", {}))

class Task:
    """Represents a scientific task, a collection of modules and their settings."""
    def __init__(self, name: str, description: str = "", modules: list = None):
        self.name = name
        self.description = description
        self.modules = modules if modules is not None else []
        self.status = "Idle" # Possible statuses: Idle, Running, Paused, Finished

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "modules": [m.to_dict() for m in self.modules],
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict):
        modules = [Module.from_dict(m_data) for m_data in data.get("modules", [])]
        task = cls(data["name"], data.get("description", ""), modules)
        task.status = data.get("status", "Idle")
        return task

# --- State Management ---

class StateManager:
    """Handles saving and loading the application state."""
    def __init__(self, file_path="app_state.json"):
        self.file_path = file_path

    def save_state(self, tasks: list[Task], current_task_index: int = -1):
        """Saves the current application state to a JSON file."""
        state_data = {
            "tasks": [task.to_dict() for task in tasks],
            "current_task_index": current_task_index
        }
        try:
            with open(self.file_path, "w") as f:
                json.dump(state_data, f, indent=4)
            print(f"Application state saved to {self.file_path}")
        except IOError as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        """Loads the application state from a JSON file."""
        if not os.path.exists(self.file_path):
            print("No saved state found. Starting with empty state.")
            return [], -1
        try:
            with open(self.file_path, "r") as f:
                state_data = json.load(f)
            tasks = [Task.from_dict(t_data) for t_data in state_data.get("tasks", [])]
            current_task_index = state_data.get("current_task_index", -1)
            print(f"Application state loaded from {self.file_path}")
            return tasks, current_task_index
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading state: {e}")
            return [], -1

# --- Custom Widgets ---

class ModuleSettingsWidget(QWidget):
    """Widget to display and edit settings for a single module."""
    settings_changed = Signal()

    def __init__(self, module: Module, parent=None):
        super().__init__(parent)
        self.module = module
        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # No extra margins for internal layout

        # Example: Add a simple setting for 'delay'
        self.delay_input = QLineEdit(str(self.module.settings.get("delay_ms", 1000)))
        self.delay_input.setPlaceholderText("Delay in ms")
        self.delay_input.textChanged.connect(self._update_settings)
        self.layout.addRow("Delay (ms):", self.delay_input)

        # Add more settings as needed
        # self.layout.addRow("Another Setting:", QLineEdit())

        self.setStyleSheet("""
            ModuleSettingsWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f8f8;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 4px;
            }
        """)

    @Slot()
    def _update_settings(self):
        try:
            self.module.settings["delay_ms"] = int(self.delay_input.text())
        except ValueError:
            self.module.settings["delay_ms"] = 0 # Default or handle error
        self.settings_changed.emit()

class TaskEditorDialog(QDialog):
    """Dialog for creating or editing a task."""
    task_saved = Signal(Task) # Emits the updated or new Task object

    def __init__(self, existing_task: Task = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Editor")
        self.setMinimumSize(600, 500)

        self.original_task = existing_task # Keep a reference to the original task
        self.edited_task = Task.from_dict(existing_task.to_dict()) if existing_task else Task("New Task")

        self.module_widgets = [] # Store references to ModuleSettingsWidget instances

        self.init_ui()
        self._load_task_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Task Name and Description
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        form_layout.addRow("Task Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        main_layout.addLayout(form_layout)

        # Module Management
        module_section_layout = QVBoxLayout()
        module_section_layout.addWidget(QLabel("<b>Modules:</b>"))

        self.module_list_layout = QVBoxLayout()
        self.module_list_layout.addStretch(1) # Allows adding widgets from top

        # Scroll area for modules
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.module_list_layout)
        scroll_area.setWidget(scroll_content)
        module_section_layout.addWidget(scroll_area)

        # Module Add/Remove Buttons
        module_buttons_layout = QHBoxLayout()
        self.add_module_button = QPushButton("Add Module")
        self.add_module_button.clicked.connect(self._add_module)
        self.remove_module_button = QPushButton("Remove Selected Module")
        self.remove_module_button.clicked.connect(self._remove_module)
        module_buttons_layout.addWidget(self.add_module_button)
        module_buttons_layout.addWidget(self.remove_module_button)
        module_buttons_layout.addStretch(1)
        module_section_layout.addLayout(module_buttons_layout)

        main_layout.addLayout(module_section_layout)

        # Save/Cancel Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Task")
        self.save_button.clicked.connect(self._save_task)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch(1)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)

    def _load_task_data(self):
        """Populates the editor with the task's current data."""
        self.name_input.setText(self.edited_task.name)
        self.description_input.setText(self.edited_task.description)
        for module in self.edited_task.modules:
            self._add_module_widget(module)

    def _add_module(self):
        """Adds a new generic module to the edited task."""
        new_module = Module(f"Module {len(self.edited_task.modules) + 1}")
        self.edited_task.modules.append(new_module)
        self._add_module_widget(new_module)

    def _add_module_widget(self, module: Module):
        """Helper to create and add a ModuleSettingsWidget to the layout."""
        module_widget = QWidget()
        module_widget_layout = QHBoxLayout(module_widget)
        module_widget_layout.setContentsMargins(5, 5, 5, 5) # Small margins for internal layout

        # Module name display
        module_name_label = QLabel(module.name)
        module_name_label.setStyleSheet("font-weight: bold;")
        module_widget_layout.addWidget(module_name_label)
        module_widget_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Module settings
        settings_widget = ModuleSettingsWidget(module)
        settings_widget.settings_changed.connect(self._update_task_data) # Connect to update task data
        module_widget_layout.addWidget(settings_widget)

        # Remove button for this specific module
        remove_btn = QPushButton("X")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        remove_btn.clicked.connect(lambda: self._remove_specific_module(module_widget, module))
        module_widget_layout.addWidget(remove_btn)

        # Insert before the stretch item
        self.module_list_layout.insertWidget(self.module_list_layout.count() - 1, module_widget)
        self.module_widgets.append((module_widget, module)) # Store widget and module for removal

    def _remove_module(self):
        """Removes the last added module. (Could be improved to select specific module)"""
        if self.module_widgets:
            widget_to_remove, module_to_remove = self.module_widgets.pop()
            self.module_list_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
            self.edited_task.modules.remove(module_to_remove)
            self._update_task_data()

    def _remove_specific_module(self, widget_to_remove: QWidget, module_to_remove: Module):
        """Removes a specific module widget and its corresponding module from the task."""
        self.module_list_layout.removeWidget(widget_to_remove)
        widget_to_remove.deleteLater()
        if module_to_remove in self.edited_task.modules:
            self.edited_task.modules.remove(module_to_remove)
        # Also remove from our tracking list
        self.module_widgets = [(w, m) for w, m in self.module_widgets if w != widget_to_remove]
        self._update_task_data()


    def _update_task_data(self):
        """Updates the edited task object from the UI inputs."""
        self.edited_task.name = self.name_input.text()
        self.edited_task.description = self.description_input.text()
        # Module settings are updated directly by ModuleSettingsWidget's signal

    def _save_task(self):
        """Validates and saves the task."""
        self._update_task_data() # Ensure latest data is captured

        if not self.edited_task.name.strip():
            QMessageBox.warning(self, "Input Error", "Task name cannot be empty.")
            return

        self.task_saved.emit(self.edited_task)
        self.accept() # Close the dialog

# --- Task List Model ---

class TaskListModel(QAbstractListModel):
    """Model for the list of tasks."""
    def __init__(self, tasks: list[Task] = None, parent=None):
        super().__init__(parent)
        self._tasks = tasks if tasks is not None else []

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        task = self._tasks[index.row()]
        if role == Qt.DisplayRole:
            return f"{task.name} ({task.status})"
        elif role == Qt.UserRole: # Custom role to return the actual Task object
            return task
        elif role == Qt.ForegroundRole:
            if task.status == "Running":
                return QColor("green")
            elif task.status == "Paused":
                return QColor("orange")
            elif task.status == "Finished":
                return QColor("gray")
            else:
                return QColor("black") # Idle
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        return len(self._tasks)

    def add_task(self, task: Task):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._tasks.append(task)
        self.endInsertRows()

    def update_task(self, old_task: Task, new_task: Task):
        """Updates an existing task in the model."""
        try:
            row = self._tasks.index(old_task)
            self._tasks[row] = new_task
            index = self.index(row, 0)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.UserRole, Qt.ForegroundRole])
        except ValueError:
            print(f"Task '{old_task.name}' not found for update.")

    def remove_task(self, index: QModelIndex):
        if not index.isValid():
            return False
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        del self._tasks[index.row()]
        self.endRemoveRows()
        return True

    def get_task_at_index(self, index: QModelIndex) -> Task | None:
        if index.isValid() and 0 <= index.row() < len(self._tasks):
            return self._tasks[index.row()]
        return None

    def get_all_tasks(self) -> list[Task]:
        return self._tasks

    def get_task_index(self, task: Task) -> int:
        try:
            return self._tasks.index(task)
        except ValueError:
            return -1

    def refresh_task_status(self, task: Task):
        """Refreshes the display for a specific task based on its status."""
        try:
            row = self._tasks.index(task)
            index = self.index(row, 0)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ForegroundRole])
        except ValueError:
            pass # Task might have been removed or not found

# --- New Page Classes ---

class TaskPage(QWidget):
    """Encapsulates the task management UI."""
    # Signals to communicate task status changes back to MainWindow for menu actions
    task_status_changed = Signal(Task)
    task_selection_changed = Signal(Task) # Emits the newly selected task or None

    def __init__(self, task_model: TaskListModel, parent=None):
        super().__init__(parent)
        self.task_model = task_model
        self.current_task = None # Reference to the currently selected task
        self.init_ui()
        # Connect to the model's dataChanged signal to update display if task data changes externally
        self.task_model.dataChanged.connect(self._on_model_data_changed)


    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # --- Left Pane: Task List ---
        left_pane = QVBoxLayout()
        left_pane.addWidget(QLabel("<b>Tasks:</b>"))

        self.task_list_view = QListView()
        self.task_list_view.setModel(self.task_model)
        self.task_list_view.setEditTriggers(QListView.NoEditTriggers) # Tasks edited via dialog
        self.task_list_view.selectionModel().currentChanged.connect(self._on_task_selection_changed)
        left_pane.addWidget(self.task_list_view)

        # Task management buttons
        task_buttons_layout = QHBoxLayout()
        self.new_task_button = QPushButton("New Task")
        self.new_task_button.clicked.connect(self._create_new_task)
        self.edit_task_button = QPushButton("Edit Task")
        self.edit_task_button.clicked.connect(self._edit_selected_task)
        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.clicked.connect(self._delete_selected_task)
        task_buttons_layout.addWidget(self.new_task_button)
        task_buttons_layout.addWidget(self.edit_task_button)
        task_buttons_layout.addWidget(self.delete_task_button)
        left_pane.addLayout(task_buttons_layout)

        main_layout.addLayout(left_pane, 1) # Give left pane 1 unit of stretch

        # --- Right Pane: Current Task Info & Controls ---
        right_pane = QVBoxLayout()
        right_pane.addWidget(QLabel("<b>Current Task:</b>"))

        # Current Task Display
        self.current_task_name_label = QLabel("No task selected")
        self.current_task_name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3;")
        self.current_task_description_label = QLabel("")
        self.current_task_description_label.setWordWrap(True)
        self.current_task_status_label = QLabel("Status: Idle")
        self.current_task_status_label.setStyleSheet("font-style: italic; color: #555;")

        right_pane.addWidget(self.current_task_name_label)
        right_pane.addWidget(self.current_task_description_label)
        right_pane.addWidget(self.current_task_status_label)

        # Current Task Modules Display
        right_pane.addWidget(QLabel("<b>Task Modules:</b>"))
        self.current_task_modules_layout = QVBoxLayout()
        self.current_task_modules_layout.addStretch(1) # For dynamic adding of module info
        modules_scroll_area = QScrollArea()
        modules_scroll_area.setWidgetResizable(True)
        modules_content_widget = QWidget()
        modules_content_widget.setLayout(self.current_task_modules_layout)
        modules_scroll_area.setWidget(modules_content_widget)
        modules_scroll_area.setMinimumHeight(150)
        right_pane.addWidget(modules_scroll_area)


        # Task Control Buttons
        control_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Task")
        self.start_button.clicked.connect(self._start_task)
        self.pause_button = QPushButton("Pause Task")
        self.pause_button.clicked.connect(self._pause_task)
        self.finish_button = QPushButton("Finish Task")
        self.finish_button.clicked.connect(self._finish_task)

        control_buttons_layout.addWidget(self.start_button)
        control_buttons_layout.addWidget(self.pause_button)
        control_buttons_layout.addWidget(self.finish_button)
        right_pane.addLayout(control_buttons_layout)

        right_pane.addStretch(1) # Push content to top
        main_layout.addLayout(right_pane, 2) # Give right pane 2 units of stretch

        self._update_button_states() # Initialize button states

        self.setStyleSheet("""
            QWidget#TaskPage { /* Style the TaskPage itself */
                background-color: #e0e0e0;
            }
            QLabel {
                font-family: "Inter", sans-serif;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
                transition: background-color 0.3s ease, transform 0.1s ease;
            }
            QPushButton:hover {
                background-color: #45a049;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #39843c;
                transform: translateY(1px);
                box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
                box-shadow: none;
            }
            QListView {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
                font-size: 15px;
            }
            QListView::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListView::item:selected {
                background-color: #a0d0ff;
                color: black;
            }
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        self.setObjectName("TaskPage") # Set object name for styling

    def load_initial_current_task(self, initial_index: int):
        """Sets the initial current task based on loaded state."""
        if initial_index != -1 and 0 <= initial_index < self.task_model.rowCount():
            index = self.task_model.index(initial_index, 0)
            self.task_list_view.setCurrentIndex(index)
            self._on_task_selection_changed(index, QModelIndex()) # Manually trigger update

    def _update_button_states(self):
        """Enables/disables buttons based on current task selection and status."""
        is_task_selected = self.current_task is not None
        self.edit_task_button.setEnabled(is_task_selected)
        self.delete_task_button.setEnabled(is_task_selected)

        if not is_task_selected:
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.finish_button.setEnabled(False)
        else:
            self.start_button.setEnabled(self.current_task.status in ["Idle", "Paused", "Finished"])
            self.pause_button.setEnabled(self.current_task.status == "Running")
            self.finish_button.setEnabled(self.current_task.status in ["Running", "Paused"])

        # Emit signal to inform MainWindow about state changes
        self.task_status_changed.emit(self.current_task)
        self.task_selection_changed.emit(self.current_task)


    @Slot(QModelIndex, QModelIndex)
    def _on_task_selection_changed(self, current_index: QModelIndex, previous_index: QModelIndex):
        """Updates the right pane when a task is selected."""
        self.current_task = self.task_model.get_task_at_index(current_index)
        self._update_current_task_display()
        self._update_button_states()

    @Slot(QModelIndex, QModelIndex, list)
    def _on_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        """Slot to react to changes in the underlying TaskListModel."""
        # If the changed data includes the current task, refresh its display
        if self.current_task:
            current_task_row = self.task_model.get_task_index(self.current_task)
            if top_left.row() <= current_task_row <= bottom_right.row():
                if Qt.DisplayRole in roles or Qt.ForegroundRole in roles:
                    self._update_current_task_display()
                    self._update_button_states() # Status change might affect button states


    def _update_current_task_display(self):
        """Updates the labels and module list in the right pane."""
        # Clear existing module widgets
        for i in reversed(range(self.current_task_modules_layout.count() - 1)): # Exclude stretch item
            widget = self.current_task_modules_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if self.current_task:
            self.current_task_name_label.setText(self.current_task.name)
            self.current_task_description_label.setText(self.current_task.description)
            self.current_task_status_label.setText(f"Status: {self.current_task.status}")

            if not self.current_task.modules:
                self.current_task_modules_layout.insertWidget(0, QLabel("No modules defined for this task."))
            else:
                for i, module in enumerate(self.current_task.modules):
                    module_info_label = QLabel(f"  - <b>{module.name}</b> (Delay: {module.settings.get('delay_ms', 'N/A')}ms)")
                    module_info_label.setWordWrap(True)
                    self.current_task_modules_layout.insertWidget(i, module_info_label)
        else:
            self.current_task_name_label.setText("No task selected")
            self.current_task_description_label.setText("")
            self.current_task_status_label.setText("Status: Idle")
            self.current_task_modules_layout.insertWidget(0, QLabel("Select a task to view its details."))

    @Slot()
    def _create_new_task(self):
        """Opens a dialog to create a new task."""
        dialog = TaskEditorDialog(parent=self)
        dialog.task_saved.connect(self._add_or_update_task)
        dialog.exec()

    @Slot()
    def _edit_selected_task(self):
        """Opens a dialog to edit the currently selected task."""
        selected_index = self.task_list_view.currentIndex()
        if selected_index.isValid():
            task_to_edit = self.task_model.get_task_at_index(selected_index)
            if task_to_edit:
                dialog = TaskEditorDialog(existing_task=task_to_edit, parent=self)
                dialog.task_saved.connect(lambda new_task: self._add_or_update_task(new_task, task_to_edit))
                dialog.exec()
        else:
            QMessageBox.information(self, "No Task Selected", "Please select a task to edit.")

    @Slot(Task, Task)
    def _add_or_update_task(self, new_task_data: Task, old_task_data: Task = None):
        """Adds a new task or updates an existing one in the model."""
        if old_task_data:
            # This is an update operation
            self.task_model.update_task(old_task_data, new_task_data)
            # If the updated task is the currently selected one, refresh display
            if self.current_task == old_task_data:
                self.current_task = new_task_data # Update reference
                self._update_current_task_display()
        else:
            # This is a new task operation
            self.task_model.add_task(new_task_data)
            # Select the newly created task
            new_index = self.task_model.index(self.task_model.rowCount() - 1, 0)
            self.task_list_view.setCurrentIndex(new_index)
            self._on_task_selection_changed(new_index, QModelIndex()) # Manually trigger selection change

    @Slot()
    def _delete_selected_task(self):
        """Deletes the currently selected task."""
        selected_index = self.task_list_view.currentIndex()
        if selected_index.isValid():
            task_name = self.task_model.get_task_at_index(selected_index).name
            reply = QMessageBox.question(self, "Delete Task",
                                         f"Are you sure you want to delete task '{task_name}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.task_model.remove_task(selected_index):
                    # If the deleted task was the current one, clear current task display
                    if self.current_task and self.task_model.get_task_index(self.current_task) == -1:
                        self.current_task = None
                        # No need to explicitly set current_task_index as it's managed by selection model
                        self._update_current_task_display()
                    self._update_button_states()
        else:
            QMessageBox.information(self, "No Task Selected", "Please select a task to delete.")

    # --- Task Control Logic (Simulated) ---
    @Slot()
    def _start_task(self):
        if self.current_task:
            if self.current_task.status in ["Idle", "Paused", "Finished"]:
                self.current_task.status = "Running"
                self._update_current_task_display()
                self.task_model.refresh_task_status(self.current_task)
                self._update_button_states()
                QMessageBox.information(self, "Task Control", f"Task '{self.current_task.name}' started.")
                # Here you would emit a signal to your backend:
                # self.backend_controller.start_task.emit(self.current_task)
            else:
                QMessageBox.warning(self, "Task Control", f"Task '{self.current_task.name}' is already running.")
        else:
            QMessageBox.information(self, "Task Control", "No task selected to start.")

    @Slot()
    def _pause_task(self):
        if self.current_task:
            if self.current_task.status == "Running":
                self.current_task.status = "Paused"
                self._update_current_task_display()
                self.task_model.refresh_task_status(self.current_task)
                self._update_button_states()
                QMessageBox.information(self, "Task Control", f"Task '{self.current_task.name}' paused.")
                # Here you would emit a signal to your backend:
                # self.backend_controller.pause_task.emit(self.current_task)
            else:
                QMessageBox.warning(self, "Task Control", f"Task '{self.current_task.name}' is not running.")
        else:
            QMessageBox.information(self, "Task Control", "No task selected to pause.")

    @Slot()
    def _finish_task(self):
        if self.current_task:
            if self.current_task.status in ["Running", "Paused"]:
                self.current_task.status = "Finished"
                self._update_current_task_display()
                self.task_model.refresh_task_status(self.current_task)
                self._update_button_states()
                QMessageBox.information(self, "Task Control", f"Task '{self.current_task.name}' finished.")
                # Here you would emit a signal to your backend:
                # self.backend_controller.finish_task.emit(self.current_task)
            else:
                QMessageBox.warning(self, "Task Control", f"Task '{self.current_task.name}' is already finished or idle.")
        else:
            QMessageBox.information(self, "Task Control", "No task selected to finish.")


class OtherPage(QWidget):
    """A placeholder page for other application features."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("<h2>Other Application Features</h2>"
                       "<p>This is a placeholder for other functionalities of your device controller.</p>"
                       "<p>You can add graphs, real-time data displays, calibration tools, etc., here.</p>")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch(1) # Push content to top

        self.setStyleSheet("""
            QWidget#OtherPage {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
            QLabel {
                color: #555;
                font-size: 16px;
            }
            h2 {
                color: #007bff;
            }
        """)
        self.setObjectName("OtherPage") # Set object name for styling


# --- Main Window ---

class MainWindow(QMainWindow):
    """Main application window for the scientific device controller."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scientific Device Controller")
        self.setGeometry(100, 100, 1000, 700) # Initial window size

        self.state_manager = StateManager()
        self.tasks, self.current_task_index = self.state_manager.load_state()

        self.task_model = TaskListModel(self.tasks)

        # Initialize menu action references to None before _create_menubar is called
        self.menu_new_task_action = None
        self.menu_save_state_action = None
        self.menu_start_action = None
        self.menu_pause_action = None
        self.menu_finish_action = None
        self.menu_edit_task_action = None
        self.menu_delete_task_action = None

        self.init_ui()
        self.task_page.load_initial_current_task(self.current_task_index)

        # Connect application about to quit signal for state saving
        QApplication.instance().aboutToQuit.connect(self._save_app_state)

    def init_ui(self):
        # --- Menubar Setup ---
        self._create_menubar()

        # --- Central Widget: QStackedWidget ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create pages
        self.task_page = TaskPage(self.task_model)
        self.other_page = OtherPage()

        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.task_page) # Index 0
        self.stacked_widget.addWidget(self.other_page) # Index 1

        # Connect signals from TaskPage to update MainWindow's menu actions
        self.task_page.task_status_changed.connect(self._update_menu_action_states)
        self.task_page.task_selection_changed.connect(self._update_menu_action_states)

        # Initial update of menu actions
        # Call with the current task from the task_page (which might be None initially)
        self._update_menu_action_states(self.task_page.current_task)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #e0e0e0;
            }
            QMenuBar {
                background-color: #d0d0d0;
                border-bottom: 1px solid #b0b0b0;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #c0c0c0;
            }
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 10px;
            }
            QMenu::item:selected {
                background-color: #a0d0ff;
            }
            QStackedWidget {
                border: none; /* No border for the stacked widget itself */
            }
        """)

    def _create_menubar(self):
        """Creates and populates the application menubar."""
        menubar = self.menuBar()

        # --- File Menu ---
        file_menu = menubar.addMenu("&File") # &F creates an Alt+F shortcut

        # New Task Action (delegated to task_page)
        self.menu_new_task_action = QAction(QIcon.fromTheme("document-new", QIcon()), "&New Task...", self)
        self.menu_new_task_action.setToolTip("Create a new scientific task")
        self.menu_new_task_action.setShortcut(Qt.CTRL | Qt.Key_N) # Ctrl+N shortcut
        self.menu_new_task_action.triggered.connect(self._create_new_task_from_menu) # Connect to a new slot
        file_menu.addAction(self.menu_new_task_action)

        # Save State Action
        self.menu_save_state_action = QAction(QIcon.fromTheme("document-save", QIcon()), "&Save State", self)
        self.menu_save_state_action.setToolTip("Save the current application state")
        self.menu_save_state_action.setShortcut(Qt.CTRL | Qt.Key_S) # Ctrl+S shortcut
        self.menu_save_state_action.triggered.connect(self._save_app_state)
        file_menu.addAction(self.menu_save_state_action)

        file_menu.addSeparator()

        # Exit Action
        exit_action = QAction(QIcon.fromTheme("application-exit", QIcon()), "E&xit", self)
        exit_action.setToolTip("Exit the application")
        exit_action.setShortcut(Qt.ALT | Qt.Key_F4) # Alt+F4 shortcut
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Task Menu ---
        task_menu = menubar.addMenu("&Task") # &T creates an Alt+T shortcut

        # Start Task Action
        self.menu_start_action = QAction(QIcon.fromTheme("media-playback-start", QIcon()), "&Start Task", self)
        self.menu_start_action.setToolTip("Start the selected task")
        self.menu_start_action.setShortcut(Qt.Key_F5) # F5 shortcut
        self.menu_start_action.triggered.connect(self._start_task_from_menu)
        task_menu.addAction(self.menu_start_action)

        # Pause Task Action
        self.menu_pause_action = QAction(QIcon.fromTheme("media-playback-pause", QIcon()), "&Pause Task", self)
        self.menu_pause_action.setToolTip("Pause the running task")
        self.menu_pause_action.setShortcut(Qt.Key_F6) # F6 shortcut
        self.menu_pause_action.triggered.connect(self._pause_task_from_menu)
        task_menu.addAction(self.menu_pause_action)

        # Finish Task Action
        self.menu_finish_action = QAction(QIcon.fromTheme("media-playback-stop", QIcon()), "&Finish Task", self)
        self.menu_finish_action.setToolTip("Finish the current task")
        self.menu_finish_action.setShortcut(Qt.Key_F7) # F7 shortcut
        self.menu_finish_action.triggered.connect(self._finish_task_from_menu)
        task_menu.addAction(self.menu_finish_action)

        task_menu.addSeparator()

        # Edit Task Action
        self.menu_edit_task_action = QAction(QIcon.fromTheme("document-edit", QIcon()), "&Edit Selected Task...", self)
        self.menu_edit_task_action.setToolTip("Edit the details of the currently selected task")
        self.menu_edit_task_action.setShortcut(Qt.CTRL | Qt.Key_E)
        self.menu_edit_task_action.triggered.connect(self._edit_selected_task_from_menu)
        task_menu.addAction(self.menu_edit_task_action)

        # Delete Task Action
        self.menu_delete_task_action = QAction(QIcon.fromTheme("edit-delete", QIcon()), "&Delete Selected Task", self)
        self.menu_delete_task_action.setToolTip("Delete the currently selected task")
        self.menu_delete_task_action.setShortcut(Qt.Key_Delete)
        self.menu_delete_task_action.triggered.connect(self._delete_selected_task_from_menu)
        task_menu.addAction(self.menu_delete_task_action)

        # --- View Menu (New) ---
        view_menu = menubar.addMenu("&View")

        self.action_show_tasks = QAction("Show &Tasks", self)
        self.action_show_tasks.setCheckable(True)
        self.action_show_tasks.setChecked(True) # Tasks page is initially visible
        self.action_show_tasks.setShortcut(Qt.CTRL | Qt.Key_1)
        self.action_show_tasks.triggered.connect(lambda: self._show_page(0))
        view_menu.addAction(self.action_show_tasks)

        self.action_show_other = QAction("Show &Other Features", self)
        self.action_show_other.setCheckable(True)
        self.action_show_other.setChecked(False)
        self.action_show_other.setShortcut(Qt.CTRL | Qt.Key_2)
        self.action_show_other.triggered.connect(lambda: self._show_page(1))
        view_menu.addAction(self.action_show_other)

        # Ensure only one view action is checked at a time
        self.action_show_tasks.toggled.connect(lambda checked: self.action_show_other.setChecked(not checked) if checked else None)
        self.action_show_other.toggled.connect(lambda checked: self.action_show_tasks.setChecked(not checked) if checked else None)


    @Slot(int)
    def _show_page(self, index: int):
        """Switches the currently visible page in the stacked widget."""
        self.stacked_widget.setCurrentIndex(index)
        # Update menu action states when page changes, as task actions might become irrelevant
        self._update_menu_action_states(self.task_page.current_task)


    @Slot(Task)
    def _update_menu_action_states(self, current_task: Task | None):
        """Enables/disables menubar actions based on current task selection and status, and active page."""
        # Only enable task-related actions if the TaskPage is currently visible
        is_task_page_active = self.stacked_widget.currentWidget() == self.task_page

        # Use bool() to ensure a strict boolean is passed to setEnabled
        self.menu_start_action.setEnabled(
            bool(is_task_page_active and current_task and current_task.status in ["Idle", "Paused", "Finished"])
        )
        self.menu_pause_action.setEnabled(
            bool(is_task_page_active and current_task and current_task.status == "Running")
        )
        self.menu_finish_action.setEnabled(
            bool(is_task_page_active and current_task and current_task.status in ["Running", "Paused"])
        )
        self.menu_edit_task_action.setEnabled(
            bool(is_task_page_active and current_task is not None)
        )
        self.menu_delete_task_action.setEnabled(
            bool(is_task_page_active and current_task is not None)
        )

        # The 'New Task' action can be enabled even if no task is selected, but still only on task page
        self.menu_new_task_action.setEnabled(is_task_page_active)


    # --- Menu Action Slots (delegating to TaskPage) ---
    @Slot()
    def _create_new_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._create_new_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to create a new task.")

    @Slot()
    def _edit_selected_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._edit_selected_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to edit a task.")

    @Slot()
    def _delete_selected_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._delete_selected_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to delete a task.")

    @Slot()
    def _start_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._start_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to start a task.")

    @Slot()
    def _pause_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._pause_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to pause a task.")

    @Slot()
    def _finish_task_from_menu(self):
        if self.stacked_widget.currentWidget() == self.task_page:
            self.task_page._finish_task()
        else:
            QMessageBox.information(self, "Action Not Available", "Please switch to the 'Tasks' page to finish a task.")


    def _save_app_state(self):
        """Called when the application is about to quit to save the state, or manually from menubar."""
        all_tasks = self.task_model.get_all_tasks()
        # Get current task index from TaskPage's current selection
        current_task_idx = self.task_page.task_model.get_task_index(self.task_page.current_task) if self.task_page.current_task else -1
        self.state_manager.save_state(all_tasks, current_task_idx)
        QMessageBox.information(self, "Save State", "Application state saved successfully.")


# --- Application Entry Point ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

