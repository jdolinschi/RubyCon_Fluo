import numpy as np
from scipy.optimize import least_squares
from numba import njit

@njit(cache=True, fastmath=True)
def _pseudo_voigt_nb(x, c, A, w, f):
    sigma = w / (2 * np.sqrt(2 * np.log(2)))
    G = A * np.exp(-0.5 * ((x - c) / sigma) ** 2)
    L = A / (1 + ((x - c) / (w / 2)) ** 2)
    return (1 - f) * G + f * L

@njit(cache=True, fastmath=True)
def _residual_nb(p, x, y):
    return _pseudo_voigt_nb(x, p[0], p[1], p[2], p[3]) - y

@njit(cache=True, fastmath=True)
def _jac_nb(p, x, y):
    c, A, w, f = p
    n = x.shape[0]
    J = np.zeros((n, 4))

    # handy intermediates
    sigma = w / (2 * np.sqrt(2 * np.log(2)))
    t     = (x - c) / sigma
    expv  = np.exp(-0.5 * t * t)
    u     = (x - c) / (w / 2)
    den   = 1 + u * u

    # dA
    J[:, 1] = (1 - f) * expv + f * (1 / den)

    # df
    J[:, 3] = -A * expv + A * (1 / den)

    # dc
    dG_dc = A * expv * t / sigma
    dL_dc = 4 * A * u / (w * den * den)
    J[:, 0] = (1 - f) * dG_dc + f * dL_dc

    # dw
    ds_dw   = 1 / (2 * np.sqrt(2 * np.log(2)))
    dt_dw   = -(x - c) / (sigma * sigma) * ds_dw
    dG_dw   = A * expv * (-t) * dt_dw
    du_dw   = -2 * (x - c) / (w * w)
    dL_dw   = -2 * A * u / (den * den) * du_dw
    J[:, 2] = (1 - f) * dG_dw + f * dL_dw

    return J

class VoigtFitter:
    @staticmethod
    def pseudo_voigt(x, center, amplitude, fwhm, frac):
        """
        frac=0 → pure Gaussian; frac=1 → pure Lorentzian.
        fwhm = full width at half maximum.
        """
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        G = amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2)
        L = amplitude * (1 / (1 + ((x - center) / (fwhm / 2)) ** 2))
        return (1 - frac) * G + frac * L

    def fit(self, x, y):
        """
        JIT‑accelerated least‑squares Voigt fit.
        Returns (popt, pcov) like curve_fit did.
        """
        # -------- initial guesses (same as before) --------
        p0 = [
            float(x[np.nanargmax(y)]),  # center
            float(np.nanmax(y)),  # amplitude
            float((x.max() - x.min()) / 10),  # fwhm
            0.5  # fraction
        ]

        lower = [-np.inf, 0, 0, 0]
        upper = [np.inf, np.inf, np.inf, 1]

        # -------- least‑squares with analytic Jacobian ----
        res = least_squares(
            _residual_nb,
            p0,
            jac=_jac_nb,
            bounds=(lower, upper),
            args=(x, y),
            method='trf',
            xtol=1e-8,
            ftol=1e-8,
            max_nfev=2000
        )
        popt = res.x

        # -------- covariance estimate (same recipe) -------
        m, n = x.size, len(p0)
        ssr = np.sum(res.fun ** 2)
        sigma2 = ssr / max(1, m - n)
        JTJ = res.jac.T.dot(res.jac)
        pcov = np.linalg.pinv(JTJ) * sigma2

        return popt, pcov

    def model(self, x, center, amplitude, fwhm, frac):
        return self.pseudo_voigt(x, center, amplitude, fwhm, frac)
