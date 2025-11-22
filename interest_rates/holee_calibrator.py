import numpy as np
import plotly.graph_objects as go

class HoLeeCalibrator:
    """
    Calibrate the Ho & Lee short-rate model from discount factor data.
    """

    def __init__(self, tau, Z, sigma, t0=0.0):
        """
        Parameters
        ----------
        tau : array-like
            Time to maturity grid (years), e.g., np.array([0.5, 1, 2, ...]).
        Z : array-like
            Discount factors corresponding to tau.
        sigma : float
            Volatility parameter σ (per annum, same units as rates).
        t0 : float, optional
            Calibration date in years (default = 0.0).
        """
        self.tau = np.asarray(tau, dtype=float)
        self.Z = np.asarray(Z, dtype=float)
        self.sigma = float(sigma)
        self.t0 = float(t0)

        if self.tau.shape != self.Z.shape:
            raise ValueError("tau and Z must have the same shape.")

    def second_derivative(self, x, y):
        """
        Compute the second derivative dy/dx^2 using central differences.

        Parameters
        ----------
        x : np.ndarray
            Grid points (must be increasing).
        y : np.ndarray
            Function values at x.

        Returns
        -------
        np.ndarray
            Second derivative at each x.
        """
        n = len(x)
        d2y = np.zeros(n)

        # Use central differences for interior points
        for i in range(1, n-1):
            dx1 = x[i] - x[i-1]
            dx2 = x[i+1] - x[i]
            d2y[i] = (
                (y[i+1] - y[i]) / dx2 - (y[i] - y[i-1]) / dx1
            ) / ((dx1 + dx2) / 2.0)

        # Forward/backward difference for endpoints
        d2y[0] = (y[2] - 2*y[1] + y[0]) / ((x[1] - x[0])**2)
        d2y[-1] = (y[-1] - 2*y[-2] + y[-3]) / ((x[-1] - x[-2])**2)

        return d2y

    def calibrate_theta(self):
        """
        Calibrate theta_c(t) from Z(t) using the Ho & Lee formula.

        Returns
        -------
        np.ndarray
            Theta values for each tau.
        """
        logZ = np.log(self.Z)
        d2_logZ = self.second_derivative(self.tau, logZ)

        theta = -d2_logZ + self.sigma**2 * (self.tau - self.t0)
        return theta

    def plot_theta(self):
        """
        Plot the calibrated theta(t) over the tau grid using Plotly.
        """
        theta_values = self.calibrate_theta()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.tau,
            y=theta_values,
            mode="lines+markers",
            name=r"$\theta_c(t)$",
            line=dict(color="royalblue"),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title="Calibrated Ho–Lee θ(t)",
            xaxis_title="Time to Maturity (years)",
            yaxis_title=r"θ(t)",
            template="plotly_white",
            hovermode="x unified"
        )

        fig.show()

    def set_sigma(self, sigma):
        self.sigma = sigma

    def plot_multiple_theta(self, sigma_values):
        """
        Plot the calibrated theta(t) over the tau grid using Plotly.
        """


        fig = go.Figure()
        for sigma in sigma_values:
            self.set_sigma(sigma=sigma)
            sigma_pc = np.round(sigma*100, 2)
            theta_values = self.calibrate_theta()
            fig.add_trace(go.Scatter(
                x=self.tau,
                y=theta_values,
                mode="lines",
                name=f"σ = {sigma_pc}%",
                line=dict(width=2) 
            ))

        fig.update_layout(
            title="Calibrated Ho–Lee θ(t)",
            xaxis_title="Time to Maturity (years)",
            yaxis_title="θ(t)",
            template="plotly_white",
            hovermode="x unified",
        )
        fig.update_layout(showlegend=True)

        return fig


# ==== Example usage ====
if __name__ == "__main__":
    tau_grid = np.linspace(0.5, 10, 20)  # years
    Z_example = np.exp(-0.03 * tau_grid)  # flat 3% cc rate
    sigma_val = 0.015

    hl = HoLeeCalibrator(tau_grid, Z_example, sigma_val)
    hl.plot_theta()
