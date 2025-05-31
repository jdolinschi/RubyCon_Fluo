from __future__ import annotations

import json
import math, time
import os
from math import sqrt
from collections import deque
from typing import cast
import threading
import re
from pathlib import Path

import numpy as np
import pyqtgraph as pg

from PySide6.QtCore import Qt, QEvent, QSettings, QTimer, Slot, QThread, QUrl
from PySide6.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, \
    QPushButton, QAbstractItemView, QFileDialog, QTextBrowser
from seabreeze.cseabreeze import SeaBreezeError

from insta_raman.gui.ui.main_window import Ui_MainWindow
from insta_raman.gui.views.spectrum_view_box import SpectrumViewBox
from insta_raman.settings.settings_manager import SettingsManager
from insta_raman.device.spectrometer import SpectrometerController

from PySide6.QtWidgets import QMessageBox

from insta_raman.gui.dialogs.help_window import AboutWindow
from insta_raman.gui.dialogs.about_dialog import AboutDialog
from insta_raman.fitting.voigt_fitter import VoigtFitter
from insta_raman.measurement.record import MeasurementRecord
from insta_raman.fitting.auto_fit import AutoFit
from insta_raman.fitting.auto_fit_worker import AutoFitWorker
from insta_raman.measurement.calculator import MeasurementCalculator
from insta_raman.measurement.manager import MeasurementManager
from insta_raman.gui.controllers.acquisition_controller import AcquisitionController
from insta_raman.fitting.auto_fit import residual_nb, jac_nb
from insta_raman.fitting.voigt_fitter import _residual_nb as res1, _jac_nb as jac1
from insta_raman.calibration.calibration_core import (
    PRESSURE_CALIBRATIONS,          # Dict[str, PressureCalibration]
    TEMPERATURE_CALIBRATIONS,       # Dict[str, TemperatureCalibration]
    PressureCalibration,
    TemperatureCalibration,
)

DEFAULT_REF_WL = 694.22      # 1 bar ruby R1 peak (nm)
_INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*\0]')   # Windows & POSIX

