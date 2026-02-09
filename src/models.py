import pymc as pm
import numpy as np
import arviz as az
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pytensor

# =========================
# Configuration
# =========================
# Disable C compiler to silence g++ warnings
pytensor.config.cxx = ""

# Use non-interactive backend to avoid blocking on Windows
matplotlib.use("Agg")


class BayesianChangePointDetector:
    """Bayesian change point detection using PyMC"""

    def __init__(self, n_samples=2000, n_tune=1000, random_seed=42):
        self.n_samples = n_samples
        self.n_tune = n_tune
        self.random_seed = random_seed
        self.trace = None
        self.model = None

    def fit(self, data):
        """Fit single change point Bayesian model"""
        data = np.asarray(data)
        n = len(data)

        with pm.Model() as model:
            # Change point prior
            tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

            # Priors for means
            mu1 = pm.Normal("mu1", mu=data.mean(), sigma=data.std() * 2)
            mu2 = pm.Normal("mu2", mu=data.mean(), sigma=data.std() * 2)

            # Noise
            sigma = pm.HalfNormal("sigma", sigma=data.std())

            # Mean before/after change
            idx = np.arange(n)
            mu = pm.math.switch(tau > idx, mu1, mu2)

            # Likelihood
            pm.Normal("obs", mu=mu, sigma=sigma, observed=data)

            # Sample
            self.trace = pm.sample(
                draws=self.n_samples,
                tune=self.n_tune,
                chains=2,
                random_seed=self.random_seed,
                return_inferencedata=True,
                target_accept=0.9
            )

            self.model = model

        return self

    def diagnose(self):
        """Print convergence diagnostics"""
        if self.trace is None:
            raise ValueError("Model not fitted yet")

        summary = az.summary(self.trace)
        print("\nModel Summary:")
        print(summary)

        print("\nR-hat values (should be < 1.1):")
        print(summary[["r_hat"]])

        return summary

    def plot_trace(self, filename="traceplot.png"):
        """Plot MCMC trace and save to file (non-interactive)"""
        if self.trace is None:
            raise ValueError("Model not fitted yet")

        az.plot_trace(self.trace)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Trace plot saved to {filename}")

    def save_trace(self, filename="brent_changepoint_trace.nc"):
        """Save posterior to NetCDF"""
        if self.trace is None:
            raise ValueError("Model not fitted yet")

        az.to_netcdf(self.trace, filename)
        print(f"Trace saved to: {filename}")

    def get_change_point_results(self, dates):
        """Extract posterior change point info"""
        if self.trace is None:
            raise ValueError("Model not fitted yet")

        tau_samples = self.trace.posterior["tau"].values.flatten()
        tau_samples = tau_samples.astype(int)

        change_point_dates = [dates[t] for t in tau_samples]

        df = pd.DataFrame({
            "tau": tau_samples,
            "date": change_point_dates
        })

        mode_date = df["date"].mode()[0]
        prob = (df["date"] == mode_date).mean()

        return {
            "all_samples": df,
            "mode_date": mode_date,
            "posterior_probability": prob
        }

    def plot_posterior(self, dates, data, filename="posterior_plot.png"):
        """Plot posterior + data with change point and save to file"""
        if self.trace is None:
            raise ValueError("Model not fitted yet")

        tau_samples = self.trace.posterior["tau"].values.flatten()
        tau_mean = int(tau_samples.mean())

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # Tau posterior
        axes[0, 0].hist(tau_samples, bins=50, density=True, alpha=0.7)
        axes[0, 0].set_title("Posterior of Change Point (tau)")
        axes[0, 0].set_xlabel("Index")
        axes[0, 0].set_ylabel("Density")

        # Means posterior
        az.plot_posterior(self.trace, var_names=["mu1", "mu2"], ax=axes[0, 1])
        axes[0, 1].set_title("Posterior of Segment Means")

        # Data + change point
        axes[1, 0].plot(dates, data, label="Data")
        if tau_mean < len(dates):
            axes[1, 0].axvline(
                dates[tau_mean],
                color="red",
                linestyle="--",
                label="Mean Change Point"
            )
        axes[1, 0].set_title("Data with Change Point")
        axes[1, 0].legend()

        # Sigma posterior
        az.plot_posterior(self.trace, var_names=["sigma"], ax=axes[1, 1])
        axes[1, 1].set_title("Posterior of Sigma")

        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Posterior plot saved to {filename}")

        return fig


# =========================
# Main execution
# =========================
if __name__ == "__main__":
    print("PyMC script started")

    # -------------------------------------------------
    # Example synthetic Brent data (replace with real data)
    # -------------------------------------------------
    np.random.seed(42)
    n = 300
    true_tau = 150
    data = np.concatenate([
        np.random.normal(60, 2, true_tau),
        np.random.normal(75, 2, n - true_tau)
    ])
    dates = pd.date_range(start="2020-01-01", periods=n)

    # -------------------------------------------------
    # Fit model
    # -------------------------------------------------
    detector = BayesianChangePointDetector(
        n_samples=1000,
        n_tune=1000
    )

    detector.fit(data)
    detector.diagnose()
    detector.plot_trace()
    detector.save_trace()

    results = detector.get_change_point_results(dates)
    print("\nMost probable change point date:", results["mode_date"])
    print("Posterior probability:", results["posterior_probability"])

    detector.plot_posterior(dates, data)

    print("Sampling finished")

