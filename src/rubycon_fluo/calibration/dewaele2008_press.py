"""
Ruby P-scale of  Dewaele et al. (2008)
--------------------------------------

    P(GPa) = (A / B) · [ (λ/λ₀)ᴮ – 1 ]

with                                              (1 σ uncertainties)
    A = 1920 ± 20 GPa
    B = 9.61 ± 0.05
"""

from __future__ import annotations
import math
from typing import Tuple

from insta_raman.calibration.calibration_core import PressureCalibration


class Dewaele2008(PressureCalibration):
    name        = "Dewaele et al. 2008"
    source      = (
        "Dewaele, A., Torrent, M., Loubeyre, P., & Mezouar, M. (2008). "
        "Compression curves of transition metals in the Mbar range: Experiments and "
        "projector augmented-wave calculations. Phys. Rev. B, 78, 104102. "
        "doi:10.1103/PhysRevB.78.104102"
    )
    is_combined = False        # the scale itself has **no** temperature term

    # constants (value, 1-σ uncertainty)
    _A, _sigmaA = 1920.0, 20.0        # GPa
    _B, _sigmaB = 9.61,   0.05

    # ------------------------------------------------------------------
    # main API required by PressureCalibration
    # ------------------------------------------------------------------
    def pressure(
        self,
        lambda0: float,
        lambda_r: float,
        t_ref: float,          # unused
        t_meas: float,         # unused
        sigma_lambda: float = 0.0
    ) -> Tuple[float, float]:

        ratio = lambda_r / lambda0
        A, B = self._A, self._B

        # equation itself
        P = (A / B) * (ratio ** B - 1)

        # ----------------- error propagation --------------------------
        # ∂P/∂A, ∂P/∂B, ∂P/∂λ_r
        dP_dA       = (1 / B) * (ratio ** B - 1)
        dP_dB       = (-A / B**2) * (ratio ** B - 1) \
                      + (A / B) * (ratio ** B) * math.log(ratio)
        dP_dlambda  = (A / B) * B * (ratio ** (B - 1)) * (1 / lambda0)

        sigmaP = math.sqrt(
            (dP_dA * self._sigmaA)**2 +
            (dP_dB * self._sigmaB)**2 +
            (dP_dlambda * sigma_lambda)**2
        )

        return P, sigmaP