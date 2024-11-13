from enum import Enum
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore

from interface.session.models.data_model import CalibrationDataPoint

from assets.assets import data_card_delete


class CalibrationDataCardType(Enum):
    FOCUS = 0
    ZOOM = 1
    IMAGE = 2

class CalibrationDataCardStatus(Enum):
    LOADED = 0
    COLLECTED = 1
    CALCULATED = 2

SELECTED_STYLE = "background-color: rgba(226,234,246,30); border-top-left-radius: 0px; border-bottom-left-radius: 0px;"
WARNING_STYLE = "border: 1px solid rgb(255, 165, 0);"

# class CalibrationDataCard
class CalibrationDataCard(QWidget):
    # pyqtSignal to emit when the delete button is clicked
    delete_clicked = QtCore.pyqtSignal(QWidget, name="deleteDataPointClicked")
    label_clicked = QtCore.pyqtSignal(QWidget, name="labelDataPointClicked")

    def __init__(self, data: CalibrationDataPoint, card_type: CalibrationDataCardType, status: CalibrationDataCardStatus = CalibrationDataCardStatus.LOADED):
        super().__init__()
        self.data = data
        self.card_type = card_type
        self.status = status
        self.label_style = ""
        self.setupUi()
        self.connectSignalsSlots()

    # override equals method to compare data points
    def __eq__(self, other):
        return self.data == other.data

    def setupUi(self):
        if self.card_type == CalibrationDataCardType.FOCUS:
            self.label = QLabel(f"{self.data.get_focus()}")
        elif self.card_type == CalibrationDataCardType.ZOOM:
            self.label = QLabel(f"{self.data.get_zoom()}")
        elif self.card_type == CalibrationDataCardType.IMAGE:
            self.label = QLabel(f"{self.data.get_image()}")

        self.setMinimumHeight(28)
        self.setMaximumHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create status sliver
        status_sliver = QLabel()
        status_sliver.setMaximumWidth(8)
        if self.status == CalibrationDataCardStatus.LOADED:
            status_sliver.setStyleSheet("background-color: rgb(255, 127, 0); width: 5px;")
        elif self.status == CalibrationDataCardStatus.COLLECTED:
            status_sliver.setStyleSheet("background-color: rgb(131, 70, 161); width: 5px;")
        elif self.status == CalibrationDataCardStatus.CALCULATED:
            status_sliver.setStyleSheet("background-color: rgb(0, 70, 22); width: 5px;")
        self.layout.addWidget(status_sliver)

        # Create label
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Create icon button
        if self.card_type == CalibrationDataCardType.IMAGE:
            self.delete_button = QPushButton()
            self.delete_button.setIcon(QIcon(data_card_delete))
            self.delete_button.setStyleSheet("background-color: none; border: none;")
            self.delete_button.setFixedSize(25, 25)
            self.layout.addWidget(self.delete_button)

    def setSelected(self, selected: bool):
        if selected:
            self.label_style = self.label_style + SELECTED_STYLE
            self.label.setStyleSheet(self.label_style)
        else:
            self.label_style = self.label_style.replace(SELECTED_STYLE, "")
            self.label.setStyleSheet(self.label_style)

    def setWarning(self, warning: bool):
        if warning:
            self.label_style += WARNING_STYLE
            self.label.setStyleSheet(self.label_style)
        else:
            self.label_style = self.label_style.replace(WARNING_STYLE, "")
            self.label.setStyleSheet(self.label_style)

    def connectSignalsSlots(self):
        if self.card_type == CalibrationDataCardType.IMAGE:
            self.delete_button.clicked.connect(self._deleteButtonClicked)
    
    def mousePressEvent(self, event):
        self.label_clicked.emit(self)

    def _deleteButtonClicked(self):
        self.delete_clicked.emit(self)

    def getData(self) -> CalibrationDataPoint:
        return self.data
