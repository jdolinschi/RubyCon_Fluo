from abc import ABC, abstractmethod
from typing import Tuple


class PressureCalibration(ABC):
    """
    Base class for **all** ruby-pressure calibrations.

    Call signature (always the same, even if a particular calibration
    ignores temperature):
        P, σP = cal.pressure(lambda0, lambda_r,
                             t_ref, t_meas,
                             sigma_lambda)
    """
    name: str = "(unnamed pressure calibration)"
    source: str = "(no source set)"  # one-line bibliographic citation
    is_combined: bool = False          # • False → needs external T-cal
                                       # • True  → already includes T

    @abstractmethod
    def pressure(
        self,
        lambda0: float,
        lambda_r: float,
        t_ref: float,
        t_meas: float,
        sigma_lambda: float = 0.0
    ) -> Tuple[float, float]:
        ...
    # ──────────────────────────────────────────────────────────────


class TemperatureCalibration(ABC):
    """
    Pure temperature corrections (no direct pressure information).

        Δλ_nm = cal.delta_lambda(t_ref, t_meas)
    """
    name: str = "(unnamed temperature calibration)"
    source: str = "(no source set)"
    @abstractmethod
    def delta_lambda(
        self,
        t_ref: float,
        t_meas: float
    ) -> float:
        ...

from rubycon_fluo.calibration.rekhi1999_combo import Rekhi1999

from rubycon_fluo.calibration.shen2020_press import Shen2020
from rubycon_fluo.calibration.dewaele2008_press import Dewaele2008
from rubycon_fluo.calibration.mao1986_press import Mao1986
from rubycon_fluo.calibration.dorogokupets2007_press import Dorogokupets2007
from rubycon_fluo.calibration.chijioke2005_press import Chijioke2005

from rubycon_fluo.calibration.yamaoka1980_temp import Yamaoka1980
from rubycon_fluo.calibration.vos1991_temp import Vos1991
from rubycon_fluo.calibration.ragan1992_temp import Ragan1992


# ---------- 3.  Build the registries ----------

PRESSURE_CALIBRATIONS = {
    cls.name: cls() for cls in (Shen2020, Rekhi1999, Dewaele2008, Mao1986, Dorogokupets2007, Chijioke2005, Shen2020)
}

TEMPERATURE_CALIBRATIONS = {
    cls.name: cls() for cls in (Yamaoka1980, Vos1991, Ragan1992)
}