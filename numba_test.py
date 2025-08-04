import numpy as np
from numba import njit, prange, get_num_threads
import time

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