class MainWindowController(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # 1. Build static UI scaffolding
        self._build_ui()

        # 2. Colours, settings paths, persistent stores
        self._load_static_assets()

        # 3. Validators & minor UI defaults
        self._configure_ui()

        # 4. Plain‑data attributes (threads, flags, caches …)
        self._create_state()

        # 5. Table model + MeasurementManager
        self._create_models()
        self._setup_measurement_manager()

        # 6. Visual widgets (Raman plot, overlays, temp plot)
        self._build_plot_items()
        self._build_temperature_plot()

        # 7. Timers
        self._create_timers()

        # 8. Calibration scales and Calculator helper
        self._init_pressure_scales()
        self._init_temperature_scales()
        self._init_calculator()

        # 9. Integration‑time widgets need their eventFilters
        self._setup_integration_widgets()

        # 10. Acquisition machinery (real device attached later in _on_device_selected)
        self._acq_mgr: AcquisitionController | None = None

        # 11. Hook up *all* signals (those that weren’t already wired inside helpers)
        self._wire_signals()

        # 12. Finished building → populate devices *after* everyone is ready
        self._refresh_devices(first_time=True)

    def _build_ui(self) -> None:
        """Instantiate the Designer‑generated UI and attach to *self*."""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def _load_static_assets(self) -> None:
        """Colours JSON + persistent settings helpers."""
        settings_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "settings")
        )

        colors_path = os.path.join(settings_dir, "colors.json")
        with open(colors_path, "r") as f:
            self.colors = json.load(f)

        # persist + last‐device
        self._sm = SettingsManager()
        self._qt = QSettings("MyCompany", "RamanNoodles")

    def _configure_ui(self) -> None:
        """Numeric validators, disabled/enabled states, trivial styles."""
        # allow only numeric (int or float) input in these three fields:
        num_validator = QDoubleValidator(-1e12, 1e12, 6, self)
        num_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.ui.lineEdit_reference_wavelength_nm.setValidator(num_validator)
        self.ui.lineEdit_reference_temperature_c.setValidator(num_validator)
        self.ui.lineEdit_measured_temperature_c.setValidator(num_validator)

        # Ensure the temperature group is unchecked and its plot hidden by default
        self.ui.groupBox_4.setChecked(False)
        self.ui.widget_temperatureplot.setVisible(False)

        # Ensure the EEPROM group is unchecked and its columnView hidden by default
        self.ui.groupBox_eeprominfo.setChecked(False)
        self.ui.tableView_eeprom.setVisible(False)

        # grey‑out disabled corrections
        self.ui.groupBox_corrections_calibrations.setStyleSheet("""
                    QCheckBox:disabled { color: gray; }
                """)

        # TEC spinbox sane defaults
        lbl = self.ui.label_integrationtime
        lbl.setCursor(Qt.PointingHandCursor)
        lbl.setStyleSheet("""
                    QLabel#label_integrationtime:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                """)
        lbl.installEventFilter(self)

        # TEC spinbox sane defaults
        self.ui.spinBox_tec_temp_setpoint.setRange(-100, 100)
        self.ui.spinBox_tec_temp_setpoint.setValue(-10)

        # Initial button states
        to_disable = [
            self.ui.pushButton_add_measurement,
            self.ui.pushButton_remove_measurement,
            self.ui.pushButton_removeall_measurements,
            self.ui.pushButton_save_selected,
            self.ui.pushButton_save_all,
            self.ui.pushButton_manual_fit,
            self.ui.pushButton_manual_voigt_fit,
            self.ui.pushButton_full_range,
            self.ui.pushButton_zoom,
            self.ui.pushButton_scale_intensity,
            self.ui.checkBox_autofit,
            self.ui.pushButton_fromview,
            self.ui.pushButton_zoom_to_range,
            self.ui.pushButton_clear_all_fits,
        ]
        for w in to_disable:
            w.setEnabled(False)

        self.ui.progressBar.setValue(100)
        self.ui.progressBar_scans_progress.setValue(100)

        help_menu = self.menuBar().addMenu("Help")

        self._act_user_guide = QAction("User Guide", self)
        self._act_user_guide.triggered.connect(self._show_user_guide_window)
        help_menu.addAction(self._act_user_guide)

        self._act_about = QAction("About", self)
        self._act_about.triggered.connect(self._show_about_dialog)
        help_menu.addAction(self._act_about)

    def _show_user_guide_window(self) -> None:
        if not hasattr(self, "_user_guide_win"):
            self._user_guide_win = AboutWindow(self)
        self._user_guide_win.show()
        self._user_guide_win.raise_()
        self._user_guide_win.activateWindow()

    # ---- Help → About ----------------------------------------------
    def _show_about_dialog(self) -> None:
        AboutDialog(self).exec()

    def _create_state(self) -> None:
        # about‑to‑quit → make sure TEC is disabled
        q_app = cast(QApplication, QApplication.instance())
        q_app.aboutToQuit.connect(self._disable_tec_on_exit)

        # worker threads
        self._auto_thread = None  # type: QThread | None
        self._auto_worker = None  # type: AutoFitWorker | None

        # generic flags / holders
        self._fitting_range_initialized = False

        self._bg_collecting = False
        self._pending_spectrum = None  # (wl, counts) queued for throttled plot

        # latest‑fit bookkeeping
        self._last_voigt_popt = None
        self._last_voigt_pcov = None
        self._last_manual_pos = None
        self._manual_voigt_locked = False
        self._manual_locked = False
        self._manual_voigt_delta = 0.5  # initial half-window in nm
        self._manual_voigt_min_delta = 0.1
        self._manual_voigt_max_delta = 10.0

        # cursor / plot throttling
        self._last_cursor_x: float | None = None
        self._last_pressure_time = 0.0
        self._last_flush_time = time.perf_counter()
        self._flush_scheduled = False

        # spectrum‑processing flags
        self._flags = {
            "electric_dark": False,
            "optical_dark": False,
            "stray_light": False,
            "non_linearity": False,
            "irradiance": False,
            "boxcar": False,
            "pixel_binning": False,
        }
        self._bin_size = 1
        self._boxcar_width = 1

        # coefficients / cached arrays (initialised to safe defaults)
        self._edark: list[tuple[int, int]] = []
        self._odark: list[tuple[int, int]] = []
        self._nl_coef = np.ones(1)
        self._sl_coef = np.zeros(1)
        self._irrad_coef = np.ones(1)

        # device‑related placeholders
        self._spec_ctrl: SpectrometerController | None = None
        self._pixel_count: int = 0

        self._last_wl = None
        self._last_raw_counts = None

        self._initial_tec_temp = None
        self._painting_paused = False

        self._pressure_cal: PressureCalibration | None = None
        self._temperature_cal: TemperatureCalibration | None = None

        # auto-fit concurrency guards
        self._auto_fit_running = False  # a fit thread is alive
        self._auto_fit_pending = False  # a new spectrum arrived while fitting

        def _warm_up():
            # tiny dummy arrays – enough for Numba’s type‑specialisation
            x = np.linspace(0.0, 1.0, 5, dtype=np.float64)
            y = np.zeros_like(x)
            residual_nb(np.zeros(9), x, y)
            jac_nb(np.zeros(9), x, y)
            res1(np.zeros(4), x, y)
            jac1(np.zeros(4), x, y)

        threading.Thread(target=_warm_up, daemon=True).start()

    def _create_models(self) -> None:
        """QStandardItemModel shown in the Saved‑measurements table."""
        self._saved_model = QStandardItemModel(0, 6, self)
        self._saved_model.setHorizontalHeaderLabels([
            "Name",
            "R1 wavelength (nm)",
            "Pressure (GPa)",
            "Temperature (C)",
            "Pressure calib.",
            "Temperature calib.",
        ])
        self.ui.tableView_saved_measurements.setModel(self._saved_model)
        self.ui.tableView_saved_measurements.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

    def _setup_measurement_manager(self) -> None:
        """Attach MeasurementManager + hook up Add / Remove / Save buttons."""
        self._measurement_manager = MeasurementManager(self._saved_model, parent=self)

        # Add
        self.ui.pushButton_add_measurement.clicked.connect(self._on_add_measurement)

        # Remove (selected / all)
        self.ui.pushButton_remove_measurement.clicked.connect(
            lambda: self._measurement_manager.remove_selected(
                self.ui.tableView_saved_measurements
            )
        )
        self.ui.pushButton_removeall_measurements.clicked.connect(
            self._measurement_manager.remove_all
        )

        # Save (selected / all)
        self.ui.pushButton_save_selected.clicked.connect(
            lambda: self._measurement_manager.save_selected(
                self.ui.tableView_saved_measurements
            )
        )
        self.ui.pushButton_save_all.clicked.connect(
            self._measurement_manager.save_all
        )

        # NEW — auto-save toggle
        self.ui.checkBox_auto_save_measurements.toggled.connect(
            self._on_auto_save_toggled
        )

        # Enable/disable buttons when selection / records change
        sel_model = self.ui.tableView_saved_measurements.selectionModel()
        sel_model.selectionChanged.connect(self._update_remove_buttons)
        sel_model.selectionChanged.connect(self._update_save_buttons)
        self._measurement_manager.recordsChanged.connect(self._update_remove_buttons)
        self._measurement_manager.recordsChanged.connect(self._update_save_buttons)

    def _build_plot_items(self) -> None:
        """Central Raman plot + every overlay / InfiniteLine."""
        self._plot_item = pg.PlotItem(viewBox=SpectrumViewBox(self.ui.widget))
        self.ui.widget.setCentralItem(self._plot_item)

        # main corrected spectrum
        self._curve = self._plot_item.plot(pen=self.colors["raw_data_curve"], name="corrected")

        # inside / outside curves (for autofit highlight)
        self._curve_inside = self._plot_item.plot(pen=pg.mkPen(self.colors["curve_inside"], width=1.5), name='inside')
        self._curve_outside = self._plot_item.plot(pen=pg.mkPen(self.colors["curve_outside"], width=1.5),
                                                   name='outside')
        self._curve_inside.hide()
        self._curve_outside.hide()

        # two‑peak Voigt overlay
        self._auto_model_curve = self._plot_item.plot(
            pen=pg.mkPen(self.colors["fit_curve"], width=2, style=Qt.DashLine), name='Auto Fit')
        self._auto_model_curve.hide()

        # auto‑fit R1 / R2 lines
        self._auto_voigt_curve = self._plot_item.plot(pen=self.colors["fit_curve"], name='voigt')
        self._auto_voigt_line = pg.InfiniteLine(angle=90, pen=pg.mkPen(self.colors["manual_locked_line"], width=2),
                                                movable=False)
        self._auto_voigt_line.setZValue(20)
        self._auto_voigt_line.setVisible(False)
        self._plot_item.addItem(self._auto_voigt_line)

        self._r2_voigt_line = pg.InfiniteLine(
            angle=90,
            pen=pg.mkPen(self.colors["r2_reference_line"], width=2, style=Qt.DashDotLine),
            movable=False
        )
        self._r2_voigt_line.setZValue(20)
        self._r2_voigt_line.setVisible(False)
        self._plot_item.addItem(self._r2_voigt_line)

        # manual follow + manual Voigt overlays
        self._manual_line = pg.InfiniteLine(angle=90, pen=pg.mkPen(self.colors["manual_follow_line"], width=2),
                                            movable=False)
        self._manual_line.setZValue(20)
        self._manual_line.setVisible(False)
        self._plot_item.addItem(self._manual_line)

        self._manual_voigt_curve = self._plot_item.plot(pen=self.colors["fit_curve"], name='voigt')
        self._manual_voigt_line = pg.InfiniteLine(angle=90, pen=pg.mkPen(self.colors["fit_curve"], width=2),
                                                  movable=False)
        self._manual_voigt_line.setZValue(20)
        self._manual_voigt_line.setVisible(False)
        self._plot_item.addItem(self._manual_voigt_line)

        # helper Voigt fitter and original wheel handler cache
        self._manual_voigt_fitter = VoigtFitter()
        self._orig_vb_wheel = self._plot_item.vb.wheelEvent

        # live cursor tracking
        self.ui.widget.scene().sigMouseMoved.connect(self._update_cursor_position)

        self.vb = self._plot_item.vb
        self.vb.interactionStarted.connect(self._on_pause_painting)
        self.vb.interactionFinished.connect(self._on_resume_painting)
        self.vb.interactionFinished.connect(self._apply_auto_intensity_after_interaction)
        self.vb.sigRangeChanged.connect(lambda *args: self._apply_auto_intensity_after_interaction())

        self.vb.disableAutoRange(pg.ViewBox.YAxis)  # ← add this line

    def _build_temperature_plot(self) -> None:
        """Static setup for the embedded temperature plot widget."""
        temp_plot = self.ui.widget_temperatureplot.getPlotItem()
        temp_vb = temp_plot.getViewBox()
        temp_vb.setMouseEnabled(False, False)
        temp_vb.setMenuEnabled(False)

        # in‑memory ring buffer for (timestamp, temp)
        self._temp_data = deque()

    def _create_timers(self) -> None:
        """All QTimer instances (resume‑paint, temperature poll, etc.)."""
        # resume‑painting guard (200 ms)
        self._resume_timer = QTimer(self)
        self._resume_timer.setInterval(200)
        self._resume_timer.timeout.connect(self._check_resume)
        self._resume_timer.start()

        # temperature sampling (1 s)
        self._temp_timer = QTimer(self)
        self._temp_timer.setInterval(1000)
        self._temp_timer.timeout.connect(self._sample_temperature)

        # TEC poll (created but started only on Settings tab)
        self._tec_timer = QTimer(self, interval=1000)
        self._tec_timer.timeout.connect(self._update_tec_temperature)

        # live pseudo‑Voigt fit timer (100 ms)
        self._manual_voigt_timer = QTimer(self)
        self._manual_voigt_timer.setInterval(100)
        self._manual_voigt_timer.timeout.connect(self._update_manual_voigt_fit)

    def _init_pressure_scales(self) -> None:
        self.ui.comboBox_pressurecalibrations.addItems(PRESSURE_CALIBRATIONS.keys())
        default = "Shen et al. 2020"
        self.ui.comboBox_pressurecalibrations.setCurrentText(default)
        # call once so the calculator already has something
        self.ui.comboBox_pressurecalibrations.currentTextChanged.connect(
            self._on_pressure_scale_changed
        )

    def _init_temperature_scales(self) -> None:
        self.ui.comboBox_temperaturecalibrations.addItems(TEMPERATURE_CALIBRATIONS.keys())
        default = "Yamaoka et al. 1980"
        self.ui.comboBox_temperaturecalibrations.setCurrentText(default)
        self.ui.comboBox_temperaturecalibrations.currentTextChanged.connect(
            self._on_temperature_scale_changed
        )

    def _init_calculator(self) -> None:
        self._calculator = MeasurementCalculator()
        self._update_calculator_scales()  # <─ NEW single source of truth
        self._calculator.set_reference_wavelength(
            float(self.ui.lineEdit_reference_wavelength_nm.text() or 0.0)
        )
        self._calculator.set_reference_temperature(
            float(self.ui.lineEdit_reference_temperature_c.text() or 0.0)
        )
        self.ui.lineEdit_measured_wavelength_nm.setReadOnly(True)

    def _wire_signals(self) -> None:
        """Connect every remaining Qt signal that wasn’t wired inside helpers."""
        # group the handful that originally lived inline in __init__
        self.ui.lineEdit_reference_wavelength_nm.returnPressed.connect(
            self._on_reference_wavelength_changed
        )
        self.ui.lineEdit_reference_temperature_c.returnPressed.connect(
            self._on_reference_temperature_changed
        )
        self.ui.lineEdit_measured_temperature_c.returnPressed.connect(
            self._on_temperature_input_changed
        )
        self.ui.pushButton_fromview.clicked.connect(self._on_fromview_clicked)
        self.ui.pushButton_manual_fit.toggled.connect(self._on_manual_fit_toggled)
        self.ui.pushButton_manual_voigt_fit.toggled.connect(self._on_manual_voigt_toggled)
        self.ui.widget.scene().sigMouseClicked.connect(self._on_mouse_clicked)

        self.ui.pushButton_pressurecalib_source.clicked.connect(
            self._show_pressure_source
        )
        self.ui.pushButton_temperaturecalib_source.clicked.connect(
            self._show_temperature_source
        )

        # Everything else lives in the original helper
        self._connect_signals()

    def _setup_acquisition_connections(self) -> None:
        """Wire AcquisitionManager to our buttons & progress widgets."""
        mgr = self._acq_mgr  # type: AcquisitionController

        # Keep the manager’s parameters in sync with the UI
        self.ui.doubleSpinBox_integration_time_ms.valueChanged.connect(
            lambda v, m=mgr: m.set_parameters(
                int(v * (1_000 if "(ms)" in self.ui.label_integrationtime.text() else 1_000_000)),
                self.ui.spinBox_scansaverage.value(),
                self.ui.checkBox_electric_dark.isChecked(),
                self.ui.checkBox_non_linearity.isChecked(),
            )
        )
        self.ui.spinBox_scansaverage.valueChanged.connect(
            lambda s, m=mgr: m.set_parameters(
                int(self.ui.doubleSpinBox_integration_time_ms.value() *
                    (1_000 if "(ms)" in self.ui.label_integrationtime.text() else 1_000_000)),
                s,
                self.ui.checkBox_electric_dark.isChecked(),
                self.ui.checkBox_non_linearity.isChecked(),
            )
        )

        # Single-shot / continuous toggles
        self.ui.pushButton_single.toggled.connect(self._on_single_toggled)
        self.ui.pushButton_continuous.toggled.connect(self._on_continuous_toggled)

        # Background acquisition
        self.ui.pushButton_background.toggled.connect(self._on_background_toggled)

        # Progress reporting
        mgr.integration_tick.connect(
            lambda pct: self.ui.progressBar.setValue(int(pct))
        )
        mgr.scan_tick.connect(
            lambda done, total: self.ui.progressBar_scans_progress.setValue(int(100 * done / total))
        )
        mgr.remaining_time.connect(
            lambda sec: self.ui.label_time_left_seconds.setText(f"{sec:.1f}")
        )

        # Spectrum data handlers
        mgr.spectrum_ready.connect(self._on_spectrum_ready)
        mgr.finished.connect(self._on_acquisition_finished)
        mgr.background_finished.connect(self._on_background_finished)

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Return *name* with any illegal path characters replaced by “_”."""
        cleaned = _INVALID_CHARS_RE.sub("_", name)
        cleaned = cleaned.strip().strip(".")  # no leading/trailing space/dot on Win
        cleaned = cleaned.replace(" ", "_")
        return cleaned or "measurement"

    @staticmethod
    def _unique_name(base: str,
                     occupied: set[str],
                     folder: Path | None) -> str:
        """
        Return a name that is unique with respect to *occupied* and to any existing
        file (same basename + .txt) in *folder*.
        """
        candidate = base
        idx = 1
        while (
                candidate in occupied or
                (folder is not None and (folder / f"{candidate}.txt").exists())
        ):
            candidate = f"{base}_{idx}"
            idx += 1
        return candidate

    @Slot(bool)
    def _on_auto_save_toggled(self, checked: bool) -> None:
        """
        When the user checks the Auto-save box, ask for a destination folder
        and enable MeasurementManager’s auto-save feature.  When they un-check,
        simply disable auto-save.
        """
        if checked:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Choose folder for auto-saved measurements"
            )
            if not folder:  # user cancelled → roll back the checkbox
                self.ui.checkBox_auto_save_measurements.blockSignals(True)
                self.ui.checkBox_auto_save_measurements.setChecked(False)
                self.ui.checkBox_auto_save_measurements.blockSignals(False)
                return
            self._measurement_manager.enable_auto_save(folder)
        else:
            self._measurement_manager.disable_auto_save()

    @Slot()
    def _on_acquisition_finished(self) -> None:
        """
        Common clean-up after ANY acquisition (single, continuous, background):
        • Re-enable both acquisition buttons and make sure they are *unchecked*.
        • Progress bars snap back to 100 %.
        • Optimise button re-enabled.
        • Fit/intensity housekeeping (unchanged).
        """
        # ----------- buttons -------------------------------------------
        for btn in (self.ui.pushButton_single, self.ui.pushButton_continuous):
            if btn.isChecked():
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.blockSignals(False)
            btn.setEnabled(True)

        # ----------- progress bars -------------------------------------
        self.ui.progressBar.setValue(100)
        self.ui.progressBar_scans_progress.setValue(100)

        # ----------- other UI bits -------------------------------------
        self.ui.pushButton_optimize.setEnabled(True)

        # Apply any auto-scale
        self._apply_auto_intensity_after_interaction()

        # Flush any pending spectrum that arrived during the exposure
        if self._pending_spectrum is not None:
            was_paused = self._painting_paused
            self._painting_paused = False
            self._flush_plot()
            self._painting_paused = was_paused

        # Auto-fit : kick a last fit if appropriate
        if self.ui.checkBox_autofit.isChecked():
            self._attempt_autofit()

    @Slot(bool)
    def _on_background_toggled(self, checked: bool) -> None:
        """
        ✔  checked   → start a *new* background acquisition
        ✖  unchecked → immediately stop using the stored background
                       (no acquisition, no progress‑bar updates)
        """
        if not self._acq_mgr:
            return

        btn = self.ui.pushButton_background

        if checked:
            # visual feedback while the worker runs
            btn.setText("Collecting…")
            btn.setEnabled(False)  # prevent a second click
            self._acq_mgr.collect_background()
        else:
            # instant – just drop the cached array
            self._acq_mgr.clear_background()
            btn.setText("Background")
            # make sure the progress bars stay quiet
            self.ui.progressBar.setValue(100)
            self.ui.progressBar_scans_progress.setValue(100)

    @Slot()
    def _on_background_finished(self) -> None:
        """
        Called after background acquisition finishes.
        Re-enable the other controls and update the button text.
        """
        # Re-enable acquisition controls
        self.ui.pushButton_continuous.setEnabled(True)
        self.ui.pushButton_single.setEnabled(True)
        self.ui.pushButton_optimize.setEnabled(True)

        # Show a checkmark on the button
        self.ui.pushButton_background.setText("Background ✓")
        self.ui.pushButton_background.setEnabled(True)

    @Slot(bool)
    def _on_single_toggled(self, checked: bool) -> None:
        """
        • When checked → start a **single-shot** acquisition and immediately
          disable the Continuous button so the user cannot click it.
        • When unchecked before the exposure finishes → stop after **this**
          exposure/scan (if averaging ≥ 1) but keep Continuous disabled until
          the worker emits *finished*.
        """
        if not self._acq_mgr:
            return

        if checked:  # user starts Single
            self.ui.pushButton_continuous.setEnabled(False)
            self._acq_mgr.start_single(False)
        else:  # user cancels Single
            self._acq_mgr.stop()  # finishes current scan only

    @Slot(bool)
    def _on_continuous_toggled(self, checked: bool) -> None:
        """
        Mirror of _on_single_toggled for **continuous** mode.
        """
        if not self._acq_mgr:
            return

        if checked:  # start Continuous
            self.ui.pushButton_single.setEnabled(False)
            self._acq_mgr.start_single(True)
        else:  # request stop
            self._acq_mgr.stop()  # completes current scan

    @Slot(str)
    def _on_pressure_scale_changed(self, _name: str) -> None:
        """
        Re-sync calculator + grey-out temperature picker if necessary,
        then refresh any locked fit.
        """
        self._update_calculator_scales()
        self._refresh_locked_fit()  # recompute displayed pressure

    @Slot(str)
    def _on_temperature_scale_changed(self, _name: str) -> None:
        """
        Only relevant when the currently selected pressure scale is *not*
        a combined one.  Otherwise the temp combo is disabled.
        """
        self._update_calculator_scales()
        self._refresh_locked_fit()

    @Slot()
    def _on_reference_wavelength_changed(self):
        try:
            lambda_0 = float(self.ui.lineEdit_reference_wavelength_nm.text())
        except ValueError:
            return
        self._calculator.set_reference_wavelength(lambda_0)
        self._refresh_locked_fit()

    @Slot()
    def _on_reference_temperature_changed(self):
        try:
            T0 = float(self.ui.lineEdit_reference_temperature_c.text())
        except ValueError:
            return
        self._calculator.set_reference_temperature(T0)
        self._refresh_locked_fit()

    @Slot()
    def _on_fromview_clicked(self) -> None:
        x0, x1 = self._plot_item.vb.viewRange()[0]
        self.ui.doubleSpinBox_min_fitting_range_nm.setValue(x0)
        self.ui.doubleSpinBox_max_fitting_range_nm.setValue(x1)
        # if auto-fit is active, and we have data, kick off a new fit
        if self.ui.checkBox_autofit.isChecked():
            # only attempt if there's data plotted
            wl = getattr(self._curve, 'xData', None)
            cnt = getattr(self._curve, 'yData', None)
            if wl is not None and cnt is not None and len(wl) > 0:
                self._attempt_autofit()
                self._update_autofit_highlight()

    @Slot()
    def _on_temperature_input_changed(self) -> None:
        """
        Called when the user presses Enter in either
        the measured‐ or reference‐temperature field.
        If a fit is locked, update the measured temperature
        in the calculator and refresh that locked fit.
        """
        # only proceed if a fit is locked
        if not (self._manual_voigt_locked or self._manual_locked):
            return

        # grab the new measured temperature
        try:
            Tm = float(self.ui.lineEdit_measured_temperature_c.text())
        except ValueError:
            return

        # tell the calculator, then refresh the locked fit
        self._calculator.set_measured_temperature(Tm)
        self._refresh_locked_fit()

    def _show_temperature_source(self) -> None:
        if self._temperature_cal is None:
            return
        cal = self._temperature_cal
        name = cal.name
        text = cal.source

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{name} — Full source")
        layout = QVBoxLayout(dlg)

        te = QTextEdit(dlg)
        te.setReadOnly(True)
        te.setPlainText(text)
        layout.addWidget(te)

        btns = QHBoxLayout()
        copy = QPushButton("Copy", dlg)
        close = QPushButton("Close", dlg)
        btns.addWidget(copy)
        btns.addWidget(close)
        layout.addLayout(btns)

        copy.clicked.connect(lambda: QApplication.clipboard().setText(text))
        close.clicked.connect(dlg.accept)

        dlg.resize(400, 200)
        dlg.exec()

    @Slot()
    def _on_reference_wavelength_changed(self) -> None:
        """
        Called when the user presses Enter in the reference‐wavelength field.
        Update the calculator's reference wavelength and refresh any locked fit.
        """
        # parse the new reference wavelength
        try:
            lambda_0 = float(self.ui.lineEdit_reference_wavelength_nm.text())
        except ValueError:
            return

        # update the calculator, then re-run the locked fit
        self._calculator.set_reference_wavelength(lambda_0)
        self._refresh_locked_fit()

    @Slot()
    def _update_save_buttons(self):
        """Enable Save Selected if any rows are selected; Save All if we have any rows."""
        sel = self.ui.tableView_saved_measurements.selectionModel().selectedRows()
        has_sel = bool(sel)
        has_any = self._saved_model.rowCount() > 0
        self.ui.pushButton_save_selected.setEnabled(has_sel)
        self.ui.pushButton_save_all.setEnabled(has_any)

    @Slot()
    def _update_remove_buttons(self):
        """Enable remove if any row is selected; remove-all if we have any rows."""
        sel = self.ui.tableView_saved_measurements.selectionModel().selectedRows()
        has_sel = bool(sel)
        has_any = self._saved_model.rowCount() > 0
        self.ui.pushButton_remove_measurement.setEnabled(has_sel)
        self.ui.pushButton_removeall_measurements.setEnabled(has_any)

    def _update_add_measurement_enable(self):
        # disabled while acquiring
        busy = self.ui.pushButton_continuous.isChecked() or self.ui.pushButton_single.isChecked()
        # need a real result pressure (not the em-dash)
        ready = (self.ui.label_result_pressure_gpa.text() != "—")
        self.ui.pushButton_add_measurement.setEnabled(not busy and ready)

    @Slot(object)
    def _on_mouse_clicked(self, event):
        # LEFT-click → lock either pseudo-Voigt or manual
        if event.button() == Qt.LeftButton:
            # 1) Pseudo-Voigt lock
            if self.ui.pushButton_manual_voigt_fit.isChecked() and not self._manual_voigt_locked:
                self._manual_voigt_timer.stop()
                x0 = self._manual_voigt_line.value()
                lo, hi = x0 - self._manual_voigt_delta, x0 + self._manual_voigt_delta
                mask = (self._curve.xData >= lo) & (self._curve.xData <= hi)
                x_full, y_full = self._curve.xData[mask], self._curve.yData[mask]

                try:
                    full_popt, full_pcov = self._manual_voigt_fitter.fit(x_full, y_full)
                    center, amp, fwhm, frac = full_popt
                    sigma_center = sqrt(full_pcov[0][0])
                except Exception:
                    self.ui.label_result_pressure_gpa.setText("No fit")
                    self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
                    self._manual_voigt_timer.start()
                    return

                # lock in the fit
                self._manual_voigt_locked = True
                self._last_fit_type = "Manual Voigt"
                self._last_r2_wavelength = None
                self._last_r2_voigt_popt = None
                self._last_r2_voigt_pcov = None
                self._last_baseline = None
                self._last_voigt_popt = full_popt.tolist()
                self._last_voigt_pcov = full_pcov.tolist()
                self.ui.lineEdit_measured_wavelength_nm.setText(f"{center:.3f}")
                self._update_clear_fits_button()

                # delegate pressure calculation
                self._apply_fit(center, sigma_center, "green")

                # uncheck the toggle button without triggering its slot
                self.ui.pushButton_manual_voigt_fit.blockSignals(True)
                self.ui.pushButton_manual_voigt_fit.setChecked(False)
                self.ui.pushButton_manual_voigt_fit.blockSignals(False)
                self._plot_item.vb.wheelEvent = self._orig_vb_wheel
                return

            # 2) Manual-fit lock
            if self.ui.pushButton_manual_fit.isChecked() and not self._manual_locked:
                pos = event.scenePos()
                data_pt = self._plot_item.vb.mapSceneToView(pos)
                x = data_pt.x()
                xdata = self._curve.xData
                if xdata is None or len(xdata) == 0:
                    return
                xmin, xmax = float(xdata.min()), float(xdata.max())
                if xmin <= x <= xmax:
                    self._manual_locked = True
                    self._update_clear_fits_button()

                    self._last_manual_pos = x
                    self._manual_line.setPen(pg.mkPen(self.colors["manual_locked_line"], width=2))
                    self._manual_line.setPos(x)
                    self._manual_line.setVisible(True)
                    self.ui.lineEdit_measured_wavelength_nm.setText(f"{x:.3f}")

                    # delegate pressure calculation (σ=0 for manual)
                    self._apply_fit(x, 0.0, "green")

                    self._last_fit_type = "Manual"
                    self._last_voigt_popt = None
                    self._last_voigt_pcov = None
                    self._last_r2_wavelength = None
                    self._last_r2_voigt_popt = None
                    self._last_r2_voigt_pcov = None
                    self._last_baseline = None

                    # uncheck the toggle button without triggering its slot
                    self.ui.pushButton_manual_fit.blockSignals(True)
                    self.ui.pushButton_manual_fit.setChecked(False)
                    self.ui.pushButton_manual_fit.blockSignals(False)
                return

        # RIGHT-click → clear overlays
        elif event.button() == Qt.RightButton:
            if self.ui.pushButton_manual_voigt_fit.isChecked():
                self.ui.pushButton_manual_voigt_fit.setChecked(False)
                self._manual_voigt_curve.clear()
                self._manual_voigt_line.setVisible(False)
                self._manual_voigt_timer.stop()
                self.ui.label_result_pressure_gpa.setText("—")
                self._update_add_measurement_enable()
                self._update_clear_fits_button()
                return

            if self.ui.pushButton_manual_fit.isChecked():
                self.ui.pushButton_manual_fit.setChecked(False)
                self._manual_line.setVisible(False)
                self.ui.label_result_pressure_gpa.setText("—")
                self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
                self._update_add_measurement_enable()
                self._update_clear_fits_button()
                return

    @Slot(bool)
    def _on_manual_voigt_toggled(self, checked: bool) -> None:
        """Start/stop live pseudo-Voigt mode, remapping the wheel to Δ control."""

        if checked:
            if self.ui.checkBox_autofit.isChecked():
                self.ui.checkBox_autofit.setChecked(False)
            # If manual‐fit is on, turn off the regular manual‐follow mode
            if self.ui.pushButton_manual_fit.isChecked() or self._manual_locked:
                self._manual_locked = False
                self._manual_line.setVisible(False)
                self.ui.pushButton_manual_fit.blockSignals(True)
                self.ui.pushButton_manual_fit.setChecked(False)
                self.ui.pushButton_manual_fit.blockSignals(False)
                self.ui.label_result_pressure_gpa.setText("—")
                self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
                self._update_add_measurement_enable()
                self._update_clear_fits_button()

            # Reset any previous Voigt‐lock
            self._manual_voigt_locked = False
            self._manual_voigt_line.setPen(pg.mkPen(self.colors["fit_curve"], width=3))
            self._manual_voigt_line.setVisible(True)
            self._manual_voigt_timer.start()
            self._update_add_measurement_enable()
            self._update_clear_fits_button()

            # Override the wheel so it adjusts the fit window Δ instead of zooming
            def _voigt_wheel(ev):
                delta = ev.angleDelta().y() if hasattr(ev, 'angleDelta') else ev.delta()
                factor = 1.1 ** (delta / 120)
                self._manual_voigt_delta = min(
                    self._manual_voigt_max_delta,
                    max(self._manual_voigt_min_delta, self._manual_voigt_delta * factor)
                )
                self._update_manual_voigt_fit()
                ev.accept()

            self.vb.wheelEvent = _voigt_wheel

            # Make sure the regular manual‐follow button is off
            if self.ui.pushButton_manual_fit.isChecked():
                self.ui.pushButton_manual_fit.setChecked(False)
                self._update_clear_fits_button()

        else:
            # **Restore the original zoom behavior no matter what**
            self.vb.wheelEvent = self._orig_vb_wheel

            # Stop live‐fitting updates
            self._manual_voigt_timer.stop()

            # If we never locked in an actual fit, clear the overlays and reset result
            if not self._manual_voigt_locked:
                self._manual_voigt_curve.clear()
                self._manual_voigt_line.setVisible(False)
                self.ui.label_result_pressure_gpa.setText("—")

            # Re-enable “Add measurement” if appropriate
            self._update_add_measurement_enable()
            self._update_clear_fits_button()

    @Slot()
    def _on_zoom_to_range_clicked(self) -> None:
        """
        Snap the plot’s X‑axis to the [min,max] in the two spin‑boxes.
        • Does nothing if either spin‑box is 0.0 or we have no data yet.
        • Leaves Y alone unless “Auto scale intensity” is ticked,
          which is already handled by _apply_auto_intensity_after_interaction().
        """
        # 1) guard: need some plotted data
        if self._curve.xData is None or len(self._curve.xData) == 0:
            return

        # 2) read spin‑boxes
        x_min = float(self.ui.doubleSpinBox_min_fitting_range_nm.value())
        x_max = float(self.ui.doubleSpinBox_max_fitting_range_nm.value())

        # ignore the (default) 0.0 → 0.0 case
        if x_min == 0.0 and x_max == 0.0:
            return

        # make sure they’re ordered
        if x_min > x_max:
            x_min, x_max = x_max, x_min

        # 3) apply the X‑range (no padding)
        self._plot_item.vb.setXRange(x_min, x_max, padding=0)

        # 4) if autofit highlighting is on, recolour the curve
        if self.ui.checkBox_autofit.isChecked():
            self._update_autofit_highlight()

        # 5) let the existing helper take care of auto‑Y, if enabled
        self._apply_auto_intensity_after_interaction()

    @Slot()
    def _update_manual_voigt_fit(self) -> None:
        if self._manual_voigt_locked:
            return

        x0 = self._last_cursor_x
        x_data, y_data = self._curve.xData, self._curve.yData
        if x_data is None or y_data is None:
            return

        # define fitting window
        lo, hi = x0 - self._manual_voigt_delta, x0 + self._manual_voigt_delta
        mask = (x_data >= lo) & (x_data <= hi)
        if mask.sum() < 5:
            # too few points: hide overlays
            self._manual_voigt_curve.clear()
            self._manual_voigt_line.setVisible(False)
            return

        # subsample if needed
        x_fit, y_fit = x_data[mask], y_data[mask]
        if x_fit.size > 50:
            idx = np.linspace(0, x_fit.size - 1, 50, dtype=int)
            x_sub, y_sub = x_fit[idx], y_fit[idx]
        else:
            x_sub, y_sub = x_fit, y_fit

        # perform the Voigt fit
        try:
            params, cov = self._manual_voigt_fitter.fit(x_sub, y_sub)
            center = params[0]
            sigma_center = sqrt(cov[0][0])
            self._last_voigt_popt = params.tolist()
            self._last_voigt_pcov = cov.tolist()
        except Exception:
            self._manual_voigt_curve.clear()
            self._manual_voigt_line.setVisible(False)
            return

        # draw the model overlay
        xs = np.linspace(lo, hi, 200)
        ys = self._manual_voigt_fitter.model(xs, *params)
        self._manual_voigt_curve.setData(xs, ys)
        if lo <= center <= hi:
            self._manual_voigt_line.setVisible(True)
            self._manual_voigt_line.setPos(center)
        else:
            self._manual_voigt_line.setVisible(False)

        # delegate pressure calculation to MeasurementCalculator
        self._apply_fit(center, sigma_center, "lightblue")

    @Slot(bool)
    def _on_manual_fit_toggled(self, checked: bool) -> None:
        """Enter or exit “follow” mode when the button is checked/unchecked."""
        if checked:
            if self.ui.checkBox_autofit.isChecked():
                self.ui.checkBox_autofit.setChecked(False)
            if self.ui.pushButton_manual_voigt_fit.isChecked() or self._manual_voigt_locked:
                # uncheck Voigt mode and clear its overlays
                self.ui.pushButton_manual_voigt_fit.setChecked(False)
                self._manual_voigt_timer.stop()
                self._manual_voigt_curve.clear()
                self._manual_voigt_line.setVisible(False)
                # clear result label
                self.ui.label_result_pressure_gpa.setText("—")
                # uncheck without signal
                self.ui.pushButton_manual_voigt_fit.blockSignals(True)
                self.ui.pushButton_manual_voigt_fit.setChecked(False)
                self.ui.pushButton_manual_voigt_fit.blockSignals(False)
                self._update_add_measurement_enable()
                self._update_clear_fits_button()

            # start following the cursor
            self._manual_locked = False
            self._manual_line.setPen(pg.mkPen(self.colors["manual_follow_line"], width=2))
            self._manual_line.setVisible(True)
            self._update_clear_fits_button()

        else:
            # if we’re not locked, hide it & clear the result label
            if not self._manual_locked:
                self._manual_line.setVisible(False)
                self.ui.label_result_pressure_gpa.setText("—")
                self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
                self._update_add_measurement_enable()
                self._update_clear_fits_button()

    def _show_pressure_source(self) -> None:
        """Pop up a dialog showing the full citation for the selected scale."""
        # Ensure our RubyPressureScale matches the combobox
        cal = self._pressure_cal
        name = cal.name
        text = cal.source

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{name} — Full source")
        layout = QVBoxLayout(dlg)

        te = QTextEdit(dlg)
        te.setReadOnly(True)
        te.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)   # wrap long lines
        te.setPlainText(text)                       # full citation
        layout.addWidget(te)

        btns = QHBoxLayout()
        copy = QPushButton("Copy", dlg)
        close = QPushButton("Close", dlg)
        btns.addWidget(copy)
        btns.addWidget(close)
        layout.addLayout(btns)

        copy.clicked.connect(lambda: QApplication.clipboard().setText(text))
        close.clicked.connect(dlg.accept)

        dlg.resize(400, 200)
        dlg.exec()

    def _update_calculator_scales(self) -> None:
        """
        Always sync the MeasurementCalculator with whatever is currently
        selected in the two drop-downs.  Handles “combined” calibrations
        (e.g. Rekhi 1999) by disabling the Temperature combo.
        """
        # ---- pressure calibration (always present) ----------------------
        p_name = self.ui.comboBox_pressurecalibrations.currentText()
        p_cal = PRESSURE_CALIBRATIONS[p_name]
        self._pressure_cal = p_cal  # <── keep in-sync ①
        self._calculator.set_pressure_scale(p_cal)

        # ---- temperature calibration -----------------------------------
        if p_cal.is_combined:  # Rekhi 1999 etc.
            self.ui.comboBox_temperaturecalibrations.setEnabled(False)
            # Tell the calculator “no external T-correction”.
            self._temperature_cal = None # <── keep in-sync ②
            self._calculator.set_temperature_scale(None)  # type: ignore[arg-type]
        else:
            self.ui.comboBox_temperaturecalibrations.setEnabled(True)
            t_name = self.ui.comboBox_temperaturecalibrations.currentText()
            t_cal = TEMPERATURE_CALIBRATIONS[t_name]
            self._temperature_cal = t_cal
            self._calculator.set_temperature_scale(t_cal)

    @Slot(object)
    def _update_cursor_position(self, scene_pos):
        # ── existing mapping to data_pt ──
        data_pt = self._plot_item.vb.mapSceneToView(scene_pos)
        x, y = data_pt.x(), data_pt.y()
        self.ui.label_xy_position.setText(f"{x:.2f}, {y:.2f}")

        # store for later use
        self._last_cursor_x = x

        # now update pressure in real time
        self._update_pressure_label_from_last_cursor()

        if self.ui.pushButton_manual_fit.isChecked() and not self._manual_locked:
            xdata = self._curve.xData
            if xdata is None or len(xdata) == 0:
                return

            xmin, xmax = float(xdata.min()), float(xdata.max())
            if x < xmin or x > xmax:
                self._manual_line.setVisible(False)
                self.ui.label_result_pressure_gpa.setText("—")
                self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
            else:
                # move the red line & show the locked label
                self._manual_line.setVisible(True)
                self._manual_line.setPos(x)
                cp = self.ui.label_current_pressure.text()
                self.ui.label_result_pressure_gpa.setText(cp)
                self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")

    def _update_pressure_label_from_last_cursor(self):
        """Recompute pressure at the last‐seen cursor X, or show “—”."""
        # 1) Do we have any data?
        xdata = self._curve.xData
        if xdata is None or len(xdata) == 0:
            self.ui.label_current_pressure.setText("—")
            return

        # 2) Has the cursor ever been inside the plot?
        x = self._last_cursor_x
        if x is None:
            self.ui.label_current_pressure.setText("—")
            return

        # 3) Outside the curve’s full x‐range?
        xmin, xmax = float(xdata.min()), float(xdata.max())
        if x < xmin or x > xmax:
            self.ui.label_current_pressure.setText("—")
            return

        # 4) Safe to compute
        try:
            # feed the calculator
            self._calculator.set_measured_wavelength(x, 0.0)
            Tm = float(self.ui.lineEdit_measured_temperature_c.text() or 0.0)
            self._calculator.set_measured_temperature(Tm)
            p, _ = self._calculator.calculate_pressure()
            self.ui.label_current_pressure.setText(f"{p:.2f}")
        except Exception:
            # any parse error or divide‐by‐zero → fall back to em‑dash
            self.ui.label_current_pressure.setText("—")

    @Slot(bool)
    def _on_irradiance_toggled(self, checked: bool) -> None:
        """When the user checks/unchecks the irradiance box, validate or reset."""
        # always reset first if they turned it off
        if not checked:
            self._flags["irradiance"] = False
            self._irrad_coef = np.ones(self._pixel_count, dtype=float)
            return

        # defaults so that arr and valid always exist
        error: str | None = None
        valid = False
        arr: np.ndarray | None = None

        # 1) feature must exist
        feats = self._spec_ctrl.features.get("irrad_cal", [])
        if not feats:
            error = "Device does not support irradiance calibration."
        else:
            raw = feats[0].read_calibration()
            try:
                arr = np.array(raw, dtype=float)
            except Exception as e:
                error = f"Failed to parse calibration: {e}"
            else:
                # 2) length must match
                if arr.size != self._pixel_count:
                    error = f"Calibration length {arr.size} ≠ pixel count {self._pixel_count}"
                # 3) no NaNs
                elif not np.isfinite(arr).all():
                    n_nan = int(np.isnan(arr).sum())
                    error = f"Calibration contains {n_nan} NaN(s)"
                else:
                    valid = True

        # 4) rollback if invalid, then bail out
        if not valid:
            QMessageBox.warning(
                self,
                "Irradiance Calibration Error",
                f"{error}\nIrradiance calibration has been turned off."
            )
            cb = self.ui.checkBox_irradiance
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)

            self._flags["irradiance"] = False
            self._irrad_coef = np.ones(self._pixel_count, dtype=float)
            return

        # At this point we know valid is True and arr was assigned
        self._flags["irradiance"] = True
        self._irrad_coef = arr  # no more “might be referenced before assignment”

    @Slot()
    def _apply_auto_intensity_after_interaction(self) -> None:
        """
        After any pan/zoom completes, if auto‑scale is on, re‑scale Y
        to the data _within_ the current X view window.
        """
        if self.ui.checkBox_auto_intensity_scale.isChecked():
            self._plot_item.vb.scale_intensity()

    @Slot()
    def _check_resume(self) -> None:
        # If continuous mode is active but painting is paused, and no buttons pressed, resume
        if self.ui.pushButton_continuous.isChecked():
            if QApplication.mouseButtons() == Qt.NoButton and self._painting_paused:
                self._on_resume_painting()

    def _flush_plot(self):
        # allow the next flush
        self._flush_scheduled = False
        self._last_flush_time = time.perf_counter()

        if self._painting_paused or self._pending_spectrum is None:
            return

        wl, proc = self._pending_spectrum
        # update ONLY the live‐data curve
        self._curve.setData(wl, proc)
        self._pending_spectrum = None

        # re-auto-scale if desired
        if self.ui.checkBox_auto_intensity_scale.isChecked():
            self._plot_item.vb.scale_intensity()

        # enable manual‐fit only if we have data
        has_data = self._curve.xData is not None and len(self._curve.xData) > 0
        always_data_controls = [
            self.ui.pushButton_manual_fit,
            self.ui.pushButton_manual_voigt_fit,
            # NEW:
            self.ui.pushButton_full_range,
            self.ui.pushButton_zoom,
            self.ui.checkBox_autofit,
            self.ui.pushButton_fromview,
            self.ui.pushButton_zoom_to_range,
        ]
        for w in always_data_controls:
            w.setEnabled(has_data)

        # scale‑intensity is only clickable when we *have* data AND
        # auto‑intensity is OFF
        self.ui.pushButton_scale_intensity.setEnabled(
            has_data and not self.ui.checkBox_auto_intensity_scale.isChecked()
        )

        if self.ui.checkBox_autofit.isChecked():
            self._update_autofit_highlight()
            self._attempt_autofit()

    def _update_clear_fits_button(self) -> None:
        has_fit = (
                self._manual_locked  # manual single line locked
                or self._manual_voigt_locked  # pseudo‑Voigt locked
                or self.ui.checkBox_autofit.isChecked()  # auto‑fit mode on
        )
        self.ui.pushButton_clear_all_fits.setEnabled(has_fit)

    def _on_pause_painting(self):
        """Called when pan/zoom begins; stop all flushes until they finish."""
        self._painting_paused = True

    @Slot(str)
    def _on_pixel_binning_changed(self, txt: str) -> None:
        """Apply the newly-picked binning factor straight to the device."""
        try:
            factor = int(txt)
        except ValueError:
            return
        self._bin_size = factor
        if self._spec_ctrl:
            self._spec_ctrl.set_binning_factor(factor)

    def _on_resume_painting(self):
        self._painting_paused = False

        # 1 ms singleShot ensures we run *after* Qt finishes its current paint cycle
        #  → flush any buffered spectrum
        if self._pending_spectrum is not None:
            QTimer.singleShot(1, self._flush_plot)

    def _connect_signals(self):
        # device selection + refresh + defaults
        self.ui.pushButton_refresh_device.clicked.connect(lambda: self._refresh_devices(False))
        self.ui.comboBox_devices.currentIndexChanged.connect(self._on_device_selected)
        self.ui.pushButton_defaults_device.clicked.connect(self._save_defaults)
        self.ui.pushButton_optimize.clicked.connect(self._on_optimize_clicked)

        # corrections → flip flags
        mapping = {
          self.ui.checkBox_electric_dark:   "electric_dark",
          self.ui.checkBox_optical_dark:    "optical_dark",
          self.ui.checkBox_stray_light_correction: "stray_light",
          self.ui.checkBox_non_linearity:   "non_linearity",
        }
        for widget, name in mapping.items():
            widget.toggled.connect(lambda chk, n=name: self._flags.__setitem__(n, chk))

        self.ui.checkBox_irradiance.toggled.connect(self._on_irradiance_toggled)

        # boxcar / pixel‐binning
        self.ui.checkBox_boxcar_smooth.toggled.connect(lambda chk: self._flags.__setitem__("boxcar", chk))
        self.ui.spinBox_boxcar_smooth.valueChanged.connect(lambda v: setattr(self, "_boxcar_width", v))
        self.ui.checkBox_pixel_binning.toggled.connect(lambda chk: self._flags.__setitem__("pixel_binning", chk))
        self.ui.comboBox_pixel_binning.currentTextChanged.connect(lambda t: setattr(self, "_bin_size", int(t)))

        self.ui.comboBox_pixel_binning.currentTextChanged.connect(self._on_pixel_binning_changed)

        # clear-everything button
        self.ui.pushButton_clear_all_fits.clicked.connect(self._on_clear_all_fits)

        # temperature & EEPROM expanders
        self.ui.groupBox_4.toggled.connect(self._on_temp_group_toggled)
        self.ui.groupBox_eeprominfo.toggled.connect(self._on_eeprom_group_toggled)

        # TEC enable / setpoint / tab‑change
        self.ui.checkBox_thermoelectric_enable.toggled.connect(self._on_tec_toggled)
        self.ui.spinBox_tec_temp_setpoint.valueChanged.connect(self._on_tec_setpoint_changed)
        self.ui.tabWidget_all.currentChanged.connect(self._on_tab_changed)

        # full‑range button → reset both axes
        self.ui.pushButton_full_range.clicked.connect(self._plot_item.vb.full_range)

        # zoom button → toggle rectangle‑zoom mode
        self.ui.pushButton_zoom.toggled.connect(self._plot_item.vb.enable_zoom_mode)

        # auto‑intensity checkbox → flag and one‑off apply
        self.ui.checkBox_auto_intensity_scale.toggled.connect(self._on_auto_intensity_toggled)

        # one‑off “Scale Intensity” button
        self.ui.pushButton_scale_intensity.clicked.connect(self._plot_item.vb.scale_intensity)

        # pixel-binning dropdown → apply immediately to hardware
        self.ui.comboBox_pixel_binning.currentTextChanged.connect(
        self._on_pixel_binning_changed
        )

        # make sure the one‑off button reflects initial checkbox state
        self.ui.pushButton_scale_intensity.setEnabled(
            not self.ui.checkBox_auto_intensity_scale.isChecked()
        )

        self.ui.checkBox_autofit.toggled.connect(self._on_autofit_toggled)

        self.ui.pushButton_zoom_to_range.clicked.connect(self._on_zoom_to_range_clicked)

    @Slot()
    def _attempt_autofit(self) -> None:
        """
        If Auto-fit is checked, run two-peak Voigt between [lo,hi],
        then plot *each* peak (R1 in blue, R2 in red) only in that window,
        and use R1’s center to update pressure.
        """
        # 1) only when Auto-fit is on
        if not self.ui.checkBox_autofit.isChecked():
            return

        # 1) already running?  just remember that we need one more pass
        if self._auto_fit_running:
            self._auto_fit_pending = True
            return

        # 2) grab full-spectrum data
        wl = self._curve.xData
        cnt = self._curve.yData
        if wl is None or cnt is None or wl.size < 5:
            return

        # 3) fitting window
        lo = self.ui.doubleSpinBox_min_fitting_range_nm.value()
        hi = self.ui.doubleSpinBox_max_fitting_range_nm.value()

        # 3) mark that we’re busy *before* starting the thread
        self._auto_fit_running = True

        # spawn a new background fit
        self._auto_worker = AutoFitWorker(wl, cnt, lo, hi)
        self._auto_thread = QThread(self)
        self._auto_worker.moveToThread(self._auto_thread)
        self._auto_thread.started.connect(self._auto_worker.run)
        self._auto_worker.fit_finished.connect(self._on_auto_fit_finished)
        # optionally handle failures:
        self._auto_worker.fit_failed.connect(lambda: None)
        self._auto_thread.start()

    @Slot()
    def _on_auto_fit_failed(self):
        # same clean‑up as success
        self._auto_fit_running = False
        if self._auto_thread:
            self._auto_thread.quit()
            self._auto_thread.wait()

        # schedule one more pass if something arrived meanwhile
        if self._auto_fit_pending:
            self._auto_fit_pending = False
            QTimer.singleShot(0, self._attempt_autofit)

    @Slot(object, object)
    def _on_auto_fit_finished(self, popt, pcov) -> None:
        # R1 parameters
        c1 = popt[0]
        amp1 = popt[1]
        fwhm1 = popt[2]
        frac1 = popt[3]

        # δ = R1–R2 separation
        delta = popt[4]

        # R2 parameters
        r2_center = c1 - delta
        amp2 = popt[5]
        fwhm2 = popt[6]
        frac2 = popt[7]

        # 1) draw overlay
        lo = self.ui.doubleSpinBox_min_fitting_range_nm.value()
        hi = self.ui.doubleSpinBox_max_fitting_range_nm.value()
        wl = self._curve.xData
        mask = (wl >= lo) & (wl <= hi)
        sel = wl[mask]
        xs = np.linspace(sel.min(), sel.max(), sel.size * 4)
        ys = AutoFit.two_peak_model(xs, *popt)
        self._auto_model_curve.setData(xs, ys)
        self._auto_model_curve.show()

        # 2) mark R1 line
        self._auto_voigt_line.setPos(c1)
        self._auto_voigt_line.setVisible(True)

        # 3) update measured‐wavelength & live‐pressure
        self.ui.lineEdit_measured_wavelength_nm.setText(f"{c1:.3f}")
        sigma1 = sqrt(pcov[0, 0])
        self._apply_fit(c1, sigma1, "green")

        self._r2_voigt_line.setPos(r2_center)
        self._r2_voigt_line.setVisible(True)

        # 4) stash for the “Add” step
        self._last_fit_type = "Auto-fit Voigt"
        self._last_voigt_popt = [c1, amp1, fwhm1, frac1]
        self._last_voigt_pcov = pcov[0:4, 0:4].tolist()
        self._last_r2_wavelength = r2_center
        self._last_r2_voigt_popt = [r2_center, amp2, fwhm2, frac2]
        # extract the 4×4 block for (c1↔r2,amp2,fwhm2,frac2):
        idxs = [0, 5, 6, 7]
        self._last_r2_voigt_pcov = pcov[np.ix_(idxs, idxs)].tolist()

        self._last_baseline = popt[8]

        # 5) re‐scale if needed
        self._apply_auto_intensity_after_interaction()

        self._auto_fit_running = False
        if self._auto_thread:
            self._auto_thread.quit()
            self._auto_thread.wait()

        # If a newer spectrum appeared while we were fitting,
        # run once more (immediately) on that latest data.
        if self._auto_fit_pending:
            self._auto_fit_pending = False
            QTimer.singleShot(0, self._attempt_autofit)

    @Slot(bool)
    def _on_autofit_toggled(self, checked: bool):
        if checked:
            if self.ui.pushButton_manual_voigt_fit.isChecked() or self._manual_voigt_locked:
                # stop live timer, clear overlays, unlock
                self._manual_voigt_timer.stop()
                self._manual_voigt_curve.clear()
                self._manual_voigt_line.setVisible(False)
                self._manual_voigt_locked = False
                # silently un‑tick the button
                self.ui.pushButton_manual_voigt_fit.blockSignals(True)
                self.ui.pushButton_manual_voigt_fit.setChecked(False)
                self.ui.pushButton_manual_voigt_fit.blockSignals(False)

                # -- Manual‑follow -----------------------------------------------
            if self.ui.pushButton_manual_fit.isChecked() or self._manual_locked:
                self._manual_line.setVisible(False)
                self._manual_locked = False
                self.ui.pushButton_manual_fit.blockSignals(True)
                self.ui.pushButton_manual_fit.setChecked(False)
                self.ui.pushButton_manual_fit.blockSignals(False)

                # reset result label (will be updated by Auto‑fit itself)
            self.ui.label_result_pressure_gpa.setText("—")
            self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
            # hide the mono‐curve and show the split ones
            self._curve.hide()
            self._curve_inside.show()
            self._curve_outside.show()
            # immediately color the existing spectrum
            self._update_autofit_highlight()
            # attempt auto fit immediately if we have data
            wl = getattr(self._curve, 'xData', None)
            cnt = getattr(self._curve, 'yData', None)
            self._update_clear_fits_button()
            if wl is not None and cnt is not None and len(wl) > 0:
                self._attempt_autofit()
        else:
            # restore single white curve
            self._curve.show()
            self._curve_inside.hide()
            self._curve_outside.hide()
            # clear any existing auto fit overlays/result
            self._auto_model_curve.hide()
            self._auto_voigt_line.setVisible(False)
            self._r2_voigt_line.setVisible(False)
            # disable add measurement until next fit
            self._update_add_measurement_enable()
            self.ui.label_result_pressure_gpa.setText("—")
            self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
            self.ui.lineEdit_measured_wavelength_nm.clear()
            self._update_clear_fits_button()
            if self._auto_thread and self._auto_thread.isRunning():
                self._auto_worker.stop()
                self._auto_thread.quit()
                self._auto_thread.wait()
            self._auto_fit_running = False
            self._auto_fit_pending = False
            self._reset_last_fit_metadata()

    def _update_autofit_highlight(self):
        x = self._curve.xData
        y = self._curve.yData
        if x is None or y is None:
            return

        lo = self.ui.doubleSpinBox_min_fitting_range_nm.value()
        hi = self.ui.doubleSpinBox_max_fitting_range_nm.value()
        inside = (x >= lo) & (x <= hi)

        # inside segment ─ keep y where ‘inside’, mask everything else
        y_inside = y.copy()
        y_inside[~inside] = np.nan
        self._curve_inside.setData(x, y_inside, connect='finite')

        # outside segment ─ the complement of the above
        y_outside = y.copy()
        y_outside[inside] = np.nan
        self._curve_outside.setData(x, y_outside, connect='finite')

    # ------------------------------------------------------------------#
    # clear-all-fits helper                                             #
    # ------------------------------------------------------------------#
    @Slot()
    def _on_clear_all_fits(self) -> None:
        """
        • Leave whatever acquisition is running untouched.
        • Exit *either* fitting mode if it’s on.
        • Remove *all* fit overlays/locks from the plot.
        • Reset the pressure read-out to an em-dash and
          disable the “Add” button until a new fit is made.
        """

        # ------------------------------------------------------------------
        # 1) Pop out of live-fitting modes (let their own slots clean up)
        # ------------------------------------------------------------------
        if self.ui.pushButton_manual_voigt_fit.isChecked():
            self.ui.pushButton_manual_voigt_fit.setChecked(False)   # triggers its toggled-slot
        if self.ui.pushButton_manual_fit.isChecked():
            self.ui.pushButton_manual_fit.setChecked(False)         # triggers its toggled-slot

        # ------------------------------------------------------------------
        # 2) Make absolutely sure *everything* visual is gone even if the
        #    buttons were already unchecked but a lock was still present.
        # ------------------------------------------------------------------
        self._manual_voigt_timer.stop()
        self._manual_voigt_curve.clear()
        self._manual_voigt_line.setVisible(False)
        self._manual_line.setVisible(False)
        self._r2_voigt_line.setVisible(False)

        self._manual_voigt_locked = False
        self._manual_locked = False
        self._last_voigt_popt = None
        self._last_voigt_pcov = None
        self._last_manual_pos = None

        self.ui.checkBox_autofit.setChecked(False)
        self._auto_model_curve.setVisible(False)
        self._auto_voigt_line.setVisible(False)

        # ------------------------------------------------------------------
        # 3) Reset GUI elements that depend on a fit
        # ------------------------------------------------------------------
        self.ui.label_result_pressure_gpa.setText("—")
        self.ui.label_result_pressure_gpa.setStyleSheet("color: red;")
        self.ui.lineEdit_measured_wavelength_nm.clear()

        # “Add measurement” no longer makes sense until another fit happens
        self._update_add_measurement_enable()
        self._update_clear_fits_button()
        self._reset_last_fit_metadata()

    def _apply_fit(self, center: float, sigma: float, color: str):
        # 1) feed measured λ & error
        self._calculator.set_measured_wavelength(center, sigma)
        # 2) feed measured temperature
        try:
            Tm = float(self.ui.lineEdit_measured_temperature_c.text())
        except ValueError:
            return
        self._calculator.set_measured_temperature(Tm)

        # 3) compute pressure
        try:
            p, sigma_p = self._calculator.calculate_pressure()
        except ValueError:
            return

        # 4) update display
        self.ui.label_result_pressure_gpa.setText(f"{p:.2f} ±{sigma_p:.2f}")
        self.ui.label_result_pressure_gpa.setStyleSheet(f"color: {color};")
        self._update_add_measurement_enable()

    def _reset_last_fit_metadata(self) -> None:
        """Clear all attributes that describe the most-recent fit."""
        self._last_fit_type = None
        self._last_voigt_popt = None
        self._last_voigt_pcov = None
        self._last_r2_wavelength = None
        self._last_r2_voigt_popt = None
        self._last_r2_voigt_pcov = None
        self._last_baseline = None

    def _refresh_locked_fit(self) -> None:
        """
        Re-run the pressure calculation for whichever fit is currently shown
        (manual line, manual Voigt, or Auto-fit Voigt) after any external
        parameter change such as a new pressure-calibration selection.
        """
        center: float | None = None
        sigma: float = 0.0           # σ_λ (nm)

        # -- Manual Voigt lock ------------------------------------------
        if self._manual_voigt_locked:
            center = self._manual_voigt_line.value()
            if self._last_voigt_pcov is not None:
                sigma = math.sqrt(self._last_voigt_pcov[0][0])

        # -- Manual single-line lock ------------------------------------
        elif self._manual_locked:
            center = self._manual_line.value()   # σ = 0 for a single data-point

        # -- Auto-fit Voigt (NEW) ---------------------------------------
        elif self.ui.checkBox_autofit.isChecked() and self._last_voigt_pcov is not None:
            try:
                center = float(self.ui.lineEdit_measured_wavelength_nm.text())
            except ValueError:
                center = None
            else:
                sigma = math.sqrt(self._last_voigt_pcov[0][0])

        # Re-apply if we found a valid wavelength
        if center is not None:
            self._apply_fit(center, sigma, "green")

    @Slot()
    def _on_optimize_clicked(self) -> None:
        # Collect the current UI flags
        flags = {
            "electric_dark": self.ui.checkBox_electric_dark.isChecked(),
            "optical_dark": self.ui.checkBox_optical_dark.isChecked(),
            "stray_light": self.ui.checkBox_stray_light_correction.isChecked(),
            "non_linearity": self.ui.checkBox_non_linearity.isChecked(),
            "irradiance": self.ui.checkBox_irradiance.isChecked(),
            "boxcar": self.ui.checkBox_boxcar_smooth.isChecked(),
            "pixel_binning": self.ui.checkBox_pixel_binning.isChecked(),
        }

        # Ask the AcquisitionManager to run the optimiser dialog
        t95 = self._acq_mgr.run_optimize(
            flags=flags,
            boxcar_width=self._boxcar_width,
            bin_size=self._bin_size,
            odark_ranges=self._odark,
            sl_coef=self._sl_coef,
            irrad_coef=self._irrad_coef,
            parent=self,
        )

        # If a recommendation was returned, push it into the spin‑box
        if t95 is not None:
            label_shows_seconds = "(s)" in self.ui.label_integrationtime.text()
            value = t95 / 1_000.0 if label_shows_seconds else t95
            self.ui.doubleSpinBox_integration_time_ms.setValue(value)

    @staticmethod
    def _next_integer_name(occupied: set[str], folder: Path | None) -> str:
        """Return the lowest positive integer (as a string) not already taken."""
        i = 1
        while (
                str(i) in occupied or
                (folder is not None and (folder / f"{i}.txt").exists())
        ):
            i += 1
        return str(i)

    @Slot()
    def _on_add_measurement(self):
        # ------------------------------------------------------------------
        # 1) Resolve a unique, file-safe name
        # ------------------------------------------------------------------
        user_raw = self.ui.lineEdit_measurement_name.text().strip()
        autosave_folder = self._measurement_manager._auto_save_folder
        existing = {r.name for r in self._measurement_manager._measurements}

        if user_raw:
            base = self._sanitize_name(user_raw)
            # If sanitising leaves us with an empty string, treat as “no name”
            if base:
                name = self._unique_name(base, existing, autosave_folder)
            else:
                name = self._next_integer_name(existing, autosave_folder)
        else:
            name = self._next_integer_name(existing, autosave_folder)

        # ------------------------------------------------------------------
        # 2) Build the MeasurementRecord (unchanged except for *name*)
        # ------------------------------------------------------------------
        r1_wl = float(self.ui.lineEdit_measured_wavelength_nm.text())
        pressure = self.ui.label_result_pressure_gpa.text()
        temp = self.ui.lineEdit_measured_temperature_c.text()
        pcal = self.ui.comboBox_pressurecalibrations.currentText()
        tcal = self.ui.comboBox_temperaturecalibrations.currentText()

        x_data = getattr(self._curve, "xData", None)
        y_data = getattr(self._curve, "yData", None)
        x = np.array(x_data) if x_data is not None else np.array([])
        y = np.array(y_data) if y_data is not None else np.array([])

        lbl = self.ui.label_integrationtime.text()
        val = self.ui.doubleSpinBox_integration_time_ms.value()
        integ_ms = float(val) if "(ms)" in lbl else float(val) * 1000.0
        scans = self.ui.spinBox_scansaverage.value()

        ref_wl = float(self.ui.lineEdit_reference_wavelength_nm.text())
        ref_tmp = float(self.ui.lineEdit_reference_temperature_c.text())
        spec_id = self._spec_ctrl.device_id

        fit_type = getattr(self, "_last_fit_type", "Manual")
        r1_popt = None
        r1_pcov = None
        r2_center = None
        r2_popt = None
        r2_pcov = None
        baseline = getattr(self, '_last_baseline', None)

        if fit_type == "Auto-fit Voigt":
            r1_popt = self._last_voigt_popt
            r1_pcov = self._last_voigt_pcov
            r2_center = self._last_r2_wavelength
            r2_popt = self._last_r2_voigt_popt
            r2_pcov = self._last_r2_voigt_pcov
        elif fit_type == "Manual Voigt":
            r1_popt = self._last_voigt_popt
            r1_pcov = self._last_voigt_pcov

        rec = MeasurementRecord(
            name=name,
            r1_wavelength=r1_wl,
            pressure=pressure,
            temperature=temp,
            pressure_calib=pcal,
            temp_calib=tcal,
            x_wavelength=x,
            y_intensity=y,
            integration_time_ms=integ_ms,
            scans=scans,
            reference_wavelength=ref_wl,
            reference_temperature=ref_tmp,
            spectrometer_id=spec_id,
            fit_type=fit_type,
            voigt_popt=r1_popt,
            voigt_pcov=r1_pcov,
            r2_wavelength=r2_center,
            r2_voigt_popt=r2_popt,
            r2_voigt_pcov=r2_pcov,
            baseline=baseline,
        )

        # ------------------------------------------------------------------
        # 3) Add & auto-save via the manager
        # ------------------------------------------------------------------
        self._measurement_manager.add(rec)

    def _on_auto_intensity_toggled(self, checked: bool) -> None:
        """
        When the user clicks the “Auto scale intensity” checkbox, if they
        turn it on we immediately scale the Y axis to the last data.
        (And on each new spectrum we’ll do it again in _flush_plot.)
        :param checked:
        :return:
        """

        # disable the one‑off button whenever auto‑mode is on
        self.ui.pushButton_scale_intensity.setEnabled(not checked)

        # on‑demand apply
        if checked:
            self._plot_item.vb.scale_intensity()

    def _setup_integration_widgets(self):
        # watch clicks on the spinbox *and* on the label
        self.ui.doubleSpinBox_integration_time_ms.installEventFilter(self)
        self.ui.label_integrationtime.installEventFilter(self)

    def _refresh_devices(self, first_time: bool=False):
        devs = SpectrometerController.list_devices()
        last = self._qt.value("last_selected_device", "")
        self.ui.comboBox_devices.clear()
        for d in devs:
            ctrl = SpectrometerController(d)
            self.ui.comboBox_devices.addItem(ctrl.device_id, d)

        idx = 0
        if first_time:
            saved = self._sm.get_last_selected()
            last = last or saved
        for i in range(self.ui.comboBox_devices.count()):
            if self.ui.comboBox_devices.itemText(i) == last:
                idx = i
                break
        self.ui.comboBox_devices.setCurrentIndex(idx)

    @Slot(int)
    def _on_device_selected(self, idx: int):
        if idx < 0: return
        raw_dev = self.ui.comboBox_devices.itemData(idx)
        did = self.ui.comboBox_devices.currentText()
        self._qt.setValue("last_selected_device", did)
        self._sm.set_last_selected(did)

        # reset temp plot
        self._temp_timer.stop()
        self._temp_data.clear()
        self.ui.widget_temperatureplot.clear()

        self._spec_ctrl = SpectrometerController(raw_dev)

        if self._acq_mgr is None:
            self._acq_mgr = AcquisitionController(self._spec_ctrl, parent=self)
            self._setup_acquisition_connections()
        else:
            # swap in new controller on device change
            self._acq_mgr.set_spectrometer(self._spec_ctrl)

        # integration limits
        mn, mx = self._spec_ctrl.integration_limits_us
        self.ui.doubleSpinBox_integration_time_ms.setRange(math.ceil(mn/1_000), mx//1_000)
        # default to 100 ms (or the max if the device can't do that)
        default_ms = min(100, mx // 1_000)

        self.ui.doubleSpinBox_integration_time_ms.setValue(default_ms)

        max_scans = self.ui.spinBox_scansaverage.maximum()
        self.ui.spinBox_scansaverage.setRange(1, max_scans)
        self.ui.spinBox_scansaverage.setValue(1)

        # grab all introspection & calibration data in one shot
        self._grab_feature_data()

        # enable/disable relevant UI
        self._apply_feature_enables()

        # populate the pixel‑binning combobox
        self._populate_pixel_binning_options()

        # load JSON defaults or pick sane ones
        saved = self._sm.get_device_settings(did)
        if saved:
            self._apply_saved_settings(saved)
        else:
            # no saved settings → start *all* corrections OFF
            for name, widget in (
                    ("electric_dark", self.ui.checkBox_electric_dark),
                    ("optical_dark", self.ui.checkBox_optical_dark),
                    ("stray_light", self.ui.checkBox_stray_light_correction),
                    ("non_linearity", self.ui.checkBox_non_linearity),
                    ("irradiance", self.ui.checkBox_irradiance),
            ):
                widget.setChecked(False)
                self._flags[name] = False

            # also reset boxcar & binning controls if you like:
            self.ui.spinBox_boxcar_smooth.setValue(1)
            self._boxcar_width = 1
            self.ui.comboBox_pixel_binning.setCurrentText("1")
            self._bin_size = 1

            # and TEC off
            self.ui.checkBox_thermoelectric_enable.setChecked(False)

        self._populate_device_information()
        # ensure our UI checkbox state is actually applied to the hardware TEC
        self._on_tec_toggled(self.ui.checkBox_thermoelectric_enable.isChecked())

    def _populate_pixel_binning_options(self) -> None:
        """Fill comboBox_pixel_binning with 1…max and select default or saved."""
        combo = self.ui.comboBox_pixel_binning
        combo.clear()

        feats = self._spec_ctrl.features.get("pixel_binning", [])

        if not feats:
            combo.setEnabled(False)
            return
        combo.setEnabled(True)

        feat = feats[0]
        max_f     = feat.get_max_binning_factor()
        default_f = feat.get_default_binning_factor()

        for f in range(1, max_f + 1):
            combo.addItem(str(f))

        # if the user has saved a custom setting, pick that; else pick device default
        saved = self._sm.get_device_settings(self._spec_ctrl.device_id)
        pick  = saved.get("bins", default_f)
        idx   = combo.findText(str(pick))
        if idx < 0:
            idx = combo.findText(str(default_f))
        combo.setCurrentIndex(idx)

    def _grab_feature_data(self):
        f = self._spec_ctrl.features

        # electric & optical dark pixel ranges
        self._edark = []
        self._odark = []
        self._active_pixels = []

        # find whichever feature implements the dark‑pixel APIs
        introspection_feat = None
        for feat_list in f.values():
            for feat in feat_list:
                if hasattr(feat, "get_electric_dark_pixel_ranges"):
                    introspection_feat = feat
                    break
            if introspection_feat:
                break

        if introspection_feat:
            # these return flat tuples: (lo0, hi0, lo1, hi1, …)
            edark = introspection_feat.get_electric_dark_pixel_ranges()
            odark = introspection_feat.get_optical_dark_pixel_ranges()
            active = introspection_feat.get_active_pixel_ranges()

            # helper: split a flat tuple into [(lo,hi), …]
            def _make_ranges(tup):
                return [(tup[i], tup[i + 1]) for i in range(0, len(tup), 2)]

            self._edark = _make_ranges(edark)
            self._odark = _make_ranges(odark)
            self._active_pixels = _make_ranges(active)

        # non‑linearity
        if f.get("nonlinearity_coefficients"):
            fl = f["nonlinearity_coefficients"][0]
            self._nl_coef = np.array(fl.get_nonlinearity_coefficients(), float)
        else:
            self._nl_coef = np.ones(1)

        # stray‑light
        if f.get("stray_light_coefficients"):
            fl = f["stray_light_coefficients"][0]
            self._sl_coef = np.array(fl.get_stray_light_coefficients(), float)
        else:
            self._sl_coef = np.zeros(1)

        # irradiance
        if f.get("irrad_cal"):
            fl = f["irrad_cal"][0]
            self._irrad_coef = np.array(fl.read_calibration(), float)
        else:
            self._irrad_coef = np.ones(1)

    def _apply_feature_enables(self):
        f = self._spec_ctrl.features

        self.ui.checkBox_electric_dark.setEnabled(True)
        self.ui.checkBox_optical_dark.setEnabled(bool(self._odark))
        self.ui.checkBox_stray_light_correction.setEnabled(bool(f.get("stray_light_coefficients")))
        self.ui.checkBox_non_linearity.setEnabled(bool(f.get("nonlinearity_coefficients")))
        self.ui.checkBox_irradiance.setEnabled(bool(f.get("irrad_cal")))

        # For each correction checkbox, enable only if the feature exists,
        # and set a tooltip on the disabled ones.
        mapping = {
            self.ui.checkBox_electric_dark: True,
            self.ui.checkBox_optical_dark: bool(self._odark),
            self.ui.checkBox_stray_light_correction: bool(f.get("stray_light_coefficients")),
            self.ui.checkBox_non_linearity: bool(f.get("nonlinearity_coefficients")),
            self.ui.checkBox_irradiance: bool(f.get("irrad_cal")),
        }

        for checkbox, is_supported in mapping.items():
            checkbox.setEnabled(is_supported)
            checkbox.setToolTip(
                "" if is_supported else "This correction is not supported by your spectrometer"
            )

        sp = self.ui.checkBox_boxcar_smooth
        sp.setEnabled(bool(f.get("spectrum_processing")))
        self.ui.spinBox_boxcar_smooth.setEnabled(sp.isEnabled())

        pb = self.ui.checkBox_pixel_binning
        pb.setEnabled(bool(f.get("pixel_binning")))

        self.ui.comboBox_pixel_binning.setEnabled(pb.isEnabled())

        self.ui.checkBox_thermoelectric_enable.setEnabled(bool(f.get("thermo_electric")))
        self._update_tec_ui(self.ui.checkBox_thermoelectric_enable.isChecked())

        self.ui.groupBox_4.setEnabled(True)

        ee = self.ui.groupBox_eeprominfo
        ee.setEnabled(bool(f.get("eeprom")))

    # ——————————————————— process & plot ———————————————————
    @Slot(np.ndarray, np.ndarray)
    def _on_spectrum_ready(self, wl: np.ndarray, raw_counts: np.ndarray) -> None:
        """
        Receive a freshly acquired spectrum, apply all user‑selected
        corrections, subtract any stored background held in
        AcquisitionManager, then queue a (throttled) plot update.
        """
        self._last_raw_counts = raw_counts

        if self._last_wl is None or self._last_wl.shape != wl.shape:
            self._last_wl = wl
            if not self._fitting_range_initialized:
                self.ui.doubleSpinBox_min_fitting_range_nm.setRange(wl.min(), wl.max())
                self.ui.doubleSpinBox_max_fitting_range_nm.setRange(wl.min(), wl.max())
                self.ui.doubleSpinBox_min_fitting_range_nm.setValue(wl.min())
                self.ui.doubleSpinBox_max_fitting_range_nm.setValue(wl.max())
                self._fitting_range_initialized = True
        wl_ref = self._last_wl  # always plot with the cached array

        # ────────────────────────────────────────────────
        # 3 .  Build the processed counts array
        # ────────────────────────────────────────────────
        proc = raw_counts.astype(float)

        # Optical‑dark correction
        if self._flags["optical_dark"]:
            for lo, hi in self._odark:
                proc -= proc[lo:hi].mean()

        # Stray‑light polynomial
        if self._flags["stray_light"]:
            x = np.arange(proc.size)
            proc -= np.polyval(self._sl_coef[::-1], x)

        # Irradiance calibration
        if self._flags["irradiance"]:
            proc *= self._irrad_coef

        # Boxcar smoothing
        if self._flags["boxcar"] and self._boxcar_width > 1:
            window = np.ones(self._boxcar_width) / self._boxcar_width
            proc = np.convolve(proc, window, mode="same")

        # Background subtraction — fetch from the manager
        bg = self._acq_mgr.last_background  # (wl_bg, counts_bg) or None
        if bg is not None and bg[1].shape == proc.shape:
            proc -= bg[1]

        # ────────────────────────────────────────────────
        # 4 .  Queue a redraw (max ~60 Hz) with flushing logic
        # ────────────────────────────────────────────────
        self._pending_spectrum = (wl_ref, proc)
        if not self._painting_paused and not self._flush_scheduled:
            now = time.perf_counter()
            elapsed = now - self._last_flush_time
            delay_ms = max(0, int((0.016 - elapsed) * 1000))  # target ≥ ~16 ms per frame
            self._flush_scheduled = True
            QTimer.singleShot(delay_ms, self._flush_plot)

    # ——————————————————— temperature ———————————————————
    @Slot(bool)
    def _on_temp_group_toggled(self, chk: bool):
        # show/hide the PlotWidget
        self.ui.widget_temperatureplot.setVisible(chk)

        if chk:
            # lock X to 0…300 and invert so “0 s ago” is on the right
            plot_item = self.ui.widget_temperatureplot.getPlotItem()
            vb = plot_item.getViewBox()
            vb.enableAutoRange(False)
            vb.setXRange(0, 300, padding=0)
            vb.invertX(True)

            # clear old data, draw one point immediately, then start timer
            self._temp_data.clear()
            self._sample_temperature()
            self._temp_timer.start()
        else:
            self._temp_timer.stop()
            self.ui.widget_temperatureplot.clear()

    @Slot()
    def _sample_temperature(self):
        # pull from the same “thermo_electric” feature that your label uses
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if not feat_list:
            return

        try:
            temp = float(feat_list[0].read_temperature_degrees_celsius())
        except Exception:
            return

        now = time.time()
        self._temp_data.append((now, temp))
        cutoff = now - 300
        # drop anything older than 5 min
        while self._temp_data and self._temp_data[0][0] < cutoff:
            self._temp_data.popleft()

        # build “seconds ago” on X
        times, temps = zip(*self._temp_data)
        ages = [now - t for t in times]

        # plot with clear=True so it's exactly one curve
        w = self.ui.widget_temperatureplot
        w.plot(ages, temps, clear=True)
        w.setLabel("bottom", "Time (s ago)")
        w.setLabel("left", "°C")

    # ——————————————————— EEPROM ———————————————————
    @Slot(bool)
    def _on_eeprom_group_toggled(self, checked: bool):
        """Show/hide and populate the EEPROM table view."""
        tv = self.ui.tableView_eeprom
        tv.setVisible(checked)
        if not checked:
            return

        spec = self._spec_ctrl._spec
        # Explanations for each EEPROM slot
        slot_explanations = {
            0: "Serial Number",
            1: "Wavelength calibration c0 (intercept)",
            2: "Wavelength calibration c1 (linear term)",
            3: "Wavelength calibration c2 (quadratic term)",
            4: "Wavelength calibration c3 (cubic term)",
            5: "Stray light constant",
            6: "Non-linearity correction coeff (0th order)",
            7: "Non-linearity correction coeff (1st order)",
            8: "Non-linearity correction coeff (2nd order)",
            9: "Non-linearity correction coeff (3rd order)",
            10: "Non-linearity correction coeff (4th order)",
            11: "Non-linearity correction coeff (5th order)",
            12: "Non-linearity correction coeff (6th order)",
            13: "Non-linearity correction coeff (7th order)",
            14: "Non-linearity polynomial order",
            15: "Grating/filter/slit configuration",
            16: "Detector serial number",
            17: "TEC & fan settings",
        }

        model = QStandardItemModel(0, 3, self)
        model.setHorizontalHeaderLabels(["Slot", "Value", "Explanation"])

        for slot in range(256):
            try:
                raw = spec.f.eeprom.eeprom_read_slot(slot)
            except SeaBreezeError:
                break
            except Exception:
                break

            # Format value, with special handling for slot 17
            if isinstance(raw, (bytes, bytearray)) and slot == 17:
                b = raw
                tec_on = bool(b[0]) if len(b) > 0 else False
                fan_on = bool(b[1]) if len(b) > 1 else False
                # Detector temperature setpoint (tenths of °C)
                setpoint = None
                if len(b) >= 4:
                    sp_raw = int.from_bytes(b[2:4], 'little', signed=False)
                    setpoint = sp_raw / 10.0
                # Saturation intensity threshold (raw counts)
                threshold = None
                if len(b) >= 8:
                    threshold = int.from_bytes(b[4:8], 'little', signed=False)

                parts = [f"TEC={'on' if tec_on else 'off'}",
                         f"Fan={'on' if fan_on else 'off'}"]
                if setpoint is not None:
                    parts.append(f"Setpoint={setpoint} °C")
                if threshold is not None:
                    parts.append(f"SaturationThreshold={threshold}")
                val = ", ".join(parts)
            elif isinstance(raw, (bytes, bytearray)):
                # ASCII string for other slots
                val = raw.rstrip(b"\x00").decode("ascii", errors="ignore")
            else:
                val = str(raw).rstrip("\x00")

            explanation = slot_explanations.get(slot, "")

            # Create non-editable items
            item_slot = QStandardItem(str(slot))
            item_slot.setEditable(False)
            item_val = QStandardItem(val)
            item_val.setEditable(False)
            item_expl = QStandardItem(explanation)
            item_expl.setEditable(False)

            model.appendRow([item_slot, item_val, item_expl])

        tv.setModel(model)
        tv.resizeColumnsToContents()
        tv.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tv.verticalHeader().setVisible(False)
        tv.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # ————————————————— defaults persistence —————————————————
    def _save_defaults(self):
        did = self._spec_ctrl.device_id
        cfg = {
            "electric_dark":    self.ui.checkBox_electric_dark.isChecked(),
            "optical_dark":     self.ui.checkBox_optical_dark.isChecked(),
            "stray_light":      self.ui.checkBox_stray_light_correction.isChecked(),
            "non_linearity":    self.ui.checkBox_non_linearity.isChecked(),
            "irradiance":       self.ui.checkBox_irradiance.isChecked(),
            "boxcar_width":     self._boxcar_width,
            "bins":             self._bin_size,
            "thermoelectric":   self.ui.checkBox_thermoelectric_enable.isChecked(),
            "temp_setpoint": self.ui.spinBox_tec_temp_setpoint.value()
        }

        try:
            ref_wl = float(self.ui.lineEdit_reference_wavelength_nm.text())
        except ValueError:
            ref_wl = DEFAULT_REF_WL

        if abs(ref_wl - DEFAULT_REF_WL) > 1e-6:
            cfg["reference_wavelength"] = ref_wl
        else:
            # If user reverted to 694.22 nm, delete any custom value
            cfg.pop("reference_wavelength", None)

        self._sm.set_device_settings(did, cfg)

    def _apply_saved_settings(self, saved: dict):
        """
        Restore per‑device defaults into the UI.
        We treat “irradiance” specially so that
        1) loading from JSON doesn’t pop our guard dialog
        2) we still validate the array and turn it off if invalid
        """

        # 0)  Per-device reference wavelength  ← NEW
        if "reference_wavelength" in saved:
            ref_wl = float(saved["reference_wavelength"])
        else:
            ref_wl = DEFAULT_REF_WL

        # Only change the field if it differs from what is already displayed
        if abs(ref_wl - float(self.ui.lineEdit_reference_wavelength_nm.text() or 0.0)) > 1e-6:
            self.ui.lineEdit_reference_wavelength_nm.setText(f"{ref_wl:.5f}")
            self._calculator.set_reference_wavelength(ref_wl)
            # If a fit is currently locked, recompute its pressure read-out
            self._refresh_locked_fit()


        # 1) Apply all flags *except* irradiance
        mapping = {
            "electric_dark": "checkBox_electric_dark",
            "optical_dark": "checkBox_optical_dark",
            "stray_light": "checkBox_stray_light_correction",
            "non_linearity": "checkBox_non_linearity",
        }
        for key, widget_name in mapping.items():
            if saved.get(key, None) is not None and hasattr(self.ui, widget_name):
                getattr(self.ui, widget_name).setChecked(saved[key])
                self._flags[key] = saved[key]

        # 2) Now handle irradiance *with* validation, but block its signal so we don’t trigger the popup
        if "irradiance" in saved and hasattr(self.ui, "checkBox_irradiance"):
            cb = self.ui.checkBox_irradiance
            desired = bool(saved["irradiance"])

            # block the user‑slot while restoring
            cb.blockSignals(True)
            cb.setChecked(desired)
            cb.blockSignals(False)
            self._flags["irradiance"] = desired

            # if the user *wanted* irradiance on, verify the calibration array
            if desired:
                feat_list = self._spec_ctrl.features.get("irrad_cal", [])
                ok = False
                if feat_list:
                    try:
                        arr = np.array(feat_list[0].read_calibration(), float)
                        nans = int(np.isnan(arr).sum())
                        if arr.size == self._curve.xData.size and nans == 0:
                            ok = True
                            self._irrad_coef = arr
                        else:
                            reason = (
                                f"length {arr.size} vs {self._curve.xData.size}, "
                                f"{nans} NaN(s)"
                            )
                    except Exception as e:
                        reason = str(e)

                else:
                    reason = "no irradiance feature on this device"

                if not ok:
                    QMessageBox.warning(
                        self,
                        "Irradiance Calibration Error",
                        f"Could not apply saved irradiance calibration:\n{reason}\n"
                        "Irradiance calibration has been turned off."
                    )
                    # roll back the checkbox
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)
                    self._flags["irradiance"] = False
                    self._irrad_coef = np.ones(self._pixel_count, dtype=float)
            else:
                # explicitly off → use unity
                self._irrad_coef = np.ones(self._pixel_count, dtype=float)

        # 3) The rest of your settings follow exactly as before
        if "boxcar_width" in saved:
            self.ui.spinBox_boxcar_smooth.setValue(saved["boxcar_width"])
            self._boxcar_width = saved["boxcar_width"]

        if "bins" in saved:
            bins = saved["bins"]
            idx = self.ui.comboBox_pixel_binning.findText(str(bins))
            if idx >= 0:
                self.ui.comboBox_pixel_binning.setCurrentIndex(idx)
                self._bin_size = bins

        if "thermoelectric" in saved:
            self.ui.checkBox_thermoelectric_enable.setChecked(saved["thermoelectric"])
        if "temp_setpoint" in saved:
            self.ui.spinBox_tec_temp_setpoint.setValue(saved["temp_setpoint"])

    def _update_tec_ui(self, enabled: bool):
        """Enable/disable the setpoint & current‐temp UI based on support+checkbox."""
        has = bool(self._spec_ctrl.features.get("thermo_electric"))
        ok = has and enabled
        # label + value
        self.ui.label_current_temperature.setEnabled(ok)
        self.ui.label_current_temperature_value.setEnabled(ok)
        # spinbox
        self.ui.spinBox_tec_temp_setpoint.setEnabled(ok)

    @Slot(bool)
    def _on_tec_toggled(self, checked: bool) -> None:
        """Called when the user toggles the TEC enable checkbox."""
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if not feat_list:
            return
        tec = feat_list[0]
        try:
            if checked:
                # capture a baseline reading (for the PSU‑check later)
                self._initial_tec_temp = tec.read_temperature_degrees_celsius()
            tec.enable_tec(checked)
        except Exception as e:
            QMessageBox.critical(
                self, "TEC Error",
                f"Failed to {'enable' if checked else 'disable'} TEC:\n{e}"
            )
            # roll back UI state
            self.ui.checkBox_thermoelectric_enable.blockSignals(True)
            self.ui.checkBox_thermoelectric_enable.setChecked(not checked)
            self.ui.checkBox_thermoelectric_enable.blockSignals(False)
            return

        # only the setpoint spinbox should turn on/off with the TEC;
        # the label_current_temperature_value itself will always be updated
        self.ui.spinBox_tec_temp_setpoint.setEnabled(checked)
        # leave the polling timer entirely to _on_tab_changed

    @Slot(int)
    def _on_tec_setpoint_changed(self, value: int):
        """When the user adjusts the spinbox, send the new goal to the spectrometer."""
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if not feat_list:
            return
        try:
            feat_list[0].set_temperature_setpoint_degrees_celsius(value)
        except Exception as e:
            QMessageBox.warning(self, "TEC Setpoint", f"Could not set temperature setpoint:\n{e}")

    def _update_tec_temperature(self):
        """Poll the current TEC temperature once a second (only when the Settings tab is active)."""
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if not feat_list:
            return
        try:
            t = feat_list[0].read_temperature_degrees_celsius()
            self.ui.label_current_temperature_value.setText(f"{t:.1f} °C")
        except Exception:
            # just ignore read errors
            pass

    def _check_tec_power(self):
        """After enabling, verify the temp has dropped — else warn about missing PSU."""
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if not feat_list or self._initial_tec_temp is None:
            return
        try:
            now = feat_list[0].read_temperature_degrees_celsius()
        except Exception:
            return
        if now > self._initial_tec_temp - 0.5:
            QMessageBox.warning(
                self, "Power Supply",
                "TEC enabled but temperature did not drop by at least 0.5 °C.\n"
                "Please check that your external TEC power supply is connected."
            )
            # automatically uncheck so they can hook up the PSU and retry
            self.ui.checkBox_thermoelectric_enable.setChecked(False)

        self._initial_tec_temp = None

    @Slot(int)
    def _on_tab_changed(self, index: int):
        """Start/stop our TEC‑poll timer whenever the user switches tabs."""
        # index 0 is Settings
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if index == 0 and feat_list:
            # always poll the temperature while Settings is visible
            self._tec_timer.start()
            # if we just enabled TEC, schedule the PSU check
            if self._initial_tec_temp is not None:
                QTimer.singleShot(5000, self._check_tec_power)
        else:
            self._tec_timer.stop()

    @Slot()
    def _populate_device_information(self):
        spec = self._spec_ctrl
        ui = self.ui

        # Model / Serial (unchanged)
        model = getattr(spec._spec, "model", "")
        serial = getattr(spec._spec, "serial_number", "")
        ui.label_modelserial_changeable.setText(
            f"{model} / {serial}" if model and serial else serial or model or "—"
        )

        # --- REVISION FEATURE (firmware + hardware) ---
        rev_list = spec._spec.features.get("revision", [])
        if rev_list:
            rev = rev_list[0]
            try:
                fw = rev.revision_firmware_get()
            except Exception:
                fw = "Error"
            try:
                hw = rev.hardware_revision()
            except Exception:
                hw = "Error"
        else:
            fw = "Not supported"
            hw = "Not supported"
            # Optionally, give the user a tooltip explaining why:
            ui.label_firmwarerev_changeable.setToolTip(
                "This spectrometer does not expose the revision feature."
            )
            ui.label_hardwarerev_changeable.setToolTip(
                "This spectrometer does not expose the revision feature."
            )

        ui.label_firmwarerev_changeable.setText(str(fw))
        ui.label_hardwarerev_changeable.setText(str(hw))

        # Pixel count & λ‑range (unchanged)
        try:
            wl, _ = spec.spectrum_raw()
            self._pixel_count = wl.size
            ui.label_pixelcount_changeable.setText(str(len(wl)))
            ui.label_wavelengthrangefactory_changeable.setText(f"{wl[0]:.1f}–{wl[-1]:.1f} nm")
        except Exception:
            ui.label_pixelcount_changeable.setText("—")
            ui.label_wavelengthrangefactory_changeable.setText("—")

        # Integration limits, formatted in ms or s
        mn_us, mx_us = spec.integration_limits_us

        def _fmt_time(us: int) -> str:
            ms = us / 1_000.0
            if ms < 1_000.0:
                return f"{ms:.0f} ms"
            else:
                return f"{ms / 1_000.0:.2f} s"

        ui.label_integrationlimits_changeable.setText(
            f"{_fmt_time(mn_us)}—{_fmt_time(mx_us)}"
        )

        # Saturation limits (maximum intensity)
        try:
            sat = spec._spec.f.spectrometer.get_maximum_intensity()
            ui.label_saturationlimits_changeable.setText(f"{sat:.0f}")
        except Exception:
            ui.label_saturationlimits_changeable.setText("—")

        # Thermistor present? (unchanged)
        ui.label_thermistorpresent_changeable.setText(
            "Yes" if spec.features.get("temperature") else "No"
        )

        # Irradiance‑coefficients count (unchanged)
        ir = spec.features.get("irrad_cal")
        if ir:
            try:
                arr = ir[0].read_calibration()
                ui.label_irradiancecoefficients_changeable.setText(f"{len(arr)} values")
            except Exception:
                ui.label_irradiancecoefficients_changeable.setText("—")
        else:
            ui.label_irradiancecoefficients_changeable.setText("—")

        # Shutter present? (unchanged)
        has_shutter = any("shutter" in k.lower() for k in spec.features)
        ui.label_shutterpresent_changeable.setText("Yes" if has_shutter else "No")

    # ————————————————— unit toggle —————————————————
    def eventFilter(self, watched, event):
        # 1) If it’s a click on the integration‐time label, handle & consume it
        if (
                watched is self.ui.label_integrationtime
                and event.type() == QEvent.Type.MouseButtonRelease
        ):
            lbl = self.ui.label_integrationtime
            sp = self.ui.doubleSpinBox_integration_time_ms
            mn_us, mx_us = self._spec_ctrl.integration_limits_us

            if "(ms)" in lbl.text():
                # → seconds
                ms_val = sp.value()
                s_val = ms_val / 1_000.0
                lbl.setText("Integration time (s):")
                sp.setDecimals(3)
                sp.setRange(mn_us / 1_000_000.0, mx_us / 1_000_000.0)
                sp.setValue(s_val)
            else:
                # → milliseconds
                s_val = sp.value()
                ms_val = s_val * 1_000.0
                lbl.setText("Integration time (ms):")
                sp.setDecimals(0)
                sp.setRange(mn_us / 1_000.0, mx_us / 1_000.0)
                sp.setValue(ms_val)

            # Push the new value (in µs) to the spectrometer
            is_ms = "(ms)" in lbl.text()
            factor = 1_000 if is_ms else 1_000_000
            self._spec_ctrl.set_integration_time_us(int(sp.value() * factor))

            return True

        # 2) For everything else, fall back to the default handler
        return super().eventFilter(watched, event)

    def closeEvent(self, ev):
        """Ensure TEC is turned off when the user closes the GUI."""
        # if the device has a TEC feature, disable it
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if feat_list:
            try:
                feat_list[0].enable_tec(False)
            except Exception:
                print("Failed to disable TEC on exit")
        super().closeEvent(ev)

    @Slot()
    def _disable_tec_on_exit(self):
        feat_list = self._spec_ctrl.features.get("thermo_electric", [])
        if feat_list:
            try:
                feat_list[0].enable_tec(False)
            except Exception:
                print("Failed to disable TEC on exit")


