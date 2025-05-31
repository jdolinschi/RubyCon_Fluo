from typing import Optional, Tuple

#from insta_raman.calibration.ruby_pressure import RubyPressureScale
#from insta_raman.calibration.ruby_temperature import RubyTemperatureScale
import logging
from insta_raman.calibration.calibration_core import (
    PressureCalibration,
    TemperatureCalibration,
)

logger = logging.getLogger(__name__)


class MeasurementCalculator:
    """
    Manages the calculation of pressure from ruby fluorescence wavelengths,
    incorporating temperature corrections and error propagation.

    Attributes:
        lambda_0: Reference (ambient) R1 wavelength in nm.
        lambda_r: Measured R1 wavelength in nm (uncorrected).
        sigma_lambda: Uncertainty on measured R1 wavelength in nm.
        t_ref: Reference temperature in K (or °C as used by the scale).
        t_meas: Measured temperature in K (or °C as used by the scale).
        pressure_scale: Instance of RubyPressureScale.
        temperature_scale: Instance of RubyTemperatureScale.
    """

    def __init__(self) -> None:
        # Spectral inputs
        self.lambda_0: Optional[float] = None
        self.lambda_r: Optional[float] = None
        self.sigma_lambda: float = 0.0

        # Temperature inputs
        self.t_ref: Optional[float] = None
        self.t_meas: Optional[float] = None

        # Calibration objects
        self.pressure_scale: PressureCalibration | None = None
        self.temperature_scale: TemperatureCalibration | None = None

    # ---------------------- Setters/Getters -----------------------
    def set_reference_wavelength(self, lambda_0: float) -> None:
        """Set the reference (R1) wavelength in nm."""
        self.lambda_0 = float(lambda_0)

    def set_measured_wavelength(self, lambda_r: float, sigma: float = 0.0) -> None:
        """Set the measured R1 wavelength in nm and its uncertainty."""
        self.lambda_r = float(lambda_r)
        self.sigma_lambda = float(sigma)

    def set_reference_temperature(self, t_ref: float) -> None:
        """Set the reference temperature (e.g., room temperature) in K."""
        self.t_ref = float(t_ref)

    def set_measured_temperature(self, t_meas: float) -> None:
        """Set the measured sample temperature in K."""
        self.t_meas = float(t_meas)

    def set_pressure_scale(self, scale: PressureCalibration) -> None:
        self.pressure_scale = scale

    def set_temperature_scale(self, scale: TemperatureCalibration | None) -> None:
        # scale may be None when the chosen pressure-scale is “combined”
        self.temperature_scale = scale

    # -------------------- Core calculation -----------------------
    def calculate_pressure(self) -> Tuple[float, float]:
        """
        Return (P, σP) in GPa.

        • If the selected PressureCalibration is “combined”
          (is_combined == True) it already knows how to fold temperature into
          the equation, so we just hand everything to it.

        • Otherwise we apply the Δλ(T) from the current TemperatureCalibration
          first, then call the pressure scale.
        """
        if self.pressure_scale is None:
            raise ValueError("Pressure calibration not set")

        if self.lambda_0 is None or self.lambda_r is None:
            raise ValueError("λ₀ or λ_r not set")

        if self.pressure_scale.is_combined:
            # The scale takes care of temperature by itself
            t_ref = self.t_ref if self.t_ref is not None else 298.0
            t_meas = self.t_meas if self.t_meas is not None else 298.0
            return self.pressure_scale.pressure(
                lambda0=self.lambda_0,
                lambda_r=self.lambda_r,
                t_ref=t_ref,
                t_meas=t_meas,
                sigma_lambda=self.sigma_lambda,
            )

        # ── pressure-only scale → we must temperature-correct λ_r first ──
        if self.temperature_scale is None:
            raise ValueError("Temperature calibration not set")

        if self.t_ref is None or self.t_meas is None:
            raise ValueError("Temperatures not provided")

        delta_nm = self.temperature_scale.delta_lambda(
            t_ref=self.t_ref,
            t_meas=self.t_meas,
        )
        lambda_r_corr = self.lambda_r - delta_nm

        return self.pressure_scale.pressure(
            lambda0=self.lambda_0,
            lambda_r=lambda_r_corr,
            t_ref=self.t_ref,
            t_meas=self.t_meas,
            sigma_lambda=self.sigma_lambda,
        )
