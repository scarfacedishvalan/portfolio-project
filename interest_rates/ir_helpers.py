import dash_bootstrap_components as dbc
import numpy as np
from numba import njit, prange, get_num_threads
import time
import pandas as pd


@njit(parallel=True)
def monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, M):
    dt = T / N
    rates = np.zeros((M, N + 1))
    
    for i in prange(M):
        rates[i, 0] = r0
        for t in range(1, N + 1):
            z = np.random.randn()
            rates[i, t] = rates[i, t - 1] + a * (b - rates[i, t - 1]) * dt + sigma  * np.sqrt(rates[i, t - 1]) * z * np.sqrt(dt)
            
    return rates

@njit(parallel=True)
def monte_carlo_cir_numba(a, b, sigma, r0, T, N, M):
    dt = T / N
    rates = np.zeros((M, N + 1))
    
    for i in prange(M):
        rates[i, 0] = r0
        for t in range(1, N + 1):
            z = np.random.randn()
            rates[i, t] = rates[i, t - 1] + a * (b - rates[i, t - 1]) * dt + sigma * np.sqrt(dt) * z
            
    return rates

def render_model_inputs(model_name):
    params = model_config.get(model_name, {}).get("parameters", [])
    input_components = []

    for param in params:
        input_components.append(dbc.Label(param["label"]))
        input_components.append(
            dbc.Input(
                id=param["id"],  # model-specific ID
                type="number",
                value=param["default"],
                step=0.01
            )
        )

    return input_components



model_config = {
    "vasicek": {
        "parameters": [
            {"id": "vasicek-a", "label": "Mean Reversion Speed (a)", "type": "float", "default": 0.1},
            {"id": "vasicek-b", "label": "Long-Term Mean (b)", "type": "float", "default": 0.05},
            {"id": "vasicek-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "vasicek-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    },
    "cir": {
        "parameters": [
            {"id": "cir-a", "label": "Mean Reversion Speed (a)", "type": "float", "default": 0.1},
            {"id": "cir-b", "label": "Long-Term Mean (b)", "type": "float", "default": 0.05},
            {"id": "cir-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "cir-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    },
    "hw": {
        "parameters": [
            {"id": "hw-theta", "label": "Drift Adjustment (θ)", "type": "float", "default": 0.02},
            {"id": "hw-lambda", "label": "Mean Reversion Speed (λ)", "type": "float", "default": 0.1},
            {"id": "hw-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "hw-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    }
}

model_names = {"vasicek": "Vasicek", "cir" : "Cox Ingleson Ross", "hw": "Hull White"}




# Platform: Linux-6.12.12+bpo-cloud-amd64-x86_64-with-glibc2.31
# Architecture: ('64bit', 'ELF')
# CPU Count: 48