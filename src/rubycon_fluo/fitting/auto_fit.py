import numpy as np
from scipy.optimize import least_squares
from numba import njit

# JIT-compiled Voigt functions and derivatives
@njit(cache=True, fastmath=True)
def pseudo_voigt_nb(x, center, amplitude, fwhm, frac):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    G = amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2)
    L = amplitude / (1 + ((x - center) / (fwhm / 2)) ** 2)
    return (1 - frac) * G + frac * L

@njit(cache=True, fastmath=True)
def two_peak_model_nb(x, c1, A1, w1, f1, delta, A2, w2, f2, b):
    v1 = pseudo_voigt_nb(x, c1,  A1, w1, f1)
    v2 = pseudo_voigt_nb(x, c1 - delta, A2, w2, f2)
    return v1 + v2 + b

@njit(cache=True, fastmath=True)
def residual_nb(p, x, y):
    return two_peak_model_nb(x,
                              p[0], p[1], p[2], p[3],
                              p[4], p[5], p[6], p[7], p[8]) - y

@njit(cache=True, fastmath=True)
def jac_nb(p, x, y):
    # Analytical Jacobian of two_peak_model_nb
    c1, A1, w1, f1, delta, A2, w2, f2, b = p
    n = x.shape[0]
    J = np.zeros((n, 9))
    # Peak1 partials
    sigma1 = w1 / (2 * np.sqrt(2 * np.log(2)))
    t1 = (x - c1) / sigma1
    exp1 = np.exp(-0.5 * t1 * t1)
    u1 = (x - c1) / (w1 / 2)
    den1 = 1 + u1 * u1
    # dA1
    J[:,1] = (1 - f1) * exp1 + f1 * (1 / den1)
    # df1
    J[:,3] = -A1 * exp1 + A1 * (1 / den1)
    # db
    J[:,8] = 1.0
    # dc1 from peak1
    dG1_dc = A1 * exp1 * t1 / sigma1
    dL1_dc = 4 * A1 * u1 / (w1 * den1 * den1)
    J[:,0] = (1 - f1) * dG1_dc + f1 * dL1_dc
    # dw1
    ds1_dw = 1 / (2 * np.sqrt(2 * np.log(2)))
    dt1_dw = -(x - c1) / (sigma1 * sigma1) * ds1_dw
    dG1_dw = A1 * exp1 * (-t1) * dt1_dw
    du1_dw = -2 * (x - c1) / (w1 * w1)
    dL1_dw = -2 * A1 * u1 / (den1 * den1) * du1_dw
    J[:,2] = (1 - f1) * dG1_dw + f1 * dL1_dw
    # Peak2 partials (center2 = c1 - delta)
    c2 = c1 - delta
    sigma2 = w2 / (2 * np.sqrt(2 * np.log(2)))
    t2 = (x - c2) / sigma2
    exp2 = np.exp(-0.5 * t2 * t2)
    u2 = (x - c2) / (w2 / 2)
    den2 = 1 + u2 * u2
    # dA2
    J[:,5] = (1 - f2) * exp2 + f2 * (1 / den2)
    # df2
    J[:,7] = -A2 * exp2 + A2 * (1 / den2)
    # dc1 from peak2
    dG2_dc2 = A2 * exp2 * t2 / sigma2
    dL2_dc2 = 4 * A2 * u2 / (w2 * den2 * den2)
    J[:,0] += (1 - f2) * dG2_dc2 + f2 * dL2_dc2
    # ddelta (negative of dc2)
    J[:,4] = -((1 - f2) * dG2_dc2 + f2 * dL2_dc2)
    # dw2
    ds2_dw = 1 / (2 * np.sqrt(2 * np.log(2)))
    dt2_dw = -(x - c2) / (sigma2 * sigma2) * ds2_dw
    dG2_dw = A2 * exp2 * (-t2) * dt2_dw
    du2_dw = -2 * (x - c2) / (w2 * w2)
    dL2_dw = -2 * A2 * u2 / (den2 * den2) * du2_dw
    J[:,6] = (1 - f2) * dG2_dw + f2 * dL2_dw
    return J

class AutoFit:
    """
    Two-peak Voigt auto-fitter for R1 & R2 peaks in ruby fluorescence.
    Uses JIT-accelerated least_squares under the hood for speed and precision.
    """

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

    @staticmethod
    def two_peak_model(x, c1, A1, w1, f1, delta, A2, w2, f2, baseline):
        v1 = AutoFit.pseudo_voigt(x, c1, A1, w1, f1)
        v2 = AutoFit.pseudo_voigt(x, c1 - delta, A2, w2, f2)
        return v1 + v2 + baseline

    def fit(self, wl: np.ndarray, counts: np.ndarray, lo: float, hi: float):
        """
        Fit two Voigt peaks between wl in [lo, hi] using a JIT-accelerated
        least_squares solver. Returns (popt, pcov) with the same shape as
        the old curve_fit interface.
        """
        mask = (wl >= lo) & (wl <= hi)
        x = wl[mask]
        y = counts[mask]
        if x.size == 0:
            raise ValueError("No data in fitting range")

        # Initial guesses (same strategy as before)
        i0 = np.argmax(y)
        c1_0, A1_0 = x[i0], y[i0]
        w1_0, f1_0 = 1.0, 0.5
        delta0 = 1.39
        A2_0, w2_0, f2_0 = A1_0 * 0.5, w1_0, f1_0
        b0 = np.min(y)

        p0 = np.array([c1_0, A1_0, w1_0, f1_0,
                       delta0, A2_0, w2_0, f2_0, b0])
        lower = np.array([lo, 0, 0, 0, 0.5, 0, 0, 0, -np.inf])
        upper = np.array([hi, np.inf, np.inf, 1, 2.5, np.inf, np.inf, 1, np.inf])

        # Run JIT-accelerated least_squares
        res = least_squares(
            residual_nb,
            p0,
            jac=jac_nb,
            bounds=(lower, upper),
            args=(x, y),
            method='trf',
            xtol=1e-12,
            ftol=1e-12,
            max_nfev=5000
        )
        popt = res.x

        # Estimate covariance matrix: cov ≈ inv(J^T J) * σ²
        m, n = x.size, p0.size
        ssr = np.sum(res.fun**2)
        sigma2 = ssr / (m - n)
        # pinv in case J^T J is ill-conditioned
        JTJ = res.jac.T.dot(res.jac)
        pcov = np.linalg.pinv(JTJ) * sigma2

        return popt, pcov
