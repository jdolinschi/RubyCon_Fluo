from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QDialog

from insta_raman.gui.controllers.acquisition import AcquisitionWorker
from insta_raman.gui.dialogs.optimize_integration import OptimizeDialog


class AcquisitionController(QObject):
    """
    Encapsulates all spectrometer acquisition logic (single-shot, continuous, background),
    tracks the most recent spectrum and background data, and emits signals for
    spectrum data and progress. Connect UI controls to this manager to offload
    acquisition-related operations from MainWindowController.
    """

    # Signals forwarded to UI or MainWindowController
    spectrum_ready: Signal = Signal(np.ndarray, np.ndarray)
    integration_tick: Signal = Signal(float)           # percent 0–100
    scan_tick: Signal = Signal(int, int)               # scans done, total scans
    remaining_time: Signal = Signal(float)             # seconds left
    finished: Signal = Signal()                        # acquisition complete

    background_ready: Signal = Signal(np.ndarray, np.ndarray)
    background_finished: Signal = Signal()

    def __init__(
        self,
        spec_ctrl,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._spec_ctrl = spec_ctrl

        # Acquisition parameters
        self._int_time_us: int = 100_000
        self._scans_to_avg: int = 1
        self._dark_counts: bool = False
        self._correct_nonlinearity: bool = False

        # Internal storage for last results
        self._last_spectrum: Optional[Tuple[np.ndarray, np.ndarray]] = None
        self._last_background: Optional[Tuple[np.ndarray, np.ndarray]] = None

        # Threads and workers for main and background acquisition
        self._thread: Optional[QThread] = None
        self._worker: Optional[AcquisitionWorker] = None
        self._bg_thread: Optional[QThread] = None
        self._bg_worker: Optional[AcquisitionWorker] = None

    def clear_background(self) -> None:
        """
        Forget the most‑recent background so that spectra are displayed
        uncorrected.  No acquisition is started and no signals are fired.
        """
        self._last_background = None

    def run_optimize(
            self,
            *,
            flags: dict,
            boxcar_width: int,
            bin_size: int,
            odark_ranges,
            sl_coef,
            irrad_coef,
            parent=None,
    ) -> int | None:
        """
        Launch the “Optimize Integration Time” dialog and return the
        recommended integration time in milliseconds, or None if the
        dialog was cancelled.

        Parameters
        ----------
        flags           dict of booleans with keys:
                            electric_dark, optical_dark, stray_light,
                            non_linearity, irradiance, boxcar, pixel_binning
        boxcar_width    current integer boxcar width
        bin_size        current pixel‑binning factor
        odark_ranges    list[(lo, hi)]   optical‑dark pixel ranges
        sl_coef         ndarray          stray‑light coefficients
        irrad_coef      ndarray          irradiance calibration array
        parent          QWidget or None  (dialog owner)
        :param bin_size:
        """
        backend_kwargs = {
            "correct_dark_counts": flags.get("electric_dark", False),
            "correct_nonlinearity": flags.get("non_linearity", False),
        }

        # Pull any stored background from the manager
        bg_wl, bg_cnt = (None, None)
        if self.last_background is not None:
            bg_wl, bg_cnt = self.last_background

        pipeline = {
            "optical_dark": flags.get("optical_dark", False),
            "stray_light": flags.get("stray_light", False),
            "irradiance": flags.get("irradiance", False),
            "boxcar": flags.get("boxcar", False),
            "boxcar_width": boxcar_width,
            "pixel_binning": flags.get("pixel_binning", False),
            "bin_size": bin_size,
            "odark_ranges": odark_ranges,
            "sl_coef": sl_coef,
            "irrad_coef": irrad_coef,
            "background_wl": bg_wl,
            "background_counts": bg_cnt,
        }

        dlg = OptimizeDialog(self._spec_ctrl, backend_kwargs, pipeline, parent=parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.optimal_ms()
        return None

    # ──────────────────────────────────────────────────────────────
    # Public helper: swap the SpectrometerController on the fly
    # ──────────────────────────────────────────────────────────────
    def set_spectrometer(self, spec_ctrl) -> None:
        """
        Replace the spectrometer controller used for subsequent
        acquisitions.  Any acquisition that is still running is
        cleanly stopped first so the worker threads don’t hold on
        to the old device handle.
        """
        # stop foreground acquisition (if any)
        self.stop()
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()

        # stop background acquisition (if any)
        if self._bg_worker:
            self._bg_worker.stop()
        if self._bg_thread and self._bg_thread.isRunning():
            self._bg_thread.quit()
            self._bg_thread.wait()

        # finally swap the reference
        self._spec_ctrl = spec_ctrl

    def set_parameters(
        self,
        integration_time_us: int,
        scans_to_avg: int,
        dark_counts: bool = False,
        correct_nonlinearity: bool = False,
    ) -> None:
        """
        Configure acquisition parameters. Call before start methods.
        """
        self._int_time_us = integration_time_us
        self._scans_to_avg = max(1, scans_to_avg)
        self._dark_counts = dark_counts
        self._correct_nonlinearity = correct_nonlinearity

    @Slot(bool)
    def start_single(self, continuous: bool = False) -> None:
        """
        Begin a single-shot (or continuous) acquisition.
        """
        self._stop_current()
        self._start_worker(continuous=continuous)

    @Slot()
    def stop(self) -> None:
        """
        Stop any ongoing acquisition (single or continuous).
        """
        self._stop_current()

    def _start_worker(self, continuous: bool) -> None:
        # Clean up existing thread if still running
        if self._thread and self._thread.isRunning():
            self._worker.stop()
            self._thread.quit()
            self._thread.wait()

        # Create new worker + thread
        self._thread = QThread(self)
        self._worker = AcquisitionWorker(
            spec=self._spec_ctrl,
            int_time_us=self._int_time_us,
            scans_to_avg=self._scans_to_avg,
            continuous=continuous,
            dark_counts=self._dark_counts,
            correct_nonlinearity=self._correct_nonlinearity,
        )
        self._worker.moveToThread(self._thread)

        # Wire signals: progress and data
        self._thread.started.connect(self._worker.start)
        self._worker.integration_tick.connect(self.integration_tick)
        self._worker.scan_tick.connect(self.scan_tick)
        self._worker.remaining_time.connect(self.remaining_time)
        self._worker.spectrum_ready.connect(self._handle_spectrum)
        self._worker.finished.connect(self._on_finished)

        self._thread.start()

    def _stop_current(self) -> None:
        if self._worker:
            self._worker.stop()

    @Slot(np.ndarray, np.ndarray)
    def _handle_spectrum(self, wl: np.ndarray, counts: np.ndarray) -> None:
        """
        Internal slot: store latest spectrum and forward it.
        """
        self._last_spectrum = (wl, counts)
        self.spectrum_ready.emit(wl, counts)

    @Slot()
    def _on_finished(self) -> None:
        """
        Internal slot for worker.finished. Emits finished and cleans up thread.
        """
        self.finished.emit()
        if self._thread:
            self._thread.quit()
            self._thread.wait()
        self._thread = None
        self._worker = None

    def collect_background(self) -> None:
        """
        Perform a single-shot acquisition for background measurements.
        """
        # If a background thread is already running, ignore
        if self._bg_thread and self._bg_thread.isRunning():
            return

        self._bg_thread = QThread(self)
        self._bg_worker = AcquisitionWorker(
            spec=self._spec_ctrl,
            int_time_us=self._int_time_us,
            scans_to_avg=self._scans_to_avg,
            continuous=False,
            dark_counts=self._dark_counts,
            correct_nonlinearity=self._correct_nonlinearity,
        )
        self._bg_worker.moveToThread(self._bg_thread)

        # Wire background signals
        self._bg_thread.started.connect(self._bg_worker.start)
        self._bg_worker.integration_tick.connect(self.integration_tick)
        self._bg_worker.scan_tick.connect(self.scan_tick)
        self._bg_worker.remaining_time.connect(self.remaining_time)
        self._bg_worker.spectrum_ready.connect(self._handle_background)
        self._bg_worker.finished.connect(self._on_background_finished)

        self._bg_thread.start()

    @Slot(np.ndarray, np.ndarray)
    def _handle_background(self, wl: np.ndarray, counts: np.ndarray) -> None:
        """
        Internal slot: store latest background then emit.
        """
        self._last_background = (wl, counts)
        self.background_ready.emit(wl, counts)

    @Slot()
    def _on_background_finished(self) -> None:
        """
        Internal slot for background worker.finished. Emits background_finished and cleans up.
        """
        self.background_finished.emit()
        if self._bg_thread:
            self._bg_thread.quit()
            self._bg_thread.wait()
        self._bg_thread = None
        self._bg_worker = None

    @property
    def last_spectrum(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get the last acquired spectrum (wl, counts)."""
        return self._last_spectrum

    @property
    def last_background(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get the last acquired background (wl, counts)."""
        return self._last_background
