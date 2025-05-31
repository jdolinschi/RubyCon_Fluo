from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
from insta_raman.fitting.auto_fit import AutoFit

class AutoFitWorker(QObject):
    """Runs a two-peak AutoFit in a background thread."""
    fit_finished = Signal(object, object)   # (popt, pcov)
    fit_failed   = Signal()

    def __init__(self,
                 wl: np.ndarray,
                 cnt: np.ndarray,
                 lo: float,
                 hi: float):
        super().__init__()
        self.wl = wl
        self.cnt = cnt
        self.lo = lo
        self.hi = hi
        self._stop = False

    def stop(self) -> None:
        """Request cancellation."""
        self._stop = True

    @Slot()
    def run(self) -> None:
        """Perform the fit; emit fit_finished or fit_failed."""
        if self._stop:
            return
        try:
            popt, pcov = AutoFit().fit(self.wl, self.cnt, self.lo, self.hi)
            if not self._stop:
                self.fit_finished.emit(popt, pcov)
        except Exception:
            if not self._stop:
                self.fit_failed.emit()
