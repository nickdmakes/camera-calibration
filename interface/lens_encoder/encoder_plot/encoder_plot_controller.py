import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt

#from interface.session.models.lens_encoder_model import LensEncoderModel, LENS_ENCODER_MAP_JSON
from interface.connection.serial_connection.serial_context_manager import SerialContextManager
from interface.connection.metadata_connection.metadata_context_manager import MetadataContextManager
from interface.app.main_window import Ui_MainWindow as MainWindow
from interface.session.calibration_session import CalibrationSession

class LensEncoderPlotController:
    def __init__(self, main_window: MainWindow, session: CalibrationSession):
        self.mw = main_window
        self.session = session
        self.line_plot_items = {"focus": [], "iris": [], "zoom": []} # First list of plot items -> linePlot
        self.bar_plot_items = {"focus": [], "iris": [], "zoom": []} # First list of plot items -> barPlot
        self.debug_window = self.mw.TB_LensEncoderDebugTextBrowser
        self.setupUi()

    def setupUi(self):
        self.mw.PW_FocusEncoderPlotWidget.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.PW_IrisEncoderPlotWidget.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.PW_ZoomEncoderPlotWidget.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.PW_RMSEFocusBarChart.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.PW_RMSEIrisBarChart.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.PW_RMSEZoomBarChart.plotItem.getViewBox().setMouseEnabled(x=False, y=False)
        self.mw.L_FocusEncoderLiveLabel.setText("NA")
        self.mw.L_FocusEncoderLiveLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mw.L_IrisEncoderLiveLabel.setText("NA")
        self.mw.L_IrisEncoderLiveLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mw.L_ZoomEncoderLiveLabel.setText("NA")
        self.mw.L_ZoomEncoderLiveLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mw.L_ZoomEncoderGraphLabel.setEnabled(not self.session.settings.get_is_prime())
        self.updateAllLineGraphs()
        self.updateAllBarGraphs()

    def updateAllGraphs(self):
        self.updateAllLineGraphs()
        self.updateAllBarGraphs()

    def updateAllBarGraphs(self):
        self._plotFocusBarChart()
        self._plotIrisBarChart()
        self._plotZoomBarChart()

    def _plotFocusBarChart(self):
        '''
        Function: Plots the focus bar chart
        '''
        self._clearBarGraph("focus")
        bar_widget = self.mw.PW_RMSEFocusBarChart
        bar_widget.setXRange(-0.5, 0.5)
        bar_widget.setYRange(-0.5, 0.5)
        # Focus needs to be fitted in order to calculate error
        if not self.session.lem.focus_is_fitted():
            return
        # If focus is fitted with linear interpolation, show text that says so
        if self.session.lem.focus_fit_is_linear_interpolation():
            text_item = pg.TextItem(f"Uses Linear Interpolation", anchor=(0.5, 0.5), color=(255, 255, 255), html='<div style="font-size: 16pt">Linear Interpolation</div>')
            self.mw.PW_RMSEFocusBarChart.addItem(text_item)
            self.bar_plot_items["focus"].append(text_item)
            return
        
        x_raw = np.array(self.session.lem.get_values(type="focus")).tolist()
        if x_raw == []:
            text_item = pg.TextItem(f"No focus values", anchor=(0.5, 0.5), color=(255, 255, 255))
            bar_widget.addItem(text_item)
        x_scaled = [np.log10(i+1) for i in x_raw]
        y_actual = (np.array(self.session.lem.get_motor_positions(type="focus"))/10000).tolist()
        y_predicted = self.session.lem.polytrope_fn(x_scaled, *self.session.lem.get_parameters(type="focus"))

        y_diff = np.abs(np.subtract(y_actual, y_predicted))
        min_residual = np.min(y_diff)
        max_residual = np.max(y_diff)
        bar_widget.setXRange(1, len(x_scaled)-1)
        bar_widget.setYRange(min_residual, max(0.2, max_residual))

        bargraph_item = pg.BarGraphItem(x=range(1, len(x_scaled)+1), height=y_diff, width=0.6, pen=pg.mkPen(255, 255, 255), brush=pg.mkBrush(0, 255, 0))
        bar_widget.addItem(bargraph_item)
        self.bar_plot_items["focus"].append(bargraph_item)

    def _plotIrisBarChart(self):
        '''
        Function: Plots the iris bar chart
        '''
        self._clearBarGraph("iris")
        bar_widget = self.mw.PW_RMSEIrisBarChart
        bar_widget.setXRange(-0.5, 0.5)
        bar_widget.setYRange(-0.5, 0.5)
        # Iris needs to be fitted in order to calculate error
        if not self.session.lem.iris_is_fitted():
            return
        # If iris is fitted with linear interpolation, show text that says so
        if self.session.lem.iris_fit_is_linear_interpolation():
            text_item = pg.TextItem(f"Uses Linear Interpolation", anchor=(0.5, 0.5), color=(255, 255, 255), html='<div style="font-size: 16pt">Linear Interpolation</div>')
            self.mw.PW_RMSEIrisBarChart.addItem(text_item)
            self.bar_plot_items["iris"].append(text_item)
            return
        
        x_raw = np.array(self.session.lem.get_values(type="iris")).tolist()
        y_actual = (np.array(self.session.lem.get_motor_positions(type="iris"))/10000).tolist()
        y_predicted = self.session.lem.polytrope_fn(x_raw, *self.session.lem.get_parameters(type="iris"))

        y_diff = np.abs(np.subtract(y_actual, y_predicted))
        min_residual = np.min(y_diff)
        max_residual = np.max(y_diff)
        bar_widget.setXRange(1, len(x_raw))
        bar_widget.setYRange(min_residual, max(0.2, max_residual))

        bargraph_item = pg.BarGraphItem(x=range(1, len(x_raw)+1), height=y_diff, width=0.6, pen=pg.mkPen(255, 255, 255), brush=pg.mkBrush(0, 255, 0))
        bar_widget.addItem(bargraph_item)
        self.bar_plot_items["iris"].append(bargraph_item)

    def _plotZoomBarChart(self):
        '''
        Function: Plots the zoom bar chart
        '''
        self._clearBarGraph("zoom")
        bar_widget = self.mw.PW_RMSEZoomBarChart
        bar_widget.setXRange(-0.5, 0.5)
        bar_widget.setYRange(-0.5, 0.5)
        bar_widget.setBackgroundBrush(pg.mkBrush(0, 0, 0))
        if self.session.settings.get_is_prime():
            text_item = pg.TextItem(f"Lens is Prime", anchor=(0.5, 0.5), color=(255, 255, 255), html='<div style="font-size: 16pt">Lens is Prime</div>')
            bar_widget.setBackgroundBrush(pg.mkBrush(255, 0, 0, 20))
            bar_widget.addItem(text_item)
            self.bar_plot_items["zoom"].append(text_item)
            return

        # Zoom needs to be fitted in order to calculate error
        if not self.session.lem.zoom_is_fitted():
            return
        x_raw = np.array(self.session.lem.get_values(type="zoom")).tolist()
        y_actual = (np.array(self.session.lem.get_motor_positions(type="zoom"))/10000).tolist()
        y_predicted = self.session.lem.polytrope_fn(x_raw, *self.session.lem.get_parameters(type="zoom"))

        y_diff = np.abs(np.subtract(y_actual, y_predicted))
        min_residual = np.min(y_diff)
        max_residual = np.max(y_diff)
        bar_widget.setXRange(1, len(x_raw))
        bar_widget.setYRange(min_residual, max(0.2, max_residual))

        bargraph_item = pg.BarGraphItem(x=range(1, len(x_raw)+1), height=y_diff, width=0.6, pen=pg.mkPen(255, 255, 255), brush=pg.mkBrush(0, 255, 0))
        bar_widget.addItem(bargraph_item)
        self.bar_plot_items["zoom"].append(bargraph_item)

    def updateAllLineGraphs(self):
        self._plotLineGraph(type="focus")
        self._plotLineGraph(type="iris")
        self._plotLineGraph(type="zoom")

    def _plotLineGraph(self, type: str):
        plot_widget = None
        if type == "focus":
            plot_widget = self.mw.PW_FocusEncoderPlotWidget
        elif type == "iris":
            plot_widget = self.mw.PW_IrisEncoderPlotWidget
        elif type == "zoom":
            plot_widget = self.mw.PW_ZoomEncoderPlotWidget
            plot_widget.setBackgroundBrush(pg.mkBrush(0, 0, 0))
        
        for pi in self.line_plot_items[type]:
            plot_widget.removeItem(pi)
        self.line_plot_items[type].clear()

        plot_widget.setXRange(-0.5, 0.5)
        plot_widget.setYRange(-0.5, 0.5)

        x = np.array(self.session.lem.get_values(type=type)).tolist()
        # If the type is focus, put the values on a logarithmic scale
        if type == "focus":
            x = [np.log10(i+1) for i in x]
        y = (np.array(self.session.lem.get_motor_positions(type=type))/10000).tolist()

        if type == "zoom" and self.session.settings.get_is_prime():
            text_item = pg.TextItem(f"Lens is Prime", anchor=(0.5, 0.5), color=(255, 255, 255), html='<div style="font-size: 16pt">Lens is Prime</div>')
            plot_widget.setBackgroundBrush(pg.mkBrush(255, 0, 0, 20))
            plot_widget.addItem(text_item)
            self.line_plot_items[type].append(text_item)
        elif x == [] or y == []:
            text_item = pg.TextItem(f"No {type} values", anchor=(0.5, 0.5), color=(255, 255, 255))
            plot_widget.addItem(text_item)
            self.line_plot_items[type].append(text_item)
        else:
            plot_widget.setXRange(x[0], x[-1])
            plot_widget.setYRange(y[0], y[-1])
            scatter_item = pg.ScatterPlotItem(x=x, y=y, size=5, pen=pg.mkPen(255, 255, 255), brush=pg.mkBrush(0, 0, 255))
            plot_widget.addItem(scatter_item)
            self.line_plot_items[type].append(scatter_item)
            if type == "focus" and self.session.lem.focus_is_fitted():
                if self.session.lem.focus_fit_is_linear_interpolation():
                    line_item = pg.PlotDataItem(x=x, y=y, pen=pg.mkPen(255, 0, 0, width=2))
                    plot_widget.addItem(line_item)
                    self.line_plot_items[type].append(line_item)
                else:
                    x_fit = np.linspace(x[0], x[-1], 500)
                    y_fit = self.session.lem.polytrope_fn(x_fit, *self.session.lem.get_parameters(type="focus"))
                    curve_item = pg.PlotCurveItem(x=x_fit, y=y_fit, pen=pg.mkPen(255, 0, 0, width=2))
                    plot_widget.addItem(curve_item)
                    self.line_plot_items[type].append(curve_item)
            elif type == "iris" and self.session.lem.iris_is_fitted():
                if self.session.lem.iris_fit_is_linear_interpolation():
                    line_item = pg.PlotDataItem(x=x, y=y, pen=pg.mkPen(255, 0, 0, width=2))
                    plot_widget.addItem(line_item)
                    self.line_plot_items[type].append(line_item)
                else:
                    x_fit = np.linspace(x[0], x[-1], 500)
                    y_fit = self.session.lem.polytrope_fn(x_fit, *self.session.lem.get_parameters(type="iris"))
                    curve_item = pg.PlotCurveItem(x=x_fit, y=y_fit, pen=pg.mkPen(255, 0, 0, width=2))
                    plot_widget.addItem(curve_item)
                    self.line_plot_items[type].append(curve_item)
            elif type == "zoom" and self.session.lem.zoom_is_fitted():
                line_item = pg.PlotDataItem(x=x, y=y, pen=pg.mkPen(255, 0, 0, width=2))
                plot_widget.addItem(line_item)
                self.line_plot_items[type].append(line_item)

    def _clearBarGraph(self, type: str):
        for pi in self.bar_plot_items[type]:
            self.mw.PW_RMSEFocusBarChart.removeItem(pi)
        self.bar_plot_items[type].clear()

    def _clearLineGraph(self, type: str):
        for pi in self.line_plot_items[type]:
            self.mw.PW_FocusEncoderPlotWidget.removeItem(pi)
        self.line_plot_items[type].clear()
