from __future__ import annotations
import logging
from contextlib import suppress
from types import MethodType
from typing import Tuple, Sequence

import seabreeze
seabreeze.use("cseabreeze")                   # ← pick the C backend exactly once
from seabreeze.spectrometers import Spectrometer, list_devices

import numpy as np

logger = logging.getLogger(__name__)


class _DummySpectrometer:
    """Stand‑in when no hardware is present."""
    _MIN_US = 1_000
    _MAX_US = 10_000_000

    def __init__(self) -> None:
        self._integration_time_us = 100_000
        self.scans_to_average = 1

    def get_integration_time_limits_us(self) -> Tuple[int, int]:
        return self._MIN_US, self._MAX_US

    def set_integration_time_us(self, value_us: int) -> None:
        self._integration_time_us = max(self._MIN_US,
                                        min(int(value_us), self._MAX_US))
        logger.debug("[Dummy] Integration set to %d µs", self._integration_time_us)

    def set_scans_to_average(self, scans: int) -> None:
        self.scans_to_average = max(1, int(scans))
        logger.debug("[Dummy] Scans-to-average: %d", self.scans_to_average)

    def spectrum(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        wl = np.linspace(400, 1000, 2048)
        counts = 1000*np.exp(-0.5*((wl - 620)/10)**2)
        return wl, counts

    @property
    def features(self) -> dict:
        return {}

    @property
    def serial_number(self) -> str:
        return "DUMMY"

    @property
    def model(self) -> str:
        return "DUMMY"

    def temperature(self) -> float:
        raise AttributeError("No temperature feature")


class SpectrometerController:
    """Single‐point façade over cseabreeze Spectrometer + dummy fallback.
    This is the only class that directly communicates with the spectrometer."""

    def __init__(self, device=None) -> None:
        # if user passed in a raw SeaBreezeDevice, open it; else pick the first
        self._spec = self._open_device(device) if device else self._open_first_available()
        self._min_us, self._max_us = self._spec.get_integration_time_limits_us()

    def set_binning_factor(self, factor: int) -> None:
        """Proxy to the underlying PixelBinningFeature."""
        feats = self._spec.features.get("pixel_binning", [])
        if not feats:
            raise RuntimeError("Device does not support pixel_binning")
        feats[0].set_binning_factor(factor)

    @classmethod
    def list_devices(cls) -> Sequence:
        try:
            return list_devices()
        except Exception:
            logger.exception("listing spectrometers failed")
            return []

    @classmethod
    def _open_device(cls, device) -> object:
        try:
            spec = Spectrometer(device)
            return cls._patch_api(spec)
        except Exception:
            logger.exception("opening %r failed – using dummy", device)
            return _DummySpectrometer()

    @classmethod
    def _open_first_available(cls) -> object:
        devs = cls.list_devices()
        if not devs:
            logger.warning("no hardware found – using dummy")
            return _DummySpectrometer()
        try:
            spec = Spectrometer.from_serial_number(devs[0].serial_number)
            return cls._patch_api(spec)
        except Exception:
            logger.exception("opening first device failed")
            return _DummySpectrometer()

    @staticmethod
    def _patch_api(spec) -> object:
        """Inject uniform micros_limits, setters, and leave the rest of the backend alone."""
        # 1) integration limits
        try:
            mn, mx = spec.integration_time_micros_limits
        except Exception:
            mn, mx = spec.f.spectrometer.get_integration_time_micros_limits()
        spec.get_integration_time_limits_us = MethodType(
            lambda self: (int(mn), int(mx)), spec
        )

        # 2) setters
        def _apply_integration(self, v):
            with suppress(AttributeError):
                self.integration_time_micros(v)
                return
            self.f.spectrometer.set_integration_time_micros(v)

        spec.set_integration_time_us = MethodType(
            lambda self, v: _apply_integration(self, v), spec
        )
        spec.set_scans_to_average = MethodType(
            lambda self, s: setattr(self, "scans_to_average", s), spec
        )

        logger.info("Using spectrometer %s", spec)
        return spec

    @property
    def device_id(self) -> str:
        m = getattr(self._spec, "model", "")
        s = getattr(self._spec, "serial_number", "")
        return f"{m}:{s}" if m and s else s or repr(self._spec)

    @property
    def features(self) -> dict:
        return getattr(self._spec, "features", {})

    @property
    def integration_limits_us(self) -> Tuple[int, int]:
        return self._spec.get_integration_time_limits_us()

    def set_integration_time_us(self, v: int):
        self._spec.set_integration_time_us(int(v))

    def set_scans_to_average(self, s: int):
        self._spec.set_scans_to_average(int(s))

    def spectrum_raw(self, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        return self._spec.spectrum(**kwargs)

    def get_detector_temperature(self) -> float:
        with suppress(AttributeError):
            return float(self._spec.temperature())
        raise RuntimeError("no temperature feature")
