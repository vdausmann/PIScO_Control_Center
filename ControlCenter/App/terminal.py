from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit, QScrollBar
import re

ANSI_COLORS = {
    "30": "black", "31": "red", "32": "green", "33": "yellow",
    "34": "blue", "35": "magenta", "36": "cyan", "37": "white",
    "90": "darkgray", "91": "lightcoral", "92": "lightgreen", "93": "lightyellow",
    "94": "lightblue", "95": "violet", "96": "lightcyan", "97": "white"
}

def ansi_to_html(text):
    """
    Converts ANSI color escape sequences to HTML spans with CSS styles.
    """
    def replace_ansi(match):
        codes = match.group(1).split(";")  # Extract ANSI codes
        color = "white"  # Default color

        for code in codes:
            if code in ANSI_COLORS:
                color = ANSI_COLORS[code]

        return f'<span style="color:{color};">'

    # Remove reset sequences
    text = re.sub(r'\033\[0m', '</span>', text)

    # Convert ANSI color codes to HTML
    text = re.sub(r'\033\[([0-9;]+)m', replace_ansi, text)

    return text

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

        self.output_lines = []

    def process_input(self):
        input_text = self.input.text()
        try:
            self.commands[input_text]()
        except KeyError:
            self.output.append(f'<font color="red">Command "{input_text}" not found. See all available commands with "help".</font>')
        self.input.clear()

    def print(self, text: str, ansi: bool=False, replace_last: bool=False):
        if ansi:
            text = ansi_to_html(text)
        if replace_last:
            self.output_lines[-1] = text
            self.output.setHtml("<br>".join(self.output_lines))
        else:
            self.output_lines.append(text)
            self.output.setHtml("<br>".join(self.output_lines))
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def clear_output(self):
        self.output.clear()

    def help(self):
        self.output.append(f'<font color="{self.app.color_settings["text_color"]}">Available commands:</font>')
        for command in self.commands:
            self.output.append(f'    {command}: {self.documentation[command]}')

    def doc(self):
        self.print("Documentation of App:\n")
        self.print("The values of the settings can be viewed by clicking on the labels.")
