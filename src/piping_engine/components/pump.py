import numpy as np
import math
import pint
from typing import Dict, Any, Tuple, Optional, List
from piping_engine.components.base import Component
from piping_engine.core.units import ensure_quantity, Q_

class PumpCurve:
    """Curva de una bomba centrífuga."""
    
    def __init__(self, flows: List[pint.Quantity], heads: List[pint.Quantity], 
                 efficiencies: Optional[List[float]] = None,
                 speed_hz: float = 50.0):
        
        # Convertir a unidades base (m3/s y m)
        self.flows_m3s = np.array([f.to("m**3/s").magnitude for f in flows])
        self.heads_m = np.array([h.to("m").magnitude for h in heads])
        
        if efficiencies is not None:
            self.efficiencies = np.array(efficiencies)
        else:
            self.efficiencies = None
            
        self.ref_speed = speed_hz
        
        # Ajuste polinomial (grado 2 suele ser adecuado para bombas centrífugas)
        # H = A*Q^2 + B*Q + C
        self.poly_H = np.polyfit(self.flows_m3s, self.heads_m, 2)
        
        if self.efficiencies is not None:
            self.poly_eta = np.polyfit(self.flows_m3s, self.efficiencies, 3)

    def head_at(self, q_m3s: float, speed_hz: float) -> float:
        """Retorna la carga (m) para el caudal y velocidad dados usando leyes de afinidad."""
        # Ley de afinidad: Q1/Q2 = N1/N2 -> Q_ref = q_m3s * (N_ref / N)
        ratio = self.ref_speed / speed_hz
        q_ref = q_m3s * ratio
        
        # Evaluar H en curva de referencia
        h_ref = np.polyval(self.poly_H, q_ref)
        
        # H1/H2 = (N1/N2)^2 -> H = h_ref * (N / N_ref)^2
        h_actual = h_ref * (speed_hz / self.ref_speed)**2
        return h_actual

class Pump(Component):
    """Componente que representa una bomba centrífuga."""
    
    def __init__(self, name: str, from_node: str, to_node: str, curve: PumpCurve, speed_hz: float = 50.0):
        super().__init__(name, from_node, to_node)
        self.curve = curve
        self.speed_hz = speed_hz

    def pressure_drop(self, mass_flow: float, rho: float, mu: float, p_from: float = 101325.0) -> Tuple[float, Dict[str, Any]]:
        """
        Una bomba 'añade' presión, por lo que la caída de presión es negativa en la dirección del flujo.
        dp = P_from - P_to = - (rho * g * H)
        """
        if mass_flow < 0:
            # Flujo inverso a través de bomba, modelo muy simplificado o error. 
            # Por ahora asignamos una gran resistencia.
            q_m3s = abs(mass_flow) / rho
            dp_fric = 1e6 * q_m3s**2 # Penalización alta
            return math.copysign(dp_fric, mass_flow), {"regime": "reverse_flow", "head_m": 0.0}

        q_m3s = mass_flow / rho
        h_m = self.curve.head_at(q_m3s, self.speed_hz)
        
        dp_pump = -rho * 9.80665 * h_m  # Negativo porque incrementa la presión hacia adelante
        
        info = {
            "flow_m3s": q_m3s,
            "head_m": h_m,
            "speed_hz": self.speed_hz,
            "dp_total": dp_pump,
            "regime": "pump_operation"
        }
        return dp_pump, info
