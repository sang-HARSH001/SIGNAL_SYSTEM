import numpy as np

def get_sample_signals():
    return {
        'Exponential Decay ': np.array([np.exp(-n) for n in range(50)]),
        'Sine Wave ': np.sin(np.linspace(0, 20 * np.pi, 100)),
        'Cosine Wave ': np.cos(np.linspace(0, 20 * np.pi, 100)),
        'Unit Step Signal ': np.array([1 for _ in range(50)]),
        'Unit Impulse Signal': np.array([1] + [0]*49),
        'Ramp Signal': np.array([n for n in range(50)]),

    }


