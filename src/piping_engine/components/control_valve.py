import math
import pint
from typing import Dict, Any, Tuple, Optional
from piping_engine.components.valve import Valve
from piping_engine.core.units import ensure_quantity, Q_

class ControlValve(Valve):
    """
    Válvula de control que permite variar su apertura.
    Hereda de Valve, pero recalcula el Kv o Cv en función del porcentaje de apertura.
    """
    
    def __init__(self, name: str, from_node: str, to_node: str, 
                 Kv_max: float,
                 diameter: pint.Quantity,
                 characteristic: str = "linear",
                 opening_percent: float = 100.0):
        
        # Inicializamos con K=None, Kv se reescribirá según apertura
        super().__init__(name, from_node, to_node, Kv=Kv_max, diameter=diameter)
        self.Kv_max = Kv_max
        self.characteristic = characteristic.lower()
        self.set_opening(opening_percent)

    def set_opening(self, opening_percent: float):
        """Ajusta el porcentaje de apertura (0 a 100)."""
        self.opening = max(1.0, min(100.0, opening_percent)) / 100.0  # Limitamos mínimo al 1% para evitar singularidad
        
        if self.characteristic == "linear":
            self.Kv_actual = self.Kv_max * self.opening
        elif self.characteristic == "equal_percentage":
            # Asumimos una rangeability típica de 50:1 si no se especifica
            R = 50.0
            self.Kv_actual = self.Kv_max * (R ** (self.opening - 1.0))
        elif self.characteristic == "quick_opening":
            self.Kv_actual = self.Kv_max * math.sqrt(self.opening)
        else:
            raise ValueError(f"Característica de válvula desconocida: {self.characteristic}")
            
        # Recalcular K en base al Kv_actual
        if self.D_m is not None:
            self.K = 1.5996e10 * (self.D_m**4) / (self.Kv_actual**2)

    def pressure_drop(self, mass_flow: float, rho: float, mu: float, p_from: float = 101325.0) -> Tuple[float, Dict[str, Any]]:
        dp, info = super().pressure_drop(mass_flow, rho, mu, p_from)
        info["opening_percent"] = self.opening * 100.0
        info["Kv_actual"] = self.Kv_actual
        info["characteristic"] = self.characteristic
        return dp, info
