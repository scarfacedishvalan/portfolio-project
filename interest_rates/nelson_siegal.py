import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc


class NelsonSiegelFitter:
    def __init__(self, tau_obs, y_obs, tau_grid = None, lam_grid = None):
        self.tau_obs = np.array(tau_obs)
        self.y_obs = np.array(y_obs)
        self.lmbda = None
        self.betas = None
        self.best_sse = None
        self.tau_grid = [1/365] + list(np.linspace(0.25, 10, 40)) if tau_grid is None else tau_grid       
        self.lam_grid = np.linspace(0.1, 5, 50) if lam_grid is None else lam_grid
        self.sse_record_df = pd.DataFrame(columns=["lambda", "beta0", "beta1", "beta2", "sse"])

    @staticmethod
    def ns_basis(taus, lam):
        f1 = (1 - np.exp(-lam * taus)) / (lam * taus)
        f2 = f1 - np.exp(-lam * taus)
        return f1, f2

    @staticmethod
    def df1(lam, tau):
        return (np.exp(-lam * tau)*(lam*tau + 1) - 1) / (lam * tau**2)

    @staticmethod
    def df2(lam, tau):
        f1p = NelsonSiegelFitter.df1(lam, tau)
        return f1p + lam*np.exp(-lam*tau)

    @staticmethod
    def d2f1(lam, tau):
        return (-lam**2 * tau**2 * np.exp(-lam * tau)
                - 2 * (np.exp(-lam * tau) * (lam * tau + 1) - 1)
            ) / (lam * tau**3)

    @staticmethod
    def d2f2(lam, tau):
        f1pp = NelsonSiegelFitter.d2f1(lam, tau)
        return f1pp - lam**2 * np.exp(-lam * tau)

    @staticmethod
    def dy(lam, tau, beta0, beta1, beta2):
        """First derivative of y(tau) in Nelson–Siegel"""
        return beta1 * NelsonSiegelFitter.df1(lam, tau) + beta2 * NelsonSiegelFitter.df2(lam, tau)

    @staticmethod
    def d2y(lam, tau, beta0, beta1, beta2):
        """Second derivative of y(tau) in Nelson–Siegel"""
        return beta1 * NelsonSiegelFitter.d2f1(lam, tau) + beta2 * NelsonSiegelFitter.d2f2(lam, tau)



    @staticmethod
    def nelson_siegel(lmbda, betas, tau):
        f1 = (1 - np.exp(-lmbda * tau)) / (lmbda * tau)
        f2 = f1 - np.exp(-lmbda * tau)
        return betas[0] + betas[1] * f1 + betas[2] * f2

    def fit(self):
        best_sse = np.inf
        best_params = None
        dlist = []
        for lam in self.lam_grid:
            f1, f2 = self.ns_basis(self.tau_obs, lam)
            X = np.vstack([np.ones_like(self.tau_obs), f1, f2]).T
            betas, *_ = np.linalg.lstsq(X, self.y_obs, rcond=None)
            yhat = np.dot(X, betas)
            sse = np.sum((self.y_obs - yhat) ** 2)
            d = {"lambda": lam, "beta0": betas[0], "beta1": betas[1], "beta2": betas[2], "sse": sse}
            dlist.append(d)
            if sse < best_sse:
                best_sse = sse
                best_params = (lam, betas)

        self.sse_record_df = pd.DataFrame(dlist)

        self.lmbda, self.betas = best_params
        self.best_sse = best_sse
        return self.lmbda, self.betas

    def predict_curve(self, tau_values=None, lmbda = None, betas = None):
        if lmbda is None:
            lmbda = self.lmbda
        if betas is None:
            betas = self.betas
        if tau_values is None:
            tau_values = self.tau_grid
        y_values = [self.nelson_siegel(lmbda, betas, t) for t in tau_values]
        return pd.DataFrame({"tau": tau_values, "y": y_values})

    def plot(self, tau_values = None):
        if tau_values is None:
            tau_values = self.tau_grid
        df_to_plot = self.predict_curve(tau_values=tau_values)

        fig = px.line(df_to_plot, x="tau", y="y", title="Nelson–Siegel Yield Curve")

        # Observed points
        fig.add_trace(go.Scatter(
            x=self.tau_obs,
            y=self.y_obs,
            mode="markers",
            name="Observed",
            marker=dict(size=8, color="red")
        ))

        # Guide lines
        for t, y in zip(self.tau_obs, self.y_obs):
            fig.add_shape(type="line", x0=t, y0=0, x1=t, y1=y,
                          line=dict(color="gray", width=1, dash="dot"))
            fig.add_shape(type="line", x0=0, y0=y, x1=t, y1=y,
                          line=dict(color="gray", width=1, dash="dot"))

        # LaTeX parameters as annotation
        fitted_params_string = (
            fr"$\lambda = {self.lmbda:.2f},\ \beta_0 = {self.betas[0]:.2f},\ \beta_1 = {self.betas[1]:.2f},\ \beta_2 = {self.betas[2]:.2f}$"
        )

        fig.update_layout(
            xaxis_title="Maturity (years)",
            yaxis_title="Yield",
            template="plotly_white",
            title=dict(text="Nelson–Siegel Yield Curve", x=0.5, xanchor="center"),
            annotations=[dict(
                text=fitted_params_string,
                x=0.5,
                y=1.08,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=12),
                align="center"
            )]
        )

        return fig

    def predict_curve_with_lmbda(self, lmbda, tau_values = None):
        sse_record_df = self.sse_record_df.copy()      
        match_cond =  np.isclose(sse_record_df["lambda"], lmbda, atol=1e-4)              
        if not match_cond.any():
            self.lam_grid = sorted(self.lam_grid + [lmbda])
            self.fit()
            sse_record_df = self.sse_record_df.copy()
        beta0 = sse_record_df.loc[match_cond, "beta0"].values[0]
        beta1 = sse_record_df.loc[match_cond, "beta1"].values[0] 
        beta2 = sse_record_df.loc[match_cond, "beta2"].values[0]   
        betas = np.array([beta0, beta1, beta2])
        df = self.predict_curve(tau_values=tau_values, lmbda=lmbda, betas=betas)
        return df

    def add_lambda_trace(self, lmbda, fig, tau_values = None):
        if tau_values is None:
            tau_values = self.tau_grid
            
        df_trace = self.predict_curve_with_lmbda(lmbda=lmbda, tau_values=tau_values)
        curve_name = f"λ={lmbda:.2f}"    

        norm_val = (lmbda - 0.1) / (10 - 0.1)
        norm_val = max(0, min(norm_val, 1))  # clamp to [0, 1]
        
        color_scale = pc.get_colorscale('Turbo')  # or 'Viridis', 'Plasma', etc.
        color_rgb = pc.sample_colorscale(color_scale, norm_val)[0]

        fig.add_trace(go.Scatter(
            x=df_trace["tau"],
            y=df_trace["y"],
            mode="lines",
            name=curve_name, 
            line=dict(color=color_rgb)            
        ))
        fig.update_layout(showlegend=True)
        return fig


    def base_yield_plot(self, tau_values = None):
        if tau_values is None:
            tau_values = self.tau_grid

        fig = go.Figure()

        # Observed points
        fig.add_trace(go.Scatter(
            x=self.tau_obs,
            y=self.y_obs,
            mode="markers",
            name="Observed",
            marker=dict(size=8, color="red")
        ))

        # Guide lines
        for t, y in zip(self.tau_obs, self.y_obs):
            fig.add_shape(type="line", x0=t, y0=0, x1=t, y1=y,
                          line=dict(color="gray", width=1, dash="dot"))
            fig.add_shape(type="line", x0=0, y0=y, x1=t, y1=y,
                          line=dict(color="gray", width=1, dash="dot"))

        fig.update_layout(
            xaxis_title="Maturity (years)",
            yaxis_title="Yield",
            template="plotly_white",
            title=dict(text="Nelson–Siegel Yield Curve", x=0.5, xanchor="center"),
        )
        fig.update_layout(showlegend=True)

        return fig        
    
    def theta_analytic(self, a, sigma, tau_values=None):
        """
        Analytic calculation of theta(t) for given a and sigma
        using:
        
        theta(t) = (2 y'(t) + t y''(t))
                   + a ( y(t) + t y'(t) )
                   + (sigma^2 / (2a)) * (1 - exp(-2a t))

        Parameters
        ----------
        a : float
            Mean reversion speed.
        sigma : float
            Volatility parameter.
        tau_values : array-like, optional
            Maturities at which to compute theta. Defaults to self.tau_grid.

        Returns
        -------
        DataFrame with tau and theta.
        """
        if tau_values is None:
            tau_values = self.tau_grid

        lam = self.lmbda
        b0, b1, b2 = self.betas

        results = []
        for tau in tau_values:
            y_val = self.nelson_siegel(lam, (b0, b1, b2), tau)
            dy_val = self.dy(lam, tau, b0, b1, b2)
            d2y_val = self.d2y(lam, tau, b0, b1, b2)

            theta_val = (2 * dy_val + tau * d2y_val) \
                        + a * (y_val + tau * dy_val) \
                        + (sigma**2 / (2 * a)) * (1 - np.exp(-2 * a * tau))

            results.append((tau, theta_val))

        return pd.DataFrame({"tau": tau_values, "theta": [t[1] for t in results]})

    @staticmethod
    def zero_rates_to_discount_factors(zero_rates, tau):
        zero_rates = np.asarray(zero_rates, dtype=float)
        tau = np.asarray(tau, dtype=float)
        
        if zero_rates.shape != tau.shape:
            raise ValueError("zero_rates and tau must have the same shape")
        
        # Formula: Z(T) = exp(- y_cc(T) * T )
        discount_factors = np.exp(-zero_rates * tau)
        
        return discount_factors


    def plot_sse_vs_lambda(self):
        """
        Creates a Plotly scatter plot of SSE vs Lambda.
        Beta values are embedded in customdata for use in Dash callbacks.
        """
        df = self.sse_record_df.copy()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["lambda"],
            y=df["sse"],
            mode="markers",
            marker=dict(size=8, color="blue"),
            name="SSE",
            customdata=df[["beta0", "beta1", "beta2"]].values,
            hovertemplate=(
                "λ: %{x}<br>"
                "SSE: %{y}<br>"
                "β0: %{customdata[0]}<br>"
                "β1: %{customdata[1]}<br>"
                "β2: %{customdata[2]}<extra></extra>"
            )
        ))

        fig.update_layout(
            title="SSE vs λ",
            xaxis_title="λ",
            yaxis_title="Sum of Squared Errors (SSE)",
            template="plotly_white",
            hovermode="closest",
            margin=dict(l=40, r=40, t=60, b=40)
        )

        return fig

    def plot_discount_curve(self, df_fit):
        # Make sure discount curve exists
        if "Z" not in df_fit.columns:
            df_fit["Z"] = np.exp(-df_fit["y"] * df_fit["tau"])

        fig = go.Figure()

        # Add discount curve line
        fig.add_trace(
            go.Scatter(
                x=df_fit["tau"],
                y=df_fit["Z"],
                mode="lines+markers",
                name="Discount Curve"
            )
        )

        # Layout
        fig.update_layout(
            title="Discount Curve from Zero Rates",
            xaxis_title="Maturity (Years)",
            yaxis_title="Discount Factor Z(t)",
            template="plotly_white"
        )
        return fig


if __name__ == '__main__':
    # Example usage
    tau_obs = [0.25, 0.5, 1, 2, 3, 5, 10]
    y_obs = [0.025, 0.027, 0.03, 0.032, 0.034, 0.038, 0.04]

    nsf = NelsonSiegelFitter(tau_obs, y_obs)
    l, b  = nsf.fit()
    print(l, b)
    # fig = nsf.plot()
    # fig.show()
