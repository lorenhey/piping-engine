import math
from typing import Dict, Any, Tuple
from piping_engine.components.base import Component
from piping_engine.core.geometry import PipeGeometry
from piping_engine.correlations.friction import reynolds_number, colebrook_white_friction_factor

class CompressiblePipe(Component):
    """
    Tubería con flujo de gas isotérmico.
    Calcula la expansión del gas y el cambio de densidad a lo largo de la tubería.
    """
    
    def __init__(self, name: str, from_node: str, to_node: str, geometry: PipeGeometry, P_ref: float = 101325.0):
        super().__init__(name, from_node, to_node)
        self.geometry = geometry
        self.P_ref = P_ref  # Presión de referencia para rho_ref

    def pressure_drop(self, mass_flow: float, rho_ref: float, mu_ref: float, p_from: float = 101325.0) -> Tuple[float, Dict[str, Any]]:
        # rho_ref es la densidad a self.P_ref.
        # Asumiendo gas ideal, rho(P) = rho_ref * (P / P_ref)
        
        area = self.geometry.area.to_base_units().magnitude
        D = self.geometry.D.to_base_units().magnitude
        L = self.geometry.L.to_base_units().magnitude
        
        # Proteger p_from negativo durante la optimización
        if p_from < 100.0:
            p_from_eval = 100.0
        else:
            p_from_eval = p_from
            
        rho_in = rho_ref * (p_from_eval / self.P_ref)
        velocity_in = mass_flow / (rho_in * area)
        abs_vel_in = abs(velocity_in)
        
        if abs_vel_in < 1e-9:
            return 0.0, {"regime": "zero_flow", "dp_total": 0.0}
            
        re = reynolds_number(abs_vel_in, D, rho_in, mu_ref)
        rel_rough = self.geometry.relative_roughness
        f, solver_info = colebrook_white_friction_factor(re, rel_rough)
        
        G = mass_flow / area
        pressure_term = f * (L / D) * (self.P_ref / rho_ref) * G**2
        
        if p_from_eval**2 <= pressure_term:
            # Extrapolación suave para el jacobiano en lugar de penalidad abrupta
            p_to = 100.0
            dp_fric = p_from_eval - p_to + (pressure_term - p_from_eval**2) / p_from_eval
            choked = True
        else:
            p_to = math.sqrt(p_from_eval**2 - pressure_term)
            dp_fric = p_from_eval - p_to
            choked = False
            
        dp = math.copysign(dp_fric, mass_flow)
        
        info = {
            "velocity_in": velocity_in,
            "reynolds": re,
            "friction_factor": f,
            "dp_total": dp,
            "choked": choked,
            "regime": "compressible",
            "solver_info": solver_info
        }
        
        return dp, info
