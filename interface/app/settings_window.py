# Form implementation generated from reading ui file '.\settings.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_D_CalibrationSettingsDialog(object):
    def setupUi(self, D_CalibrationSettingsDialog):
        D_CalibrationSettingsDialog.setObjectName("D_CalibrationSettingsDialog")
        D_CalibrationSettingsDialog.resize(450, 474)
        D_CalibrationSettingsDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(D_CalibrationSettingsDialog)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName("verticalLayout")
        self.GB_CameraSettingsGroupBox = QtWidgets.QGroupBox(parent=D_CalibrationSettingsDialog)
        self.GB_CameraSettingsGroupBox.setObjectName("GB_CameraSettingsGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.GB_CameraSettingsGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.R_ImageSizeRow = QtWidgets.QHBoxLayout()
        self.R_ImageSizeRow.setSpacing(0)
        self.R_ImageSizeRow.setObjectName("R_ImageSizeRow")
        self.SB_ImageResTitleLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SB_ImageResTitleLabel.sizePolicy().hasHeightForWidth())
        self.SB_ImageResTitleLabel.setSizePolicy(sizePolicy)
        self.SB_ImageResTitleLabel.setObjectName("SB_ImageResTitleLabel")
        self.R_ImageSizeRow.addWidget(self.SB_ImageResTitleLabel)
        self.SB_ImageResWidthLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        self.SB_ImageResWidthLabel.setObjectName("SB_ImageResWidthLabel")
        self.R_ImageSizeRow.addWidget(self.SB_ImageResWidthLabel)
        self.SB_ImageResWidthValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CameraSettingsGroupBox)
        self.SB_ImageResWidthValueSpinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.SB_ImageResWidthValueSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.SB_ImageResWidthValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_ImageResWidthValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_ImageResWidthValueSpinBox.setMinimum(206)
        self.SB_ImageResWidthValueSpinBox.setMaximum(10000)
        self.SB_ImageResWidthValueSpinBox.setProperty("value", 1920)
        self.SB_ImageResWidthValueSpinBox.setObjectName("SB_ImageResWidthValueSpinBox")
        self.R_ImageSizeRow.addWidget(self.SB_ImageResWidthValueSpinBox)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageSizeRow.addItem(spacerItem)
        self.SB_ImageResHeightLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        self.SB_ImageResHeightLabel.setObjectName("SB_ImageResHeightLabel")
        self.R_ImageSizeRow.addWidget(self.SB_ImageResHeightLabel)
        self.SB_ImageResHeightValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CameraSettingsGroupBox)
        self.SB_ImageResHeightValueSpinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.SB_ImageResHeightValueSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.SB_ImageResHeightValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_ImageResHeightValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_ImageResHeightValueSpinBox.setMinimum(206)
        self.SB_ImageResHeightValueSpinBox.setMaximum(10000)
        self.SB_ImageResHeightValueSpinBox.setProperty("value", 1080)
        self.SB_ImageResHeightValueSpinBox.setObjectName("SB_ImageResHeightValueSpinBox")
        self.R_ImageSizeRow.addWidget(self.SB_ImageResHeightValueSpinBox)
        self.verticalLayout_3.addLayout(self.R_ImageSizeRow)
        self.R_SensorSizeRow = QtWidgets.QHBoxLayout()
        self.R_SensorSizeRow.setSpacing(0)
        self.R_SensorSizeRow.setObjectName("R_SensorSizeRow")
        self.L_SensorSizeTitleLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_SensorSizeTitleLabel.sizePolicy().hasHeightForWidth())
        self.L_SensorSizeTitleLabel.setSizePolicy(sizePolicy)
        self.L_SensorSizeTitleLabel.setObjectName("L_SensorSizeTitleLabel")
        self.R_SensorSizeRow.addWidget(self.L_SensorSizeTitleLabel)
        self.L_SensorSizeWidthLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        self.L_SensorSizeWidthLabel.setObjectName("L_SensorSizeWidthLabel")
        self.R_SensorSizeRow.addWidget(self.L_SensorSizeWidthLabel)
        self.SB_SensorSizeWidthValueSpinBox = QtWidgets.QDoubleSpinBox(parent=self.GB_CameraSettingsGroupBox)
        self.SB_SensorSizeWidthValueSpinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.SB_SensorSizeWidthValueSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.SB_SensorSizeWidthValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_SensorSizeWidthValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_SensorSizeWidthValueSpinBox.setMinimum(0.01)
        self.SB_SensorSizeWidthValueSpinBox.setProperty("value", 36.7)
        self.SB_SensorSizeWidthValueSpinBox.setObjectName("SB_SensorSizeWidthValueSpinBox")
        self.R_SensorSizeRow.addWidget(self.SB_SensorSizeWidthValueSpinBox)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_SensorSizeRow.addItem(spacerItem1)
        self.L_SensorSizeHeightLabel = QtWidgets.QLabel(parent=self.GB_CameraSettingsGroupBox)
        self.L_SensorSizeHeightLabel.setObjectName("L_SensorSizeHeightLabel")
        self.R_SensorSizeRow.addWidget(self.L_SensorSizeHeightLabel)
        self.SB_SensorSizeHeightValueSpinBox = QtWidgets.QDoubleSpinBox(parent=self.GB_CameraSettingsGroupBox)
        self.SB_SensorSizeHeightValueSpinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.SB_SensorSizeHeightValueSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.SB_SensorSizeHeightValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_SensorSizeHeightValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_SensorSizeHeightValueSpinBox.setMinimum(0.01)
        self.SB_SensorSizeHeightValueSpinBox.setProperty("value", 25.54)
        self.SB_SensorSizeHeightValueSpinBox.setObjectName("SB_SensorSizeHeightValueSpinBox")
        self.R_SensorSizeRow.addWidget(self.SB_SensorSizeHeightValueSpinBox)
        self.verticalLayout_3.addLayout(self.R_SensorSizeRow)
        self.verticalLayout.addWidget(self.GB_CameraSettingsGroupBox)
        self.GB_CalibrationSettingsGroupBox = QtWidgets.QGroupBox(parent=D_CalibrationSettingsDialog)
        self.GB_CalibrationSettingsGroupBox.setObjectName("GB_CalibrationSettingsGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.GB_CalibrationSettingsGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.R_ImageCollectionFocusRangeRow = QtWidgets.QHBoxLayout()
        self.R_ImageCollectionFocusRangeRow.setSpacing(0)
        self.R_ImageCollectionFocusRangeRow.setObjectName("R_ImageCollectionFocusRangeRow")
        self.L_FocusRangeTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        self.L_FocusRangeTitleLabel.setObjectName("L_FocusRangeTitleLabel")
        self.R_ImageCollectionFocusRangeRow.addWidget(self.L_FocusRangeTitleLabel)
        self.L_MinFocusDistanceLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_MinFocusDistanceLabel.sizePolicy().hasHeightForWidth())
        self.L_MinFocusDistanceLabel.setSizePolicy(sizePolicy)
        self.L_MinFocusDistanceLabel.setObjectName("L_MinFocusDistanceLabel")
        self.R_ImageCollectionFocusRangeRow.addWidget(self.L_MinFocusDistanceLabel)
        self.SB_MinFocusDistanceSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_MinFocusDistanceSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_MinFocusDistanceSpinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.SB_MinFocusDistanceSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_MinFocusDistanceSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_MinFocusDistanceSpinBox.setMaximum(300)
        self.SB_MinFocusDistanceSpinBox.setProperty("value", 100)
        self.SB_MinFocusDistanceSpinBox.setObjectName("SB_MinFocusDistanceSpinBox")
        self.R_ImageCollectionFocusRangeRow.addWidget(self.SB_MinFocusDistanceSpinBox)
        spacerItem2 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageCollectionFocusRangeRow.addItem(spacerItem2)
        self.L_MaxFocusDistanceLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_MaxFocusDistanceLabel.sizePolicy().hasHeightForWidth())
        self.L_MaxFocusDistanceLabel.setSizePolicy(sizePolicy)
        self.L_MaxFocusDistanceLabel.setObjectName("L_MaxFocusDistanceLabel")
        self.R_ImageCollectionFocusRangeRow.addWidget(self.L_MaxFocusDistanceLabel)
        self.SB_MaxFocusDistanceSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_MaxFocusDistanceSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_MaxFocusDistanceSpinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.SB_MaxFocusDistanceSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_MaxFocusDistanceSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_MaxFocusDistanceSpinBox.setMinimum(300)
        self.SB_MaxFocusDistanceSpinBox.setMaximum(1000)
        self.SB_MaxFocusDistanceSpinBox.setProperty("value", 500)
        self.SB_MaxFocusDistanceSpinBox.setObjectName("SB_MaxFocusDistanceSpinBox")
        self.R_ImageCollectionFocusRangeRow.addWidget(self.SB_MaxFocusDistanceSpinBox)
        self.verticalLayout_2.addLayout(self.R_ImageCollectionFocusRangeRow)
        self.R_ImageCollectionFocusPointsRow = QtWidgets.QHBoxLayout()
        self.R_ImageCollectionFocusPointsRow.setObjectName("R_ImageCollectionFocusPointsRow")
        self.L_FocusPointsTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_FocusPointsTitleLabel.sizePolicy().hasHeightForWidth())
        self.L_FocusPointsTitleLabel.setSizePolicy(sizePolicy)
        self.L_FocusPointsTitleLabel.setObjectName("L_FocusPointsTitleLabel")
        self.R_ImageCollectionFocusPointsRow.addWidget(self.L_FocusPointsTitleLabel)
        self.SB_FocusPointsValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_FocusPointsValueSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_FocusPointsValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_FocusPointsValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_FocusPointsValueSpinBox.setMinimum(1)
        self.SB_FocusPointsValueSpinBox.setMaximum(100)
        self.SB_FocusPointsValueSpinBox.setProperty("value", 5)
        self.SB_FocusPointsValueSpinBox.setObjectName("SB_FocusPointsValueSpinBox")
        self.R_ImageCollectionFocusPointsRow.addWidget(self.SB_FocusPointsValueSpinBox)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageCollectionFocusPointsRow.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.R_ImageCollectionFocusPointsRow)
        self.DIV_00 = QtWidgets.QFrame(parent=self.GB_CalibrationSettingsGroupBox)
        self.DIV_00.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.DIV_00.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.DIV_00.setObjectName("DIV_00")
        self.verticalLayout_2.addWidget(self.DIV_00)
        self.R_ImageCollectionPrimeRow = QtWidgets.QHBoxLayout()
        self.R_ImageCollectionPrimeRow.setSpacing(0)
        self.R_ImageCollectionPrimeRow.setObjectName("R_ImageCollectionPrimeRow")
        self.L_IsPrimeTitleLable = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_IsPrimeTitleLable.sizePolicy().hasHeightForWidth())
        self.L_IsPrimeTitleLable.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        self.L_IsPrimeTitleLable.setFont(font)
        self.L_IsPrimeTitleLable.setObjectName("L_IsPrimeTitleLable")
        self.R_ImageCollectionPrimeRow.addWidget(self.L_IsPrimeTitleLable)
        self.CB_IsPrimeValueCheckBox = QtWidgets.QCheckBox(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CB_IsPrimeValueCheckBox.sizePolicy().hasHeightForWidth())
        self.CB_IsPrimeValueCheckBox.setSizePolicy(sizePolicy)
        self.CB_IsPrimeValueCheckBox.setText("")
        self.CB_IsPrimeValueCheckBox.setTristate(False)
        self.CB_IsPrimeValueCheckBox.setObjectName("CB_IsPrimeValueCheckBox")
        self.R_ImageCollectionPrimeRow.addWidget(self.CB_IsPrimeValueCheckBox)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageCollectionPrimeRow.addItem(spacerItem4)
        self.L_PrimeZoomTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_PrimeZoomTitleLabel.sizePolicy().hasHeightForWidth())
        self.L_PrimeZoomTitleLabel.setSizePolicy(sizePolicy)
        self.L_PrimeZoomTitleLabel.setObjectName("L_PrimeZoomTitleLabel")
        self.R_ImageCollectionPrimeRow.addWidget(self.L_PrimeZoomTitleLabel)
        self.SB_PrimeZoomValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_PrimeZoomValueSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_PrimeZoomValueSpinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.SB_PrimeZoomValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_PrimeZoomValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_PrimeZoomValueSpinBox.setProperty("value", 35)
        self.SB_PrimeZoomValueSpinBox.setObjectName("SB_PrimeZoomValueSpinBox")
        self.R_ImageCollectionPrimeRow.addWidget(self.SB_PrimeZoomValueSpinBox)
        self.verticalLayout_2.addLayout(self.R_ImageCollectionPrimeRow)
        self.R_ImageCollectionZoomRangeRow = QtWidgets.QHBoxLayout()
        self.R_ImageCollectionZoomRangeRow.setSpacing(0)
        self.R_ImageCollectionZoomRangeRow.setObjectName("R_ImageCollectionZoomRangeRow")
        self.L_ZoomRangeTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        self.L_ZoomRangeTitleLabel.setObjectName("L_ZoomRangeTitleLabel")
        self.R_ImageCollectionZoomRangeRow.addWidget(self.L_ZoomRangeTitleLabel)
        self.L_MinZoomDistanceLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_MinZoomDistanceLabel.sizePolicy().hasHeightForWidth())
        self.L_MinZoomDistanceLabel.setSizePolicy(sizePolicy)
        self.L_MinZoomDistanceLabel.setObjectName("L_MinZoomDistanceLabel")
        self.R_ImageCollectionZoomRangeRow.addWidget(self.L_MinZoomDistanceLabel)
        self.SB_MinZoomDistanceSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_MinZoomDistanceSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_MinZoomDistanceSpinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.SB_MinZoomDistanceSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_MinZoomDistanceSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_MinZoomDistanceSpinBox.setMaximum(1000)
        self.SB_MinZoomDistanceSpinBox.setProperty("value", 100)
        self.SB_MinZoomDistanceSpinBox.setObjectName("SB_MinZoomDistanceSpinBox")
        self.R_ImageCollectionZoomRangeRow.addWidget(self.SB_MinZoomDistanceSpinBox)
        spacerItem5 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageCollectionZoomRangeRow.addItem(spacerItem5)
        self.L_MaxZoomDistanceLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_MaxZoomDistanceLabel.sizePolicy().hasHeightForWidth())
        self.L_MaxZoomDistanceLabel.setSizePolicy(sizePolicy)
        self.L_MaxZoomDistanceLabel.setObjectName("L_MaxZoomDistanceLabel")
        self.R_ImageCollectionZoomRangeRow.addWidget(self.L_MaxZoomDistanceLabel)
        self.SB_MaxZoomDistanceSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_MaxZoomDistanceSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_MaxZoomDistanceSpinBox.setMaximumSize(QtCore.QSize(50, 16777215))
        self.SB_MaxZoomDistanceSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_MaxZoomDistanceSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_MaxZoomDistanceSpinBox.setMinimum(0)
        self.SB_MaxZoomDistanceSpinBox.setMaximum(1000)
        self.SB_MaxZoomDistanceSpinBox.setProperty("value", 500)
        self.SB_MaxZoomDistanceSpinBox.setObjectName("SB_MaxZoomDistanceSpinBox")
        self.R_ImageCollectionZoomRangeRow.addWidget(self.SB_MaxZoomDistanceSpinBox)
        self.verticalLayout_2.addLayout(self.R_ImageCollectionZoomRangeRow)
        self.R_ImageCaptureZoomPointsRow = QtWidgets.QHBoxLayout()
        self.R_ImageCaptureZoomPointsRow.setObjectName("R_ImageCaptureZoomPointsRow")
        self.L_ZoomPointsTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.L_ZoomPointsTitleLabel.sizePolicy().hasHeightForWidth())
        self.L_ZoomPointsTitleLabel.setSizePolicy(sizePolicy)
        self.L_ZoomPointsTitleLabel.setObjectName("L_ZoomPointsTitleLabel")
        self.R_ImageCaptureZoomPointsRow.addWidget(self.L_ZoomPointsTitleLabel)
        self.SB_ZoomPointsValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_ZoomPointsValueSpinBox.setMinimumSize(QtCore.QSize(50, 0))
        self.SB_ZoomPointsValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.SB_ZoomPointsValueSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.SB_ZoomPointsValueSpinBox.setMinimum(1)
        self.SB_ZoomPointsValueSpinBox.setProperty("value", 1)
        self.SB_ZoomPointsValueSpinBox.setObjectName("SB_ZoomPointsValueSpinBox")
        self.R_ImageCaptureZoomPointsRow.addWidget(self.SB_ZoomPointsValueSpinBox)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageCaptureZoomPointsRow.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.R_ImageCaptureZoomPointsRow)
        self.R_SamplesPerConfigurationRow = QtWidgets.QHBoxLayout()
        self.R_SamplesPerConfigurationRow.setObjectName("R_SamplesPerConfigurationRow")
        self.L_SamplesPerConfigurationTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        self.L_SamplesPerConfigurationTitleLabel.setObjectName("L_SamplesPerConfigurationTitleLabel")
        self.R_SamplesPerConfigurationRow.addWidget(self.L_SamplesPerConfigurationTitleLabel)
        self.SB_SamplesPerConfigurationValueSpinBox = QtWidgets.QSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.SB_SamplesPerConfigurationValueSpinBox.setMinimum(1)
        self.SB_SamplesPerConfigurationValueSpinBox.setMaximum(99)
        self.SB_SamplesPerConfigurationValueSpinBox.setProperty("value", 5)
        self.SB_SamplesPerConfigurationValueSpinBox.setObjectName("SB_SamplesPerConfigurationValueSpinBox")
        self.R_SamplesPerConfigurationRow.addWidget(self.SB_SamplesPerConfigurationValueSpinBox)
        self.verticalLayout_2.addLayout(self.R_SamplesPerConfigurationRow)
        self.DIV_01 = QtWidgets.QFrame(parent=self.GB_CalibrationSettingsGroupBox)
        self.DIV_01.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.DIV_01.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.DIV_01.setObjectName("DIV_01")
        self.verticalLayout_2.addWidget(self.DIV_01)
        self.R_ImageGatherModeRow = QtWidgets.QHBoxLayout()
        self.R_ImageGatherModeRow.setObjectName("R_ImageGatherModeRow")
        self.L_ImageGatherModeTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        font = QtGui.QFont()
        font.setBold(True)
        self.L_ImageGatherModeTitleLabel.setFont(font)
        self.L_ImageGatherModeTitleLabel.setObjectName("L_ImageGatherModeTitleLabel")
        self.R_ImageGatherModeRow.addWidget(self.L_ImageGatherModeTitleLabel)
        self.RB_ImageGatherModeTimedRadioButton = QtWidgets.QRadioButton(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RB_ImageGatherModeTimedRadioButton.sizePolicy().hasHeightForWidth())
        self.RB_ImageGatherModeTimedRadioButton.setSizePolicy(sizePolicy)
        self.RB_ImageGatherModeTimedRadioButton.setChecked(True)
        self.RB_ImageGatherModeTimedRadioButton.setObjectName("RB_ImageGatherModeTimedRadioButton")
        self.R_ImageGatherModeRow.addWidget(self.RB_ImageGatherModeTimedRadioButton)
        spacerItem7 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.R_ImageGatherModeRow.addItem(spacerItem7)
        self.RB_ImageGatherModeManualRadioButton = QtWidgets.QRadioButton(parent=self.GB_CalibrationSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RB_ImageGatherModeManualRadioButton.sizePolicy().hasHeightForWidth())
        self.RB_ImageGatherModeManualRadioButton.setSizePolicy(sizePolicy)
        self.RB_ImageGatherModeManualRadioButton.setObjectName("RB_ImageGatherModeManualRadioButton")
        self.R_ImageGatherModeRow.addWidget(self.RB_ImageGatherModeManualRadioButton)
        self.verticalLayout_2.addLayout(self.R_ImageGatherModeRow)
        self.R_TimeToHoldStillRow = QtWidgets.QHBoxLayout()
        self.R_TimeToHoldStillRow.setObjectName("R_TimeToHoldStillRow")
        self.L_TimeToHoldStillTitleLabel = QtWidgets.QLabel(parent=self.GB_CalibrationSettingsGroupBox)
        self.L_TimeToHoldStillTitleLabel.setObjectName("L_TimeToHoldStillTitleLabel")
        self.R_TimeToHoldStillRow.addWidget(self.L_TimeToHoldStillTitleLabel)
        self.DSP_TimeToHoldStillValueDoubleSpinBox = QtWidgets.QDoubleSpinBox(parent=self.GB_CalibrationSettingsGroupBox)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setMinimumSize(QtCore.QSize(60, 0))
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setMinimum(0.25)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setMaximum(10.0)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setProperty("value", 2.0)
        self.DSP_TimeToHoldStillValueDoubleSpinBox.setObjectName("DSP_TimeToHoldStillValueDoubleSpinBox")
        self.R_TimeToHoldStillRow.addWidget(self.DSP_TimeToHoldStillValueDoubleSpinBox)
        self.verticalLayout_2.addLayout(self.R_TimeToHoldStillRow)
        self.R_CheckerboardSizeRow = QtWidgets.QHBoxLayout()
        self.R_CheckerboardSizeRow.setSpacing(0)
        self.R_CheckerboardSizeRow.setObjectName("R_CheckerboardSizeRow")
        self.verticalLayout_2.addLayout(self.R_CheckerboardSizeRow)
        self.verticalLayout.addWidget(self.GB_CalibrationSettingsGroupBox)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem8)
        self.BB_SettingsActionsButtonBox = QtWidgets.QDialogButtonBox(parent=D_CalibrationSettingsDialog)
        self.BB_SettingsActionsButtonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.BB_SettingsActionsButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.BB_SettingsActionsButtonBox.setObjectName("BB_SettingsActionsButtonBox")
        self.verticalLayout.addWidget(self.BB_SettingsActionsButtonBox)

        self.retranslateUi(D_CalibrationSettingsDialog)
        self.BB_SettingsActionsButtonBox.accepted.connect(D_CalibrationSettingsDialog.accept) # type: ignore
        self.BB_SettingsActionsButtonBox.rejected.connect(D_CalibrationSettingsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(D_CalibrationSettingsDialog)

    def retranslateUi(self, D_CalibrationSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        D_CalibrationSettingsDialog.setWindowTitle(_translate("D_CalibrationSettingsDialog", "Settings"))
        self.GB_CameraSettingsGroupBox.setTitle(_translate("D_CalibrationSettingsDialog", "Camera Settings"))
        self.SB_ImageResTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Image Resolution (px)"))
        self.SB_ImageResWidthLabel.setText(_translate("D_CalibrationSettingsDialog", "Width"))
        self.SB_ImageResHeightLabel.setText(_translate("D_CalibrationSettingsDialog", "Height"))
        self.L_SensorSizeTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Sensor Size (mm)"))
        self.L_SensorSizeWidthLabel.setText(_translate("D_CalibrationSettingsDialog", "Width"))
        self.L_SensorSizeHeightLabel.setText(_translate("D_CalibrationSettingsDialog", "Height"))
        self.GB_CalibrationSettingsGroupBox.setTitle(_translate("D_CalibrationSettingsDialog", "Image Capture Settings"))
        self.L_FocusRangeTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Focus Distance Range (cm)"))
        self.L_MinFocusDistanceLabel.setText(_translate("D_CalibrationSettingsDialog", "Min"))
        self.L_MaxFocusDistanceLabel.setText(_translate("D_CalibrationSettingsDialog", "Max"))
        self.L_FocusPointsTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Focus Points"))
        self.L_IsPrimeTitleLable.setText(_translate("D_CalibrationSettingsDialog", "Prime Lens"))
        self.L_PrimeZoomTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Prime Focal Length (mm)"))
        self.L_ZoomRangeTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Zoom Range (mm)"))
        self.L_MinZoomDistanceLabel.setText(_translate("D_CalibrationSettingsDialog", "Min"))
        self.L_MaxZoomDistanceLabel.setText(_translate("D_CalibrationSettingsDialog", "Max"))
        self.L_ZoomPointsTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Zoom Points"))
        self.L_SamplesPerConfigurationTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Images Per Configuration"))
        self.L_ImageGatherModeTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Gather Mode"))
        self.RB_ImageGatherModeTimedRadioButton.setText(_translate("D_CalibrationSettingsDialog", "Timed"))
        self.RB_ImageGatherModeManualRadioButton.setText(_translate("D_CalibrationSettingsDialog", "Manual"))
        self.L_TimeToHoldStillTitleLabel.setText(_translate("D_CalibrationSettingsDialog", "Time to Hold Still (seconds)"))
