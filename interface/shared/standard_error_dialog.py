# Standard Error Dialog widget for displaying error messages using QMessageBox

from PyQt6.QtWidgets import QMessageBox

class StandardErrorDialog(QMessageBox):
    def __init__(self, title: str = "", message: str = "", details: str = ""):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(message)
        if details:
            self.setDetailedText(details)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.exec()
