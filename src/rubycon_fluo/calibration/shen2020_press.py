from insta_raman.calibration.calibration_core import PressureCalibration
from typing import Tuple
import math

class Shen2020(PressureCalibration):
    """
    Shen G. et al. (2020) IPPS-Ruby scale:

        P(GPa) = A·δ · (1 + C·δ)         with  δ = (λ/λ₀ – 1)

    Constants (one-sigma uncertainties shown for completeness):

        A = 1.870 ×10³ ± 10 GPa
        C = 5.63      ± 0.03
    """
    name = "Shen et al. 2020"
    is_combined = False
    source = (
        "Shen, G., Wang, Y., Dewaele, A., Wu, C., Fratanduono, D. E., … Eggert, J. (2020). "
        "Toward an international practical pressure scale: A proposal for an IPPS ruby gauge (IPPS-Ruby2020). "
        "High Pressure Research, 40(3), 299–314. "
        "doi:10.1080/08957959.2020.1791107"
    )


    _A, _sigmaA = 1.870e3, 1.0e1      # GPa
    _C, _sigmaC = 5.63,     0.03

    def pressure(self,
                 lambda0: float,
                 lambda_r: float,
                 t_ref: float,         # ignored
                 t_meas: float,        # ignored
                 sigma_lambda: float = 0.0
                 ) -> Tuple[float, float]:

        delta = (lambda_r - lambda0) / lambda0
        A, C = self._A, self._C
        P = A * delta * (1 + C * delta)

        # 1-σ error propagation (optional – same as your current code)
        dP_dA = delta * (1 + C * delta)
        dP_dC = A * delta * delta
        dP_dlambda = A * (1 + 2 * C * delta) * (1 / lambda0)

        sigmaP = math.sqrt(
            (dP_dA * self._sigmaA) ** 2 +
            (dP_dC * self._sigmaC) ** 2 +
            (dP_dlambda * sigma_lambda) ** 2
        )
        return P, sigmaP