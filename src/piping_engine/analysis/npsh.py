import math
from piping_engine.network.graph import HydraulicNetwork
from piping_engine.core.units import Q_

def calculate_npsh_available(network: HydraulicNetwork, pump_name: str) -> float:
    """
    Calcula el NPSH disponible para una bomba.
    Asume que la red ha sido resuelta previamente.
    
    NPSH_a = (P_abs / (rho * g)) + z_inlet - P_vapor / (rho * g) + v^2 / 2g
    (Simplificado: utilizamos la presión estática resuelta en el nodo de entrada a la bomba)
    """
    
    # Buscar la bomba
    pump = next((c for c in network.components if c.name == pump_name), None)
    if not pump:
        raise ValueError(f"No se encontró la bomba {pump_name}")
        
    inlet_node = network.nodes[pump.from_node]
    p_abs = inlet_node.pressure_result  # Pa
    
    rho = network.fluid.density(network.fluid_T, network.fluid_P_ref).to("kg/m**3").magnitude
    p_vap = network.fluid.vapor_pressure(network.fluid_T).to("Pa").magnitude
    
    # El término cinético v^2/2g puede calcularse si la tubería entrante se asume del mismo diámetro.
    # Por seguridad y conservación, el NPSH se calcula asumiendo que P_abs es presión total o 
    # ignorando la velocidad (en cuyo caso es conservador).
    # Tomamos P_abs como presión estática:
    
    npsh_a = (p_abs - p_vap) / (rho * 9.80665)
    
    return npsh_a
