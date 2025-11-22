import numpy as np
from numba import njit, prange, get_num_threads
import time
import pandas as pd

# Vasicek model parameters
a = 0.1       # speed of mean reversion
b = 0.05      # long-term mean
sigma = 0.02  # volatility
r0 = 0.03     # initial rate

T = 1.0       # time horizon in years
N = 252       # time steps
M = 1000     # number of paths
dt = T / N

# -------------------------
# Numba-parallel version
# -------------------------
@njit(parallel=True)
def monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, M):
    dt = T / N
    rates = np.zeros((M, N + 1))
    
    for i in prange(M):
        rates[i, 0] = r0
        for t in range(1, N + 1):
            z = np.random.randn()
            rates[i, t] = rates[i, t - 1] + a * (b - rates[i, t - 1]) * dt + sigma * np.sqrt(dt) * z
            
    return rates

def call_mc_fn(a, b, sigma, r0, T, N, M):
    return monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, M)
    
# -------------------------
# Pure Python version
# -------------------------
def monte_carlo_vasicek_python(a, b, sigma, r0, T, N, M):
    dt = T / N
    rates = np.zeros((M, N + 1))

    for i in range(M):
        rates[i, 0] = r0
        for t in range(1, N + 1):
            z = np.random.randn()
            rates[i, t] = rates[i, t - 1] + a * (b - rates[i, t - 1]) * dt + sigma * np.sqrt(dt) * z

    return rates

def summarize_paths(paths):
    summary = {
            "mean": np.mean(paths[:, -1]),
            "std": np.std(paths[:, -1]),
            "min": np.min(paths[:, -1]),
            "max": np.max(paths[:, -1]),
            "5th_percentile": np.percentile(paths[:, -1], 5),
            "95th_percentile": np.percentile(paths[:, -1], 95),     
    }
    df = pd.DataFrame([summary])
    return df

import numpy as np

def summarize_payoff(paths, payoff_fn):
    """
    Compute mean and standard deviation of the payoff from Monte Carlo paths.

    Parameters:
    - paths: np.ndarray of shape (M, N+1)
    - payoff_fn: callable that accepts (paths or final values) and returns a 1D array of payoffs

    Returns:
    - dict with mean and std of the payoff
    """
    payoffs = payoff_fn(paths[:, -1])  # Use final values of each path
    return {
        "payoff_mean": np.mean(payoffs),
        "payoff_std": np.std(payoffs)
    }

# -------------------------
# Benchmarking
# -------------------------
def print_benchmarking_results():
    print(f"\nBenchmarking with M={M} paths, N={N} time steps")
    print(f"Numba using {get_num_threads()} threads")

    # Warm-up JIT
    monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, 10)

    # Numba
    start = time.time()
    paths_numba = monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, M)
    end = time.time()
    print(f"Numba-parallel: {end - start:.3f} seconds, Final avg rate: {np.mean(paths_numba[:, -1]):.4f}")

    # Pure Python
    start = time.time()
    paths_python = monte_carlo_vasicek_python(a, b, sigma, r0, T, N, M)
    end = time.time()
    print(f"Pure Python   : {end - start:.3f} seconds, Final avg rate: {np.mean(paths_python[:, -1]):.4f}")


if __name__ == '__main__':
    a = 0.1       # speed of mean reversion
    b = 0.05      # long-term mean
    sigma = 0.02  # volatility
    r0 = 0.03     # initial rate

    T = 5.0       # time horizon in years 
    N = 365*5       # time steps
    M = 1000     # number of paths

    start = time.time()
    paths_numba = monte_carlo_vasicek_numba(a, b, sigma, r0, T, N, M)
    end = time.time()
    print(f"Numba-parallel: {end - start:.3f} seconds, Final avg rate: {np.mean(paths_numba[:, -1]):.4f}")
    df2 = summarize_paths(paths_numba)
    print(df2)

    start = time.time()
    paths_numba = call_mc_fn(a, b, sigma, r0, T, N, M)
    end = time.time()
    print(f"Numba-call-another: {end - start:.3f} seconds, Final avg rate: {np.mean(paths_numba[:, -1]):.4f}")
    df2 = summarize_paths(paths_numba)
    print(df2)

    # Pure Python
    start = time.time()
    paths_python = monte_carlo_vasicek_python(a, b, sigma, r0, T, N, M)
    end = time.time()
    print(f"Pure Python   : {end - start:.3f} seconds, Final avg rate: {np.mean(paths_python[:, -1]):.4f}")
    df3 = summarize_paths(paths_python)
    print(df3)
    b=2