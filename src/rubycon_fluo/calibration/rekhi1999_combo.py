# insta_raman/calibration/rekhi1999_combo.py
from rubycon_fluo.calibration.calibration_core import PressureCalibration
from typing import Tuple
import math


class Rekhi1999(PressureCalibration):
    """
    Rekhi, Dubrovinsky & Saxena (1999) *combined* ruby P–T calibration.
    Validated range: 300–900 K, 0–15 GPa.

        λ₀(T) = λ₀,298 + m·ΔT
        b(T)  = b₀ + b₁·ΔT + b₂·ΔT²
        P     = a/b(T) · [ 100·Δλ / λ₀(T) ]^{ b(T) – 1 }

      where  ΔT = T_meas – 298 K  and  Δλ = λ_R – λ₀(T).
    """
    name        = "Rekhi et al. 1999 (combined)"
    is_combined = True
    source      = ("Rekhi S., Dubrovinsky L.S., Saxena S.K. (1999) Study of temperature–induced "
                   "ruby fluorescence shifts up to a pressure 15 GPa in an externally heated diamond anvil cell. "
                   "High Temperatures–High Pressures 31, 299-305"
                   )

    # ——— constants from Table 1 of the paper ———
    _a  = 19.99                # GPa
    _b0 = 6.75
    _b1 = 9.7540e-4            # K⁻¹
    _b2 = 6.9260e-6            # K⁻²
    _lambda0_298 = 694.2413    # nm
    _m  = 6.0106e-3            # nm K⁻¹

    def pressure(self,
                 lambda0: float,        # user’s ambient λ₀ (nm) – optional
                 lambda_r: float,       # measured R1 (or R̄) wavelength
                 t_ref: float,          # ambient T used for lambda0 (K)
                 t_meas: float,         # sample temperature (K)
                 sigma_lambda: float = 0.0
                 ) -> Tuple[float, float]:

        # 1) allow per-grain λ₀ if the caller supplied one, otherwise use paper value
        lambda0_298 = lambda0 or self._lambda0_298
        delta_T     = t_meas - (t_ref or 298.0)

        # 2) temperature-dependent reference wavelength and exponent
        lambda0_T = lambda0_298 + self._m * delta_T          # nm
        b_T       = self._b0 + self._b1 * delta_T + self._b2 * delta_T ** 2

        # 3) wavelength *shift* (NOT the ratio used by Mao-type scales)
        delta_lambda = lambda_r - lambda0_T                  # nm
        if delta_lambda <= 0.0:
            raise ValueError("Measured line is blue of λ₀(T); "
                             "check inputs or range of validity.")

        x = 100.0 * delta_lambda / lambda0_T                 # dimensionless
        P = (self._a / b_T) * (x ** (b_T - 1.0))             # GPa

        # 4) rough 1-σ error estimate
        dP_dl = (self._a / b_T) * (b_T - 1.0) * (x ** (b_T - 2.0)) * (100.0 / lambda0_T)
        # uncertainty in b(T) and a are small – main contributor is line-position error
        sigmaP = abs(dP_dl) * sigma_lambda
        return P, sigmaP
