"""
Ruby P-scale of Chijioke *et al.* (2005)
----------------------------------------

    P(GPa) = (A / B) · [ (λᵣ / λ₀)ᴮ – 1 ]           (eq. 1)

λ₀ is the reference R1 wavelength at ambient P–T.

Constants (paper, table III):
    A = 1876 ± 6.7  GPa
    B = 10.71 ± 0.14
"""

from __future__ import annotations
import math
from typing import Tuple

from rubycon_fluo.calibration.calibration_core import PressureCalibration


class Chijioke2005(PressureCalibration):
    """Chijioke, A. D. *et al.* (2005) pressure scale."""
    name        = "Chijioke et al. 2005"
    source      = (
        "Chijioke, A. D., Nellis, W. J., Soldatov, A., & Silvera, I. F. (2005). "
        "The ruby pressure standard to 150 GPa. J. Appl. Phys. 98 (11): 114905. "
        "doi:10.1063/1.2135877"
    )
    is_combined = False

    _A, _sigmaA = 1876.0, 6.7     # GPa
    _B, _sigmaB = 10.71,  0.14

    # ------------------------------------------------------------------ #
    def pressure(
        self,
        lambda0: float,
        lambda_r: float,
        t_ref: float,             # not used
        t_meas: float,            # not used
        sigma_lambda: float = 0.0
    ) -> Tuple[float, float]:

        A, B = self._A, self._B
        ratio  = lambda_r / lambda0   #  = 1 + δ

        # equation
        P = (A / B) * (ratio ** B - 1.0)

        # ---------- derivatives ----------------------------------------
        dP_dA = (1.0 / B) * (ratio ** B - 1.0)

        dP_dB = - (A / B**2) * (ratio ** B - 1.0) \
                + (A / B) * (ratio ** B) * math.log(ratio)

        dP_dlr = A * ratio ** (B - 1.0) * (1.0 / lambda0)

        # ---------- uncertainty ----------------------------------------
        sigmaP = math.sqrt(
            (dP_dA * self._sigmaA) ** 2 +
            (dP_dB * self._sigmaB) ** 2 +
            (dP_dlr * sigma_lambda) ** 2
        )

        return P, sigmaP
