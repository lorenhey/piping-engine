import pytest
import math
from piping_engine.correlations.friction import reynolds_number, haaland_friction_factor, colebrook_white_friction_factor

def test_reynolds_number():
    re = reynolds_number(velocity=2.0, diameter=0.1, density=1000.0, viscosity=0.001)
    assert math.isclose(re, 200000.0)

def test_haaland():
    re = 100000.0
    eps_d = 0.001
    f = haaland_friction_factor(re, eps_d)
    assert 0.021 < f < 0.023  # Valor típico para este Re y rugosidad

def test_colebrook_white_turbulent():
    re = 100000.0
    eps_d = 0.001
    f, info = colebrook_white_friction_factor(re, eps_d)
    assert info["converged"]
    assert 0.021 < f < 0.023
    
def test_colebrook_white_laminar():
    re = 1000.0
    eps_d = 0.001
    f, info = colebrook_white_friction_factor(re, eps_d)
    assert info["method"] == "laminar"
    assert math.isclose(f, 0.064)
