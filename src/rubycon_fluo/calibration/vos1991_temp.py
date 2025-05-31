"""
Vos & Schouten (1991) temperature shift for ruby R1
---------------------------------------------------

Cubic polynomial (their eq. 3) fitted to Δλ(Å) relative to 300 K:

    Δλ(Å) =  6.591 × 10⁻⁷ · ΔT
           + 7.624 × 10⁻¹⁰ · ΔT²
           − 1.733 × 10⁻¹³ · ΔT³

where ΔT = T − 300 K.  Returned here as **nm**.
"""

from __future__ import annotations

from rubycon_fluo.calibration.calibration_core import TemperatureCalibration


class Vos1991(TemperatureCalibration):
    name   = "Vos & Schouten 1991"
    source = (
        "Vos, W. L., & Schouten, J. A. (1991). On the temperature correction to the ruby pressure scale. "
        "Journal of Applied Physics, 69(9), 6744–6746. "
        "doi:10.1063/1.348903 "
    )

    # polynomial coefficients (Å per K, K², K³)
    _c1 = 6.591e-7
    _c2 = 7.624e-10
    _c3 = -1.733e-13

    # ------------------------------------------------------------------
    def delta_lambda(self, t_ref: float, t_meas: float) -> float:
        """
        Return Δλ (nm) that should be *subtracted* from λ_meas to reference
        both wavelengths to **t_ref**.
        Input temperatures are expected in **Kelvin** (match your UI units).
        """
        def _poly(t: float) -> float:
            dt = t - 300.0
            # result in Å
            return (
                self._c1 * dt
                + self._c2 * dt * dt
                + self._c3 * dt * dt * dt
            )

        # difference in Å → convert to nm
        return (_poly(t_meas) - _poly(t_ref)) * 0.1
