import math
import pint
from piping_engine.core.units import Q_, ensure_quantity

class PipeGeometry:
    """Clase para manejar la geometría interna de una tubería."""
    
    def __init__(self, internal_diameter: pint.Quantity, roughness: pint.Quantity, length: pint.Quantity, elevation_change: pint.Quantity = Q_(0, "m")):
        self.D = ensure_quantity(internal_diameter, "m")
        self.epsilon = ensure_quantity(roughness, "m")
        self.L = ensure_quantity(length, "m")
        self.dz = ensure_quantity(elevation_change, "m")  # z_out - z_in

    @property
    def area(self) -> pint.Quantity:
        return math.pi * (self.D ** 2) / 4.0

    @property
    def relative_roughness(self) -> float:
        """Rugosidad relativa epsilon / D."""
        return (self.epsilon / self.D).to_base_units().magnitude
