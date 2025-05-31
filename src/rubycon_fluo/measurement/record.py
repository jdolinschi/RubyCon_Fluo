from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

@dataclass
class MeasurementRecord:
    # Primary R1 results
    name: str
    r1_wavelength: float
    pressure: str
    temperature: str
    pressure_calib: str
    temp_calib: str

    # the raw spectrum
    x_wavelength: np.ndarray = field(repr=False)
    y_intensity: np.ndarray = field(repr=False)

    # acquisition settings
    integration_time_ms: float
    scans: int

    # reference settings
    reference_wavelength: float
    reference_temperature: float

    # instrument + fit metadata for R1
    spectrometer_id: str
    fit_type: str                    # "Manual", "Manual Voigt", or "Auto-fit Voigt"
    voigt_popt: Optional[List[float]] = None  # [center, amp, fwhm, frac]
    voigt_pcov: Optional[List[List[float]]] = None  # covariance matrix as nested lists

    # Secondary R2 Voigt results (only for Auto-fit Voigt)
    r2_wavelength: Optional[float] = None
    r2_voigt_popt: Optional[List[float]] = None
    r2_voigt_pcov: Optional[List[List[float]]] = None

    baseline: Optional[float] = None

    def to_metadata_block(self) -> str:
        lines = [
            f"name: {self.name}",
            f"r1_wavelength_nm: {self.r1_wavelength}",
            f"pressure_gpa: {self.pressure}",
            f"temperature_c: {self.temperature}",
            f"pressure_calib: {self.pressure_calib}",
            f"temperature_calib: {self.temp_calib}",
            f"integration_time_ms: {self.integration_time_ms}",
            f"scans: {self.scans}",
            f"reference_wavelength_nm: {self.reference_wavelength}",
            f"reference_temperature_c: {self.reference_temperature}",
            f"spectrometer_id: {self.spectrometer_id}",
            f"fit_type: {self.fit_type}",
        ]

        # R1 Voigt parameters (always include labels)
        popt_str = ",".join(map(str, self.voigt_popt)) if self.voigt_popt else ""
        cov_str  = ";".join(
            ",".join(map(str, row)) for row in self.voigt_pcov
        ) if self.voigt_pcov else ""
        lines.append(f"voigt_popt: {popt_str}")
        lines.append(f"voigt_pcov: {cov_str}")

        # R2 results (always include labels)
        lines.append(f"r2_wavelength_nm: {self.r2_wavelength if self.r2_wavelength is not None else ""}")
        r2_popt = ",".join(map(str, self.r2_voigt_popt)) if self.r2_voigt_popt else ""
        r2_cov  = ";".join(
            ",".join(map(str, row)) for row in self.r2_voigt_pcov
        ) if self.r2_voigt_pcov else ""
        lines.append(f"r2_voigt_popt: {r2_popt}")
        lines.append(f"r2_voigt_pcov: {r2_cov}")

        # Baseline (always include label, may be empty)
        base_str = str(self.baseline) if self.baseline is not None else ""
        lines.append(f"baseline: {base_str}")

        return "\n".join(lines)

    def to_data_dump(self) -> str:
        header = "wavelength_nm, intensity"
        rows = (f"{x}, {y}" for x, y in zip(self.x_wavelength, self.y_intensity))
        return "\n".join([header, *rows])
