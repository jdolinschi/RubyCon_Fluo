"""
Ruby P-scale of Dorogokupets & Oganov (2007)
--------------------------------------------

    P(GPa) = A · δ · (1 + C·δ)                    (eq. 1)

with
    δ = (λᵣ – λ₀) / λ₀

Valid to ≈120 GPa at 300 K.
"""

from __future__ import annotations
import math
from typing import Tuple

from insta_raman.calibration.calibration_core import PressureCalibration


class Dorogokupets2007(PressureCalibration):
    """Dorogokupets, P. I. & Oganov, A. R. (2007) pressure scale."""
    name        = "Dorogokupets & Oganov 2007"
    source      = (
        "Dorogokupets, P. I., & Oganov, A. R. (2007). Ruby, metals, and MgO as alternative"
        "pressure scales: A semi-empirical description of shock-wave, ultrasonic, x-ray,"
        "and thermochemical data at high temperatures and pressures. Phys. Rev. B 75, 024115."
        "doi:10.1103/PhysRevB.75.024115"
    )
    is_combined = False          # needs an external temperature correction

    _A, _sigmaA = 1884.0, 0.0    # GPa
    _C, _sigmaC = 5.50,  0.0

    # ------------------------------------------------------------------ #
    #  required API                                                      #
    # ------------------------------------------------------------------ #
    def pressure(
        self,
        lambda0: float,
        lambda_r: float,
        t_ref: float,             # not used
        t_meas: float,            # not used
        sigma_lambda: float = 0.0
    ) -> Tuple[float, float]:

        delta = (lambda_r - lambda0) / lambda0
        A, C  = self._A, self._C

        # main equation
        P = A * delta * (1.0 + C * delta)

        # === partial derivatives for σP =================================
        # ∂P/∂A
        dP_dA = delta * (1.0 + C * delta)

        # ∂P/∂C
        dP_dC = A * delta * delta

        # ∂P/∂λᵣ  (through δ)
        dP_ddelta = A * (1.0 + 2.0 * C * delta)
        ddelta_dlr = 1.0 / lambda0
        dP_dlr = dP_ddelta * ddelta_dlr

        # === error propagation ==========================================
        sigmaP = math.sqrt(
            (dP_dA  * self._sigmaA) ** 2 +
            (dP_dC  * self._sigmaC) ** 2 +
            (dP_dlr * sigma_lambda) ** 2
        )

        return P, sigmaP
