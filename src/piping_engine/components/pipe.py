import math
from typing import Dict, Any, Tuple
from piping_engine.components.base import Component
from piping_engine.core.geometry import PipeGeometry
from piping_engine.correlations.friction import reynolds_number, colebrook_white_friction_factor, darcy_weisbach_dp

class Pipe(Component):
    """Componente que representa un tramo de tubería recta."""
    
    def __init__(self, name: str, from_node: str, to_node: str, geometry: PipeGeometry):
        super().__init__(name, from_node, to_node)
        self.geometry = geometry

    def pressure_drop(self, mass_flow: float, rho: float, mu: float) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula la caída de presión en Pascales (Pa).
        Valores positivos indican caída de presión en la dirección from_node -> to_node.
        mass_flow, rho, mu deben estar en unidades base SI.
        """
        # Calcular velocidad
        area = self.geometry.area.to_base_units().magnitude
        D = self.geometry.D.to_base_units().magnitude
        L = self.geometry.L.to_base_units().magnitude
        dz = self.geometry.dz.to_base_units().magnitude
        
        # v y m_flow tienen el mismo signo. 
        # v = m_flow / (rho * area)
        velocity = mass_flow / (rho * area)
        abs_vel = abs(velocity)
        
        if abs_vel < 1e-9:
            # Flujo cero, solo carga estática
            dp_stat = rho * 9.80665 * dz
            info = {
                "velocity": 0.0,
                "reynolds": 0.0,
                "friction_factor": 0.0,
                "dp_friction": 0.0,
                "dp_static": dp_stat,
                "dp_total": dp_stat,
                "regime": "zero_flow"
            }
            return dp_stat, info
            
        re = reynolds_number(abs_vel, D, rho, mu)
        rel_rough = self.geometry.relative_roughness
        
        f, solver_info = colebrook_white_friction_factor(re, rel_rough)
        
        # La pérdida por fricción siempre se opone al flujo.
        # Si v > 0, dp_f > 0. Si v < 0, dp_f < 0.
        dp_f_mag = darcy_weisbach_dp(f, L, D, rho, abs_vel)
        dp_f = math.copysign(dp_f_mag, velocity)
        
        # Carga estática: positiva si sube (dz > 0)
        dp_stat = rho * 9.80665 * dz
        
        dp_total = dp_f + dp_stat
        
        info = {
            "velocity": velocity,
            "reynolds": re,
            "relative_roughness": rel_rough,
            "friction_factor": f,
            "dp_friction": dp_f,
            "dp_static": dp_stat,
            "dp_total": dp_total,
            "regime": "laminar" if re < 2300 else ("transitional" if re < 4000 else "turbulent"),
            "solver_info": solver_info
        }
        
        return dp_total, info
