"""
Ruby P-scale of  Mao, Xu & Bell (1986)
--------------------------------------

    P(GPa) = 100 · (A / B) · [ (1 + δ)ᴮ – 1 ]                 (eq. 1)

where
    δ  = (λᵣ – λ₀) / λ₀

Constants (originally reported in megabar, MB):
    A = 19.04 ± 0.00 MB   →  A = 1904 GPa
    B = 7.665 ± 0.000

The extra factor **100** converts the *megabar* formulation into **GPa**.
"""

from __future__ import annotations
import math
from typing import Tuple

from rubycon_fluo.calibration.calibration_core import PressureCalibration


class Mao1986(PressureCalibration):
    """Mao, H.-k., Xu, J., & Bell, P. M. (1986) pressure scale."""
    name        = "Mao et al. 1986"
    source      = (
        "Mao, H. K., Xu, J., & Bell, P. M. (1986). Calibration of the ruby pressure gauge"
        "to 800 kbar under quasi-hydrostatic conditions. J. Geophys. Res. 91(B5), 4673–4676"
        "doi:10.1029/JB091iB05p04673"
    )
    is_combined = False   # ⇢ still needs an external T-correction

    # ---- constants in the original units ---------------------------------
    _A_MB, _sigmaA_MB = 19.04, 0.00      # megabar
    _B,    _sigmaB    = 7.665, 0.000

    # ----------------------------------------------------------------------
    # API required by PressureCalibration
    # ----------------------------------------------------------------------
    def pressure(
        self,
        lambda0: float,
        lambda_r: float,
        t_ref: float,          # not used
        t_meas: float,         # not used
        sigma_lambda: float = 0.0
    ) -> Tuple[float, float]:

        # convert A → GPa once so we can reuse it
        A_GPa  = self._A_MB * 100.0          # 1 MB = 100 GPa
        sigmaA = self._sigmaA_MB * 100.0

        B, sigmaB = self._B, self._sigmaB
        delta     = (lambda_r - lambda0) / lambda0

        # -------------------- equation itself -----------------------------
        P = (A_GPa / B) * ((1 + delta) ** B - 1)

        # -------------------- derivatives for σP --------------------------
        # ∂P/∂A   (A still in GPa here)
        dP_dA = (1 / B) * ((1 + delta) ** B - 1)

        # ∂P/∂B
        dP_dB = (A_GPa / B) * ((1 + delta) ** B) * math.log(1 + delta) \
                - (A_GPa / B**2) * ((1 + delta) ** B - 1)

        # ∂P/∂λᵣ   (via δ)
        ddelta_dlr = 1.0 / lambda0
        dP_dlr     = (A_GPa / B) * B * ((1 + delta) ** (B - 1)) * ddelta_dlr

        # -------------------- combine uncertainties -----------------------
        sigmaP = math.sqrt(
            (dP_dA * sigmaA) ** 2 +
            (dP_dB * sigmaB) ** 2 +
            (dP_dlr * sigma_lambda) ** 2
        )

        return P, sigmaP
