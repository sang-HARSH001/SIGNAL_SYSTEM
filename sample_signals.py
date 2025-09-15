import numpy as np

def get_sample_signals():
    return {
        'Exponential Decay (Energy)': np.array([np.exp(-n) for n in range(50)]),
        'Sine Wave (Power, Periodic)': np.sin(np.linspace(0, 20 * np.pi, 100)),
        'Cosine Wave (Power, Periodic)': np.cos(np.linspace(0, 20 * np.pi, 100)),
        'Unit Step Signal (Causal)': np.array([1 for _ in range(50)]),
        'Unit Impulse Signal': np.array([1] + [0]*49),
        'Ramp Signal (Causal)': np.array([n for n in range(50)]),
        'Non-Causal Example': np.array([1 if -5 <= n < 5 else 0 for n in range(-10, 10)]),
    }
