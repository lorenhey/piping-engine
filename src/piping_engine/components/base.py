from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from piping_engine.core.units import ureg, Q_

class Component(ABC):
    """Clase base para todos los componentes de la red."""
    
    def __init__(self, name: str, from_node: str, to_node: str):
        self.name = name
        self.from_node = from_node
        self.to_node = to_node

    @abstractmethod
    def pressure_drop(self, mass_flow: float, rho: float, mu: float) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula la caída de presión (Pa) a partir del flujo másico (kg/s), 
        densidad (kg/m3) y viscosidad (Pa.s).
        Retorna (delta_p, info_detallada)
        """
        pass
