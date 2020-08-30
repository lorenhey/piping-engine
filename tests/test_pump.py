import pytest
from piping_engine.components.pump import PumpCurve
from piping_engine.core.units import Q_
import numpy as np
import math

def test_pump_curve_affinity():
    flows = [Q_(0, "m**3/s"), Q_(1, "m**3/s"), Q_(2, "m**3/s")]
    heads = [Q_(10, "m"), Q_(8, "m"), Q_(4, "m")]
    
    curve = PumpCurve(flows, heads, speed_hz=50.0)
    
    # A 50 Hz, Q=1 m3/s -> H=8m (aprox, el polyfit lo suavizará)
    h_50 = curve.head_at(1.0, 50.0)
    assert 7.9 < h_50 < 8.1
    
    # A 25 Hz (mitad de velocidad): Q se reduce a mitad, H a un cuarto.
    # El punto equivalente a Q=0.5 m3/s a 25 Hz es Q=1.0 m3/s a 50 Hz.
    # H(25Hz) = H(50Hz) * (25/50)^2 = 8 * 0.25 = 2m
    h_25 = curve.head_at(0.5, 25.0)
    assert 1.9 < h_25 < 2.1
