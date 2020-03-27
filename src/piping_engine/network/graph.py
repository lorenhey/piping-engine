from typing import Dict, List, Optional
from piping_engine.components.base import Component
from piping_engine.core.units import ensure_quantity, Q_

class Node:
    """Nodo de la red hidráulica."""
    def __init__(self, name: str, elevation: float = 0.0, 
                 fixed_pressure: Optional[float] = None, 
                 flow_demand: float = 0.0):
        self.name = name
        self.elevation = elevation  # m
        self.fixed_pressure = fixed_pressure  # Pa (absoluta o manométrica, pero consistente)
        self.flow_demand = flow_demand  # kg/s, positivo si sale de la red, negativo si entra.
        self.pressure_result: Optional[float] = None

class HydraulicNetwork:
    """Representa una red hidráulica completa."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.components: List[Component] = []
        self.fluid = None
        self.fluid_T = None
        self.fluid_P_ref = None

    def set_fluid(self, fluid, T, P_ref):
        """Establece el fluido y sus condiciones de referencia para la red."""
        self.fluid = fluid
        self.fluid_T = T
        self.fluid_P_ref = P_ref

    def add_node(self, name: str, elevation: float = 0.0, 
                 fixed_pressure: Optional[float] = None, 
                 flow_demand: float = 0.0):
        if name in self.nodes:
            raise ValueError(f"El nodo {name} ya existe.")
        self.nodes[name] = Node(name, elevation, fixed_pressure, flow_demand)

    def add_component(self, component: Component):
        if component.from_node not in self.nodes or component.to_node not in self.nodes:
            raise ValueError(f"Los nodos del componente {component.name} deben existir antes de agregarlo.")
        self.components.append(component)
