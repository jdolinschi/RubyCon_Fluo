from __future__ import annotations

import threading
import time

import numpy as np
from PySide6.QtCore import QObject, Signal, Slot


class AcquisitionWorker(QObject):
    spectrum_ready = Signal(np.ndarray, np.ndarray)        # wl, intensity
    integration_tick = Signal(float)                       # 0‑100 %
    scan_tick = Signal(int, int)                           # done, total
    remaining_time = Signal(float)                         # seconds left
    finished = Signal()                                    # done

    def __init__(
        self,
        spec,
        int_time_us: int,
        scans_to_avg: int,
        continuous: bool,
        dark_counts: bool,
        correct_nonlinearity: bool,
    ):
        super().__init__()
        self._spec = spec
        self._int_us = int_time_us
        self._scans = max(1, scans_to_avg)
        self._scans_total = self._scans
        self._continuous = continuous
        self._stop_flag = False
        self._dark_counts = dark_counts
        self._correct_nonlinearity = correct_nonlinearity

    # ------------------------------------------------------------------#
    # public control slot                                                #
    # ------------------------------------------------------------------
    @Slot()
    def start(self) -> None:                       # ← rewritten
        total_scans      = self._scans_total
        single_scan_sec  = self._int_us / 1_000_000

        self.integration_tick.emit(0)  # integration bar → 0 %
        self.scan_tick.emit(0, total_scans)  # scans bar       → 0 %

        while not self._stop_flag:
            self._spec.set_integration_time_us(self._int_us)
            self._spec.set_scans_to_average(total_scans)

            wl_accum: np.ndarray | None = None
            acc:      np.ndarray | None = None

            for n in range(total_scans):
                if self._stop_flag:
                    break

                # ---------------------------------------------------------
                # 1. kick off the blocking spectrum read in a helper thread
                # ---------------------------------------------------------
                buf: dict[str, np.ndarray] = {}

                def _capture():
                    buf["wl"], buf["cnt"] = self._spec.spectrum_raw(
                        correct_dark_counts=self._dark_counts,
                        correct_nonlinearity=self._correct_nonlinearity,
                    )

                t = threading.Thread(target=_capture, daemon=True)
                t.start()

                # ---------------------------------------------------------
                # 2. while that thread runs, emit progress every 0.1 s
                # ---------------------------------------------------------
                start = time.perf_counter()
                while t.is_alive() and not self._stop_flag:
                    elapsed = time.perf_counter() - start
                    self.integration_tick.emit(min(99, int(elapsed /
                                                             single_scan_sec * 100)))
                    self.remaining_time.emit(
                        round(max(0.0,
                                  (total_scans - n - 1) * single_scan_sec
                                  + single_scan_sec - elapsed), 1)
                    )
                    time.sleep(0.10)      # ≈100 ms refresh

                t.join()                  # make sure we actually have data
                self.integration_tick.emit(100)          # exposure done
                self.remaining_time.emit(0.0)

                wl, counts = buf["wl"], buf["cnt"]
                wl_accum = wl if wl_accum is None else wl_accum
                acc      = counts.astype(float) if acc is None else acc + counts

                # update scan bar (20 %, 40 %, …)
                self.scan_tick.emit(n + 1, total_scans)

            self.scan_tick.emit(total_scans, total_scans)
            if self._stop_flag or acc is None:
                break

            acc /= total_scans
            self.spectrum_ready.emit(wl_accum, acc)      # averaged spectrum

            if not self._continuous:                     # single‑shot mode
                break

        self.integration_tick.emit(100)
        self.scan_tick.emit(total_scans, total_scans)
        self.finished.emit()

    # ------------------------------------------------------------------#
    # public API                                                         #
    # ------------------------------------------------------------------
    def stop(self) -> None:
        self._stop_flag = True
        self.scan_tick.emit(self._scans_total, self._scans_total)
