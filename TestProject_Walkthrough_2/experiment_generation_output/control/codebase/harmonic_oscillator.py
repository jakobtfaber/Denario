# filename: codebase/harmonic_oscillator.py
import numpy as np

def nonlinear_damping(x, b0, b1):
    """
    Calculate the non-linear damping coefficient.
    
    Parameters:
    x (float): Displacement of the oscillator.
    b0 (float): Linear damping coefficient.
    b1 (float): Non-linear damping coefficient factor.
    
    Returns:
    float: Total damping coefficient.
    """
    return b0 + b1 * x**2

mass_range = np.linspace(0.1, 5.0, 50)
spring_constant_range = np.linspace(1.0, 100.0, 50)
b0_range = np.linspace(0.1, 1.0, 10)
b1_range = np.linspace(0.0, 0.5, 10)