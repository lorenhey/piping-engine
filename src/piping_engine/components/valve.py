import math
import pint
from typing import Dict, Any, Tuple, Optional
from piping_engine.components.base import Component
from piping_engine.core.units import ensure_quantity, Q_
from piping_engine.correlations.friction import minor_loss_dp

class Valve(Component):
    """Componente que representa una válvula o accesorio con pérdida localizada."""
    
    def __init__(self, name: str, from_node: str, to_node: str, 
                 K: Optional[float] = None, 
                 Kv: Optional[float] = None, 
                 Cv: Optional[float] = None,
                 diameter: Optional[pint.Quantity] = None):
        super().__init__(name, from_node, to_node)
        self.K = float(K) if K is not None else None
        self.Kv = float(Kv) if Kv is not None else None
        self.Cv = float(Cv) if Cv is not None else None
        self.D_m = ensure_quantity(diameter, "m").magnitude if diameter is not None else None
        
        # Convertir Kv/Cv a K equivalente si se proporciona diámetro
        if self.D_m is not None:
            if self.Kv is not None and self.K is None:
                # Kv en m3/h para dp en bar, sg=1 (rho=1000 kg/m3)
                # K = 1.6e10 * D[m]^4 / Kv^2  (aproximación estándar)
                self.K = 1.5996e10 * (self.D_m**4) / (self.Kv**2)
            elif self.Cv is not None and self.K is None:
                # Kv = 0.865 * Cv
                kv_equiv = 0.865 * self.Cv
                self.K = 1.5996e10 * (self.D_m**4) / (kv_equiv**2)
                
        if self.K is None:
            raise ValueError(f"La válvula {name} debe tener un coeficiente K, o Kv/Cv con un diámetro definido.")

    def pressure_drop(self, mass_flow: float, rho: float, mu: float, p_from: float = 101325.0) -> Tuple[float, Dict[str, Any]]:
        if self.D_m is None:
            raise ValueError(f"Para calcular la pérdida en base a velocidad, {self.name} requiere diámetro.")
            
        area = math.pi * (self.D_m ** 2) / 4.0
        velocity = mass_flow / (rho * area)
        abs_vel = abs(velocity)
        
        dp_mag = minor_loss_dp(self.K, rho, abs_vel)
        dp = math.copysign(dp_mag, velocity)
        
        info = {
            "velocity": velocity,
            "K_factor": self.K,
            "dp_total": dp,
        }
        return dp, info
