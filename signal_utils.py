import numpy as np

def calculate_energy(signal):
    return np.sum(np.abs(signal) ** 2)

def calculate_power(signal):
    return np.mean(np.abs(signal) ** 2)

def is_periodic(signal, max_lag=100):
    N = len(signal)
    for period in range(1, max_lag):
        periodic = True
        for i in range(N - period):
            if not np.isclose(signal[i], signal[i + period], atol=1e-5):
                periodic = False
                break
        if periodic:
            return True, period
    return False, None

def is_causal(signal):
    n_values = np.arange(-len(signal)//2, len(signal)//2)
    for n, val in zip(n_values, signal):
        if n < 0 and abs(val) > 1e-5:
            return False
    return True
def is_anti_causal(signal):
    n_values = np.arange(-len(signal)//2, len(signal)//2)
    for n, val in zip(n_values, signal):
        if n > 0 and abs(val) > 1e-5:
            return False
    return True
    