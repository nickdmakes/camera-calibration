from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QObject
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QFont

from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.calibration_command.data_browser.calibration_data_card import CalibrationDataCard, CalibrationDataCardType, CalibrationDataCardStatus
from interface.session.models.data_model import CalibrationDataPoint
from interface.session.calibration_session import CalibrationSession
from interface.calibration_command.ui.capture_preview import CapturePreview

from assets.assets import db_loaded, db_collected, db_calculated

from calibration.camera_calibration_api import paint_corner_image, get_calibration_matrix_values


class CalibrationDataBrowserController(QObject):
    # Called when the session data is added or removed
    browser_data_changed = QtCore.pyqtSignal(name="SessionDataChanged")

    def __init__(self, mw: MainWindow, session: CalibrationSession):
        super().__init__()
        self.mw = mw
        self.session = session
        self.capture_preview = CapturePreview(main_window=self.mw)
        self.fc = mw.SA_CalibrationFocusScrollArea
        self.zc = mw.SA_CalibrationZoomScrollArea
        self.ic = mw.SA_CalibrationImageScrollArea
        self.selected_focus = None
        self.selected_zoom = None
        self.selected_image = None
        self.reprojection_error_threshold = 1.0 # TODO: make this a user setting
        self.setupUi()

    def setupUi(self):
        focus_scroll_widget = QWidget()
        focus_scroll_widget.setLayout(QVBoxLayout())
        focus_scroll_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        focus_scroll_widget.layout().setContentsMargins(0, 0, 0, 0)
        focus_scroll_widget.layout().setSpacing(0)
        self.fc.setWidgetResizable(True)
        self.fc.setWidget(focus_scroll_widget)

        zoom_scroll_widget = QWidget()
        zoom_scroll_widget.setLayout(QVBoxLayout())
        zoom_scroll_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        zoom_scroll_widget.layout().setContentsMargins(0, 0, 0, 0)
        zoom_scroll_widget.layout().setSpacing(0)
        self.zc.setWidgetResizable(True)
        self.zc.setWidget(zoom_scroll_widget)

        image_scroll_widget = QWidget()
        image_scroll_widget.setLayout(QVBoxLayout())
        image_scroll_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        image_scroll_widget.layout().setContentsMargins(0, 0, 0, 0)
        image_scroll_widget.layout().setSpacing(0)
        self.ic.setWidgetResizable(True)
        self.ic.setWidget(image_scroll_widget)

        # Data Preview
        self.mw.L_DataPreviewFocusValueLabel.setText("NA")
        self.mw.L_DataPreviewZoomValueLabel.setText("NA")
        self.mw.L_DataPreviewImageValueLabel.setText("NA")

        # insert at second to last index
        self.mw.C_DataBrowserInfoColumn.insertWidget(2, self.capture_preview)
        self.mw.L_CalibrationFocusDataLabel.setStyleSheet("background-color: #333")
        self.mw.L_CalibrationZoomDataLabel.setStyleSheet("background-color: #333")
        self.mw.L_CalibrationImageDataLabel.setStyleSheet("background-color: #333")

        self.mw.L_LoadedPlaceHolderOrange.setPixmap(QPixmap(db_loaded))
        self.mw.L_GatheredPlaceholderPurple.setPixmap(QPixmap(db_collected))
        self.mw.L_CalibratedPlaceHolderGreen.setPixmap(QPixmap(db_calculated))

    def updateBrowser(self):
        self.removeFocusCards()
        self.removeZoomCards()
        self.removeImageCards()
        self.selected_focus = None
        self.selected_zoom = None
        self.selected_image = None
        self.updateFocusCards()
        self.updateZoomCards()
        self.updateImageCards()

    def clearModelAndPreloadData(self, focus_points: list, zoom_points: list, num_images: int):
        self.session.data.delete_all_nodes()
        for focus in focus_points:
            for zoom in zoom_points:
                for i in range(num_images):
                    image_node = CalibrationDataPoint(float(focus), float(zoom), f"image-{i}", None, None, None)
                    self.session.data.add_image_node(image_node)
        self.updateBrowser()
        self.session.data_updated.emit()

    def addData(self, data: CalibrationDataPoint):
        self.session.data.add_image_node(data)
        self.updateFocusCards()
        self.updateZoomCards()
        self.updateImageCards()
        self.session.data_updated.emit()

    def deleteData(self, id: str):
        self.session.data.delete_node(id)
        self.updateFocusCards()
        self.updateZoomCards()
        self.updateImageCards()
        self.session.data_updated.emit()

    def isFullyCollected(self):
        for focus_node in self.session.data.get_all_focus_nodes():
            for zoom_node in self.session.data.get_zoom_nodes_from_id(focus_node.get_focus_id()):
                for image_node in self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id()):
                    if image_node.corner_payload is None:
                        return False
        return True
                
    def removeFocusCards(self):
        for i in reversed(range(self.fc.widget().layout().count())): 
            self.fc.widget().layout().itemAt(i).widget().deleteLater()

    def updateFocusCards(self):
        self.removeFocusCards()
        for focus_node in self.session.data.get_all_focus_nodes():
            status = self.getFocusCardStatus(focus_node)
            focus_card = CalibrationDataCard(focus_node, CalibrationDataCardType.FOCUS, status=status)
            if self.selected_focus is not None and self.selected_focus == focus_card:
                self.selected_focus = focus_card
                focus_card.setSelected(True)
            self.fc.widget().layout().addWidget(focus_card)
            focus_card.label_clicked.connect(self._onFocusCardClicked)
            # set warning if any of the images under this focus node has high reprojection error
            for zoom_node in self.session.data.get_zoom_nodes_from_id(focus_node.get_focus_id()):
                for image_node in self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id()):
                    if self._isReprojectionErrorHigh(image_node, self.reprojection_error_threshold):
                        focus_card.setWarning(True)

    def getFocusCardStatus(self, focus_node: CalibrationDataPoint) -> CalibrationDataCardStatus:
        all_calculated = True
        all_collected = True
        for zoom_node in self.session.data.get_zoom_nodes_from_id(focus_node.get_focus_id()):
            for image_node in self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id()):
                if image_node.calibration_payload is None:
                    all_calculated = False
                if image_node.corner_payload is None:
                    all_collected = False
        if all_calculated:
            return CalibrationDataCardStatus.CALCULATED
        elif all_collected:
            return CalibrationDataCardStatus.COLLECTED
        else:
            return CalibrationDataCardStatus.LOADED

    def removeZoomCards(self):
        for i in reversed(range(self.zc.widget().layout().count())): 
            self.zc.widget().layout().itemAt(i).widget().deleteLater()

    def updateZoomCards(self):
        if self.selected_focus is None:
            return
        self.removeZoomCards()
        focus_id = self.selected_focus.getData().get_focus_id()
        for zoom_node in self.session.data.get_zoom_nodes_from_id(focus_id):
            status = self.getZoomCardStatus(zoom_node)
            zoom_card = CalibrationDataCard(zoom_node, CalibrationDataCardType.ZOOM, status=status)
            if self.selected_zoom is not None and self.selected_zoom == zoom_card:
                self.selected_zoom = zoom_card
                zoom_card.setSelected(True)
            self.zc.widget().layout().addWidget(zoom_card)
            zoom_card.label_clicked.connect(self._onZoomCardClicked)
            # set warning if any of the images under this zoom node has high reprojection error
            for image_node in self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id()):
                if self._isReprojectionErrorHigh(image_node, self.reprojection_error_threshold):
                    zoom_card.setWarning(True)
                    return
                
    def getZoomCardStatus(self, zoom_node: CalibrationDataPoint) -> CalibrationDataCardStatus:
        if len(self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id())) == 0:
            return CalibrationDataCardStatus.LOADED
        all_calculated = True
        all_collected = True
        for image_node in self.session.data.get_image_nodes_from_id(zoom_node.get_zoom_id()):
            if image_node.calibration_payload is None:
                all_calculated = False
            if image_node.corner_payload is None:
                all_collected = False
        if all_calculated:
            return CalibrationDataCardStatus.CALCULATED
        elif all_collected:
            return CalibrationDataCardStatus.COLLECTED
        else:
            return CalibrationDataCardStatus.LOADED

    def removeImageCards(self):
        for i in reversed(range(self.ic.widget().layout().count())):
            self.ic.widget().layout().itemAt(i).widget().deleteLater()

    def updateImageCards(self):
        if self.selected_zoom is None:
            return
        self.removeImageCards()
        zoom_id = self.selected_zoom.getData().get_zoom_id()
        for image_node in self.session.data.get_image_nodes_from_id(zoom_id):
            status = self.getImageCardStatus(image_node)
            image_card = CalibrationDataCard(image_node, CalibrationDataCardType.IMAGE, status=status)
            if self.selected_image is not None and self.selected_image == image_card:
                self.selected_image = image_card
                image_card.setSelected(True)
            self.ic.widget().layout().addWidget(image_card)
            image_card.label_clicked.connect(self._onImageCardClicked)
            image_card.delete_clicked.connect(self._onImageCardDelete)
            # If image has high reprojection error, set warning
            if self._isReprojectionErrorHigh(image_node, self.reprojection_error_threshold):
                image_card.setWarning(True)      

    def getImageCardStatus(self, image_node: CalibrationDataPoint) -> CalibrationDataCardStatus:
        if image_node.calibration_payload is not None:
            return CalibrationDataCardStatus.CALCULATED
        elif image_node.corner_payload is not None:
            return CalibrationDataCardStatus.COLLECTED
        else:
            return CalibrationDataCardStatus.LOADED   

    def _onFocusCardClicked(self, card: CalibrationDataCard):
        if self.selected_image is not None:
            self.selected_image.setSelected(False)
            self.selected_image = None
        self.removeImageCards()
        if self.selected_zoom is not None:
            self.selected_zoom.setSelected(False)
            self.selected_zoom = None
        self.removeZoomCards()
        if self.selected_focus is None:
            self.selected_focus = card
        self.selected_focus.setSelected(False)
        self.selected_focus = card
        self.selected_focus.setSelected(True)
        self.updateZoomCards()
        self.updateDataPreview()

    def _onFocusCardDelete(self, card: CalibrationDataCard):
        if self.selected_focus is not None and self.selected_focus.data.get_focus_id() == card.data.get_focus_id():
            self.selected_focus.setSelected(False)
            self.selected_focus = None
            self.removeZoomCards()
            self.removeImageCards()
        if self.selected_zoom is not None:
            self.selected_zoom.setSelected(False)
            self.selected_zoom = None
        if self.selected_image is not None:
            self.selected_image.setSelected(False)
            self.selected_image = None
        self.deleteData(card.getData().get_focus_id())
        self.updateDataPreview()

    def _onZoomCardClicked(self, card: CalibrationDataCard):
        if self.selected_image is not None:
            self.selected_image.setSelected(False)
            self.selected_image = None
        self.removeImageCards()
        if self.selected_zoom is None:
            self.selected_zoom = card
        self.selected_zoom.setSelected(False)
        self.selected_zoom = card
        self.selected_zoom.setSelected(True)
        self.updateImageCards()
        self.updateDataPreview()

    def _onZoomCardDelete(self, card: CalibrationDataCard):
        if self.selected_zoom is not None and self.selected_zoom.data.get_zoom_id() == card.data.get_zoom_id():
            self.selected_zoom.setSelected(False)
            self.selected_zoom = None
            self.removeImageCards()
        if self.selected_image is not None:
            self.selected_image.setSelected(False)
            self.selected_image = None
        self.deleteData(card.getData().get_zoom_id())
        # If last zoom node under the focus node, remove the focus node
        if len(self.session.data.get_zoom_nodes_from_id(card.getData().get_focus_id())) == 0:
            self._onFocusCardDelete(card)
        self.updateDataPreview()

    def _onImageCardClicked(self, card: CalibrationDataCard):
        if card.data.image_data is not None:
            c_image = paint_corner_image(card.data.image_data, card.data.corner_payload.pattern_size, card.data.corner_payload.image_points)
            self.capture_preview.set_frame(c_image)
        else:
            self.capture_preview.reset_frame()

        if self.selected_image is None:
            self.selected_image = card
        elif self.selected_image == card:
            return
        self.selected_image.setSelected(False)
        self.selected_image = card
        self.selected_image.setSelected(True)
        self.updateDataPreview()

    def _onImageCardDelete(self, card: CalibrationDataCard):
        if self.selected_image is not None and self.selected_image == card:
            self.selected_image.setSelected(False)
            self.selected_image = None
            self.capture_preview.reset_frame()
        self.deleteData(card.getData().get_image_id())
        # If last image node under the zoom node, remove the zoom node
        if len(self.session.data.get_image_nodes_from_id(card.getData().get_zoom_id())) == 0:
            self._onZoomCardDelete(card)
        self.updateDataPreview()

    def _isReprojectionErrorHigh(self, data_point: CalibrationDataPoint, threshold: float) -> bool:
        if data_point.calibration_payload is not None:
            return data_point.calibration_payload.reproj_error > threshold
        return False
    
    def updateDataPreview(self):
        if self.selected_image is not None:
            image = self.selected_image.getData()
            self.mw.L_DataPreviewFocusValueLabel.setText(str(image.get_focus()))
            self.mw.L_DataPreviewZoomValueLabel.setText(str(image.get_zoom()))
            self.mw.L_DataPreviewImageValueLabel.setText(str(image.get_image()))
            if image.corner_payload is not None:
                if image.calibration_payload is not None:
                    self._updateDistCoefTable(image.calibration_payload.distortion_coefficients)
                else:
                    self._clearDistCoefTable()
            else:
                self._clearDistCoefTable()
        elif self.selected_zoom is not None:
            zoom = self.selected_zoom.getData()
            self.mw.L_DataPreviewFocusValueLabel.setText(str(zoom.get_focus()))
            self.mw.L_DataPreviewZoomValueLabel.setText(str(zoom.get_zoom()))
            self.mw.L_DataPreviewImageValueLabel.setText("ALL")
            if zoom.calibration_payload is not None:
                self._updateDistCoefTable(zoom.calibration_payload.distortion_coefficients)
            else:
                self._clearDistCoefTable()
        elif self.selected_focus is not None:
            focus = self.selected_focus.getData()
            self.mw.L_DataPreviewFocusValueLabel.setText(str(focus.get_focus()))
            self.mw.L_DataPreviewZoomValueLabel.setText("--")
            self.mw.L_DataPreviewImageValueLabel.setText("--")
            self._clearDistCoefTable()
        else:
            self.mw.L_DataPreviewFocusValueLabel.setText("NA")
            self.mw.L_DataPreviewZoomValueLabel.setText("NA")
            self.mw.L_DataPreviewImageValueLabel.setText("NA")
            self._clearDistCoefTable()

    def _updateDistCoefTable(self, coefs: list) -> None:
        self._clearDistCoefTable()
        for i, coef in enumerate(coefs[0]):
            coef = "{:.2e}".format(float(coef))
            table_item = QTableWidgetItem(str(coef))
            table_item.setFont(QFont("Arial", 8, QFont.Weight.Normal, False))
            table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.mw.TW_DataPreviewDistCoefTable.setItem(0, i, table_item)

    def _clearDistCoefTable(self):
        # remove data from row 0
        self.mw.TW_DataPreviewDistCoefTable.clearContents()
