import pint
from abc import ABC, abstractmethod
from typing import Optional
from piping_engine.core.units import ureg, Q_, to_si
from piping_engine.core.exceptions import FluidPropertyError
import CoolProp.CoolProp as CP

class Fluid(ABC):
    """Interfaz base para las propiedades de un fluido."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def density(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        """Densidad del fluido a la temperatura y presión dadas."""
        pass

    @abstractmethod
    def dynamic_viscosity(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        """Viscosidad dinámica del fluido."""
        pass

    @abstractmethod
    def vapor_pressure(self, T: pint.Quantity) -> pint.Quantity:
        """Presión de vapor absoluta a la temperatura dada."""
        pass


class ConstantFluid(Fluid):
    """Fluido incompresible con propiedades constantes."""

    def __init__(self, name: str, rho: pint.Quantity, mu: pint.Quantity, pv: Optional[pint.Quantity] = None):
        super().__init__(name)
        self._rho = rho
        self._mu = mu
        self._pv = pv if pv is not None else Q_(0, "Pa")

    def density(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        return self._rho

    def dynamic_viscosity(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        return self._mu

    def vapor_pressure(self, T: pint.Quantity) -> pint.Quantity:
        return self._pv


class CoolPropFluid(Fluid):
    """
    Fluido utilizando la base de datos CoolProp.
    Las entradas de temperatura (T) y presión (P) deben ser absolutas.
    """

    def __init__(self, name: str, backend: str = "HEOS"):
        super().__init__(name)
        self.backend_name = f"{backend}::{name}"

    def density(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        T_K = T.to("K").magnitude
        P_Pa = P.to("Pa").magnitude
        try:
            rho = CP.PropsSI('D', 'T', T_K, 'P', P_Pa, self.backend_name)
            return Q_(rho, "kg/m**3")
        except ValueError as e:
            raise FluidPropertyError(f"Error en CoolProp para densidad: {e}")

    def dynamic_viscosity(self, T: pint.Quantity, P: pint.Quantity) -> pint.Quantity:
        T_K = T.to("K").magnitude
        P_Pa = P.to("Pa").magnitude
        try:
            mu = CP.PropsSI('V', 'T', T_K, 'P', P_Pa, self.backend_name)
            return Q_(mu, "Pa*s")
        except ValueError as e:
            raise FluidPropertyError(f"Error en CoolProp para viscosidad: {e}")

    def vapor_pressure(self, T: pint.Quantity) -> pint.Quantity:
        T_K = T.to("K").magnitude
        try:
            # Presión de vapor requiere calidad Q=0
            p_vap = CP.PropsSI('P', 'T', T_K, 'Q', 0, self.backend_name)
            return Q_(p_vap, "Pa")
        except ValueError as e:
            # Para gases que no tienen P_vap a esa T
            return Q_(0, "Pa")
