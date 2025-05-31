from rubycon_fluo.calibration.calibration_core import TemperatureCalibration

class Yamaoka1980(TemperatureCalibration):
    """
    Linear fit   Δλ = a · (T – T_ref)   with
        a = 6.80×10⁻³ nm / °C
    """
    name = "Yamaoka et al. 1980"
    source = (
        "Yamaoka, S., Shimomura, O., & Fukunaga, O. (1980). "
        "Simultaneous measurements of temperature and pressure by the ruby fluorescence line. "
        "Proceedings of the Japan Academy, Series B, 56(3), 103–107. "
        " doi:10.2183/pjab.56.103 "
    )
    _a = 6.80e-3        # nm / °C  (paper quotes 6.8×10⁻³)

    def delta_lambda(self, t_ref: float, t_meas: float) -> float:
        return self._a * (t_meas - t_ref)
