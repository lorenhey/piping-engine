import math
import scipy.optimize
from typing import Tuple, Dict, Any
from piping_engine.core.exceptions import PhysicsWarning
import warnings

def reynolds_number(velocity: float, diameter: float, density: float, viscosity: float) -> float:
    """Calcula el número de Reynolds. Todas las entradas en MKS (SI)."""
    if viscosity <= 0:
        raise ValueError("La viscosidad debe ser positiva.")
    return (density * abs(velocity) * diameter) / viscosity


def haaland_friction_factor(re: float, rel_roughness: float) -> float:
    """Factor de fricción de Darcy según la aproximación explícita de Haaland."""
    if re < 2300:
        return 64.0 / max(re, 1e-10)
    
    inv_sqrt_f = -1.8 * math.log10((rel_roughness / 3.7)**1.11 + 6.9 / re)
    return (1.0 / inv_sqrt_f)**2


def colebrook_white_friction_factor(re: float, rel_roughness: float) -> Tuple[float, Dict[str, Any]]:
    """
    Factor de fricción de Darcy resolviendo la ecuación implícita de Colebrook-White.
    Retorna (f_darcy, info_convergencia).
    """
    if re < 2300:
        return 64.0 / max(re, 1e-10), {"method": "laminar", "iterations": 0}
        
    if re >= 2300 and re < 4000:
        warnings.warn(f"Flujo transicional detectado (Re = {re:.0f}). El factor de fricción es incierto.", PhysicsWarning)
        
    def colebrook(f):
        return 1.0 / math.sqrt(f) + 2.0 * math.log10(rel_roughness / 3.7 + 2.51 / (re * math.sqrt(f)))

    # Valor inicial usando Haaland
    f_guess = haaland_friction_factor(re, rel_roughness)
    
    try:
        # Resolvemos f usando fsolve
        sol = scipy.optimize.root_scalar(colebrook, x0=f_guess, x1=f_guess*1.1, method='secant', xtol=1e-6)
        if sol.converged:
            return sol.root, {"method": "colebrook_white", "iterations": sol.iterations, "converged": True}
        else:
            return f_guess, {"method": "haaland_fallback", "iterations": sol.iterations, "converged": False}
    except Exception:
        return f_guess, {"method": "haaland_fallback", "iterations": 0, "converged": False, "error": "Solver failed"}


def darcy_weisbach_dp(f: float, L: float, D: float, rho: float, v: float) -> float:
    """Pérdida de presión distribuida según Darcy-Weisbach en Pascales."""
    return f * (L / D) * 0.5 * rho * v**2

def minor_loss_dp(K: float, rho: float, v: float) -> float:
    """Pérdida de presión localizada en Pascales."""
    return K * 0.5 * rho * v**2
