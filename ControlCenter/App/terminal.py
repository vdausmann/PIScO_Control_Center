from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit

class Terminal(QWidget):
    input: QLineEdit
    output: QTextEdit


    def __init__(self, app, parent):
        super().__init__(parent=parent)
        self.app = app

        layout = QVBoxLayout(self)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.process_input)

        layout.addWidget(self.output)
        layout.addWidget(self.input)

        self.setLayout(layout)

        self.commands = {"clear": self.clear_output, "help": self.help, "doc": self.doc}
        self.documentation = {"clear": "Clears the output", "help": "Displays available commands", "doc": "Short documentation of App"}

        self.setStyleSheet(f"background-color: {self.app.color_settings['terminal_color']};")

    def process_input(self):
        input_text = self.input.text()
        try:
            self.commands[input_text]()
        except KeyError:
            self.output.append(f'<font color="red">Command "{input_text}" not found. See all available commands with "help".</font>')
        self.input.clear()

    def print(self, text: str):
        self.output.append(text)

    def clear_output(self):
        self.output.clear()

    def help(self):
        self.output.append(f'<font color="{self.app.color_settings["text_color"]}">Available commands:</font>')
        for command in self.commands:
            self.output.append(f'    {command}: {self.documentation[command]}')

    def doc(self):
        self.print("Documentation of App:\n")
        self.print("The values of the settings can be viewed by clicking on the labels.")
