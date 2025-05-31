import numpy as np
from PySide6.QtWidgets import (
    QDialog, QTextEdit, QVBoxLayout, QPushButton,
    QHBoxLayout, QProgressBar
)
from PySide6.QtCore import QObject, Signal, QThread, Slot, Qt
import numpy as _np


def _is_plateau(prev: float, curr: float, rel_tol: float = 0.1, min_counts: float = 1000.0) -> bool:
    """
    Plateau if the fractional increase (curr/prev − 1) is <= rel_tol,
    but only *after* we’re above some minimum count level.

    rel_tol=0.1 means “10%”;
    min_counts prevents false‐positives at very low signals.
    """
    if prev <= 0.0:
        return False
    # don’t start plateauing until we have enough signal to trust
    if prev < min_counts:
        return False
    # fractional gain
    frac_gain = (curr - prev) / prev
    return frac_gain <= rel_tol


class OptimizeWorker(QObject):
    """
    Worker to sweep integration times in a background thread.
    Emits:
      - progress(ms, counts)
      - finished_scan(data: list of (ms, count))
    """
    progress = Signal(int, float)
    finished_scan = Signal(list)

    def __init__(self, spec_ctrl, backend_kwargs, pipeline, parent=None):
        super().__init__(parent)
        self.spec_ctrl = spec_ctrl
        self.backend_kwargs = backend_kwargs
        self.pipeline = pipeline
        self._stop = False

    @Slot()
    def run(self):
        mn_us, mx_us = self.spec_ctrl.integration_limits_us
        t_us = mn_us
        results = []
        prev_max = None

        while t_us <= mx_us and not self._stop:
            # 1) set & read
            self.spec_ctrl.set_integration_time_us(t_us)
            wl, cnt = self.spec_ctrl.spectrum_raw(**self.backend_kwargs)

            # 2) apply *your* processing pipeline
            proc = cnt.astype(float)

            bg = self.pipeline.get("background_counts")
            if bg is not None and bg.shape == proc.shape:
                proc = proc - bg

            # optical‐dark
            if self.pipeline["optical_dark"]:
                for lo, hi in self.pipeline["odark_ranges"]:
                    proc -= proc[lo:hi].mean()
            # stray‐light
            if self.pipeline["stray_light"]:
                x = np.arange(proc.size)
                proc -= np.polyval(self.pipeline["sl_coef"][::-1], x)
            # irradiance
            if self.pipeline["irradiance"]:
                proc *= self.pipeline["irrad_coef"]
            # boxcar
            if self.pipeline["boxcar"] and self.pipeline["boxcar_width"] > 1:
                w = np.ones(self.pipeline["boxcar_width"]) / self.pipeline["boxcar_width"]
                proc = np.convolve(proc, w, mode="same")
            # pixel‐binning (simple re‐bin by averaging)
            if self.pipeline["pixel_binning"] and self.pipeline["bin_size"] > 1:
                n = self.pipeline["bin_size"]
                # trim to multiple of n
                L = (proc.size // n) * n
                proc = proc[:L].reshape(-1, n).mean(axis=1)

            max_cnt = float(proc.max())
            ms = int(t_us // 1_000)
            results.append((ms, max_cnt))
            self.progress.emit(ms, max_cnt)

            # plateau check unchanged
            if prev_max is not None and _is_plateau(prev_max, max_cnt):
                break
            prev_max = max_cnt
            t_us *= 2

        self.finished_scan.emit(results)

    def stop(self):
        self._stop = True


class OptimizeDialog(QDialog):
    def __init__(self, spec_ctrl, backend_kwargs, pipeline, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Optimize Integration Time")
        self.setModal(True)
        self.spec_ctrl = spec_ctrl
        self.backend_kwargs = backend_kwargs
        self._optimal_ms = None

        # UI
        layout = QVBoxLayout(self)
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # busy
        layout.addWidget(self.progress)

        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply integration time", self)
        self.apply_btn.setEnabled(False)
        self.cancel_btn = QPushButton("Cancel", self)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # signals
        self.apply_btn.clicked.connect(self._on_apply)
        # allow cancel at any time
        self.cancel_btn.clicked.connect(self._on_cancel)

        # worker thread
        self._thread = QThread(self)
        self._worker = OptimizeWorker(spec_ctrl, backend_kwargs, pipeline)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_scan.connect(self._on_finished)
        # ensure thread quits when done
        self._worker.finished_scan.connect(self._thread.quit)

        self.setAttribute(Qt.WA_DeleteOnClose)

    @Slot(int, float)
    def _on_progress(self, ms: int, count: float) -> None:
        self.log.append(f"Tested {ms} ms → max count {count:.2f}")

    @Slot(list)
    def _on_finished(self, data: list) -> None:
        # 1) split into used vs saturated (last two)
        if len(data) > 2:
            used = data[:-2]
            saturated = data[-2:]
        else:
            used = data
            saturated = []

        # 2) prepare arrays for fit
        x = _np.array([pt[0] for pt in used], float)
        y = _np.array([pt[1] for pt in used], float)

        # 3) get true saturation level from the last two points
        if saturated:
            sat = max(count for _, count in saturated)
        else:
            sat = used[-1][1] if used else 0.0

        # 3) fit
        if x.size >= 2:
            m, b = _np.polyfit(x, y, 1)
            y_pred = m * x + b
            ss_res = ((y - y_pred) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot else 1.0
            t95 = int((0.95 * sat - b) / m)
        elif x.size == 1:
            m, b, r2 = 0.0, y[0], 1.0
            t95 = int(x[0])
        else:
            m, b, r2, t95 = 0.0, 0.0, 0.0, 0

        # (correct) clamp to the full tested range, including the two saturated points
        if data:
            min_ms = data[0][0]
            max_ms = data[-1][0]
            t95 = max(min(t95, max_ms), min_ms)

        self._optimal_ms = t95

        # 4) rebuild dialog log with colored text
        self.log.clear()
        for ms, cnt in used:
            self.log.append(
                f'<span style="color: lightgreen">Tested {ms} ms → max count {cnt:.2f}</span>'
            )
        for ms, cnt in saturated:
            self.log.append(
                f'<span style="color: lightcoral">Tested {ms} ms → max count {cnt:.2f}</span>'
            )

        # 5) summary & stats
        self.log.append("<hr>")
        self.log.append(f"Optimal ~ <b>{t95} ms</b> (95% sat ~ {0.95 * sat:.1f})")
        self.log.append(f"Fit: y = {m:.2f}·x + {b:.1f}   R² = {r2:.4f}")

        # 6) re-enable
        self.apply_btn.setEnabled(True)
        self.progress.setRange(0, 1)
        self.progress.setValue(1)

    def optimal_ms(self) -> int | None:
        return self._optimal_ms

    @Slot()
    def _on_apply(self) -> None:
        # 1) stop the worker
        self._worker.stop()
        # 2) quit & wait for its thread
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        # 3) explicitly set the spectrometer to the chosen value one last time
        if self._optimal_ms is not None:
            self.spec_ctrl.set_integration_time_us(self._optimal_ms * 1_000)
        # 4) finally close the dialog
        self.accept()

    @Slot()
    def _on_cancel(self) -> None:
        # stop background sweep, quit thread and wait for it to finish, then close
        self._worker.stop()
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        self.reject()

    def closeEvent(self, ev):
        # ensure thread is stopped if dialog is closed
        self._worker.stop()
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        super().closeEvent(ev)

        # stop background sweep and close
        self._worker.stop()
        self.reject()

    def showEvent(self, ev):
        """Start the background sweep every time the dialog is shown."""
        super().showEvent(ev)
        # only start if not already running
        if not self._thread.isRunning():
            self._thread.start()
