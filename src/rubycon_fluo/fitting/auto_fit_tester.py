import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import OptimizeWarning
import warnings
from tqdm import tqdm
import time

from rubycon_fluo.fitting.auto_fit import AutoFit

class SyntheticSpectrumTester:
    """
    Generate and fit synthetic R1/R2 ruby fluorescence spectra
    with realistic spectrometer sampling and noise, then plot results.
    """
    def __init__(self,
                 center=694.2,
                 amplitude1=100.0,
                 fwhm1=1.0,
                 frac1=0.5,
                 delta=1.39,
                 amplitude2=None,
                 fwhm2=None,
                 frac2=None,
                 baseline=10.0,
                 read_noise_std=1.0,
                 lo=None,
                 hi=None):
        # True (ground-truth) parameters
        self.true_params = {
            'c1': center,
            'A1': amplitude1,
            'w1': fwhm1,
            'f1': frac1,
            'delta': delta,
            'A2': amplitude2 if amplitude2 is not None else amplitude1 * 0.5,
            'w2': fwhm2 if fwhm2 is not None else fwhm1,
            'f2': frac2 if frac2 is not None else frac1,
            'baseline': baseline
        }

        # Spectrometer sampling
        self.step = 0.164  # nm per data point

        # Wavelength window
        halfspan = max(5 * self.true_params['w1'],
                       5 * self.true_params['w2'])
        self.lo = lo if lo is not None else center - halfspan
        self.hi = hi if hi is not None else center + halfspan

        # Noise
        self.read_noise_std = read_noise_std

        # placeholders
        self.x = None
        self.y = None
        self.fit_params = None
        self.fit_cov = None

    def generate_spectrum(self, seed=None):
        """
        Build a two-peak Voigt spectrum, add shot + read noise.
        """
        if seed is not None:
            np.random.seed(seed)

        # wavelength axis
        self.x = np.arange(self.lo,
                           self.hi + self.step/2,
                           self.step)

        # noiseless peaks
        tp = self.true_params
        v1 = AutoFit.pseudo_voigt(self.x,
                                  tp['c1'], tp['A1'], tp['w1'], tp['f1'])
        v2 = AutoFit.pseudo_voigt(self.x,
                                  tp['c1'] - tp['delta'],
                                  tp['A2'], tp['w2'], tp['f2'])

        spectrum = v1 + v2 + tp['baseline']

        # Poisson shot noise + Gaussian read noise
        lam = np.clip(spectrum, 0, None)
        shot = np.random.poisson(lam)
        read = np.random.normal(0,
                                self.read_noise_std,
                                size=self.x.shape)
        self.y = shot + read

    def run_fit(self):
        """
        Fit the current synthetic spectrum with AutoFit,
        then print parameter estimates and fit metrics.
        """
        if self.x is None or self.y is None:
            raise RuntimeError("No spectrum generated yet. Call generate_spectrum().")

        af = AutoFit()
        warnings.simplefilter('ignore', OptimizeWarning)

        popt, pcov = af.fit(self.x, self.y, self.lo, self.hi)

        keys = ['c1', 'A1', 'w1', 'f1', 'delta',
                'A2', 'w2', 'f2', 'baseline']
        self.fit_params = dict(zip(keys, popt))
        self.fit_cov = pcov

        # Print fit results vs true values
        print("\nFit Results:")
        for idx, key in enumerate(keys):
            fitted = self.fit_params[key]
            true = self.true_params[key]
            err = np.sqrt(self.fit_cov[idx, idx])
            diff = fitted - true
            print(f" {key}: fitted = {fitted:.4f} ± {err:.4f}, "
                  f"true = {true:.4f}, diff = {diff:.4f}")

        # Compute and print residual metrics
        model_y = AutoFit.two_peak_model(
            self.x,
            *[self.fit_params[k] for k in keys]
        )
        residuals = self.y - model_y
        rmse = np.sqrt(np.mean(residuals**2))
        dof = len(self.y) - len(popt)
        chi2 = np.sum((residuals / self.read_noise_std)**2)
        red_chi2 = chi2 / dof
        print(f"RMSE = {rmse:.4f}")
        print(f"Reduced chi-squared = {red_chi2:.2f}\n")

    def plot_fit(self):
        """
        Plot noisy data, true peak centers, fitted model, and fitted centers.
        """
        if self.fit_params is None:
            raise RuntimeError("No fit available. Call run_fit() first.")

        # compute fitted model curve
        p = self.fit_params
        model_y = AutoFit.two_peak_model(
            self.x,
            p['c1'], p['A1'], p['w1'], p['f1'],
            p['delta'], p['A2'], p['w2'], p['f2'],
            p['baseline']
        )

        plt.figure(figsize=(8, 5))
        plt.plot(self.x, self.y, '-', label='Noisy data')

        # true centers
        tc1 = self.true_params['c1']
        tc2 = tc1 - self.true_params['delta']
        plt.axvline(tc1, linestyle='--', label='True R1')
        plt.axvline(tc2, linestyle='--', label='True R2')

        # fitted model
        plt.plot(self.x, model_y, '-', label='Fitted model')

        # fitted centers
        fc1 = p['c1']
        fc2 = fc1 - p['delta']
        plt.axvline(fc1, linestyle=':', label='Fitted R1')
        plt.axvline(fc2, linestyle=':', label='Fitted R2')

        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Intensity (counts)')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def run_batch_diagnostics(self,
                              delta_range=(1.0, 2.0),
                              noise_range=(0.5, 5.0),
                              n_points=50):
        """
        Perform batch fitting on a linear grid of delta and noise, but:
          - Record reduced χ² in chi2s
          - Record fit duration in times
          - At the end, make two separate plots:
              1) Δ vs noise colored by reduced χ²
              2) Δ vs noise colored by fit time
        """
        deltas = np.linspace(delta_range[0], delta_range[1], n_points)
        noises = np.linspace(noise_range[0], noise_range[1], n_points)
        D, N = np.meshgrid(deltas, noises)

        chi2s = np.full_like(D, np.nan)
        times = np.full_like(D, np.nan)
        af = AutoFit()

        total = n_points * n_points
        with tqdm(total=total, desc='Batch fitting (diag)') as pbar:
            for i in range(n_points):
                for j in range(n_points):
                    d = D[i, j]
                    noise = N[i, j]

                    # update params and regenerate spectrum
                    self.true_params['delta'] = d
                    self.read_noise_std = noise
                    self.generate_spectrum()

                    # time & fit once
                    t0 = time.perf_counter()
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', OptimizeWarning)
                            popt, _ = af.fit(self.x, self.y, self.lo, self.hi)
                        dt = time.perf_counter() - t0

                        # compute reduced chi2
                        model_y = AutoFit.two_peak_model(self.x, *popt)
                        resid = self.y - model_y
                        dof = len(self.y) - len(popt)
                        rchi2 = np.sum((resid / noise) ** 2) / dof

                        # store metrics
                        chi2s[i, j] = rchi2
                        times[i, j] = dt
                    except RuntimeError:
                        # leave as nan on failure
                        pass

                    pbar.update(1)

        # Plot 1: reduced χ²
        plt.figure(figsize=(8, 6))
        valid = ~np.isnan(chi2s)
        failed = np.isnan(chi2s)
        sc1 = plt.scatter(D[valid], N[valid], c=chi2s[valid])
        plt.scatter(D[failed], N[failed], marker='x', label='no fit')
        plt.xlabel('Delta (nm)')
        plt.ylabel('Read noise std')
        plt.title('Reduced χ² over delta and noise')
        cbar1 = plt.colorbar(sc1)
        cbar1.set_label('Reduced χ²')
        plt.legend()
        plt.tight_layout()

        # Plot 2: fit time
        plt.figure(figsize=(8, 6))
        valid = ~np.isnan(times)
        failed = np.isnan(times)
        sc2 = plt.scatter(D[valid], N[valid], c=times[valid])
        plt.scatter(D[failed], N[failed], marker='x', label='no fit')
        plt.xlabel('Delta (nm)')
        plt.ylabel('Read noise std')
        plt.title('Fit duration over delta and noise')
        cbar2 = plt.colorbar(sc2)
        cbar2.set_label('Time per fit (s)')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def test(self, seed=None):
        """
        One-shot: generate synthetic spectrum, fit it, and plot everything.
        """
        self.generate_spectrum(seed)
        self.run_fit()
        self.plot_fit()


if __name__ == "__main__":
    tester = SyntheticSpectrumTester(
        center=694.2,
        amplitude1=100.0,
        fwhm1=0.8,
        frac1=0.3,
        delta=1.4,
        baseline=10.0,
        read_noise_std=5.0,
        lo=685,
        hi=700
    )
    # example: run batch to explore fitting limits on a 50x50 grid
    #tester.run_batch_diagnostics(delta_range=(0.5, 2.0), noise_range=(1.0, 10.0), n_points=50)
    tester.test(seed=42)
