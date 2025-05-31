"""
Ragan *et al.* (1992) temperature shift for ruby R1
---------------------------------------------------

Polynomial for the **wavenumber** ν_R1(T) (cm⁻¹):

    ν(T) = 14423.0
         + 4.49 × 10⁻²  · T
         − 4.81 × 10⁻⁴  · T²
         + 3.71 × 10⁻⁷  · T³

λ[nm] = 10⁷ / ν.  The calibration returns the wavelength
difference between **T_meas** and **T_ref** in nm.
"""

from __future__ import annotations
from typing import Tuple

from insta_raman.calibration.calibration_core import TemperatureCalibration


class Ragan1992(TemperatureCalibration):
    name   = "Ragan et al. 1992"
    source = (
        "Ragan, D. D., Gustavsen, R., & Schiferl, D. (1992). Calibration of the ruby R1 and"
        "R2 fluorescence shifts as a function of temperature from 0 K to 600 K. J. Appl. Phys. 72 (12), 5539-5544."
        "doi:10.1063/1.351951"
    )

    _a0 = 14423.0
    _a1 = 4.49e-2
    _a2 = -4.81e-4
    _a3 = 3.71e-7

    # ------------------------------------------------------------------
    def _nu_cm1(self, T: float) -> float:
        return (
            self._a0
            + self._a1 * T
            + self._a2 * T * T
            + self._a3 * T * T * T
        )

    def delta_lambda(self, t_ref: float, t_meas: float) -> float:
        """
        Return Δλ (nm) = λ(T_meas) − λ(T_ref).
        Temperatures are in Kelvin.
        """
        # wavelength in nm
        lam_meas = 1.0e7 / self._nu_cm1(t_meas)
        lam_ref  = 1.0e7 / self._nu_cm1(t_ref)
        return lam_meas - lam_ref
