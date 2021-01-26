from piping_engine.core.units import Q_
from piping_engine.fluids.properties import ConstantFluid
from piping_engine.core.geometry import PipeGeometry
from piping_engine.components.pipe import Pipe
from piping_engine.network.graph import HydraulicNetwork
from piping_engine.network.solver import solve_network
import math

def main():
    print("VERIFICACIÓN: TUBERÍAS EN PARALELO")
    # Dos tuberías idénticas en paralelo deberían dividir el flujo exactamente a la mitad.
    water = ConstantFluid("Agua", rho=Q_(1000.0, "kg/m**3"), mu=Q_(1e-3, "Pa*s"))
    net = HydraulicNetwork()
    net.set_fluid(water, T=Q_(20, "degC"), P_ref=Q_(1, "atm"))
    
    net.add_node("IN", fixed_pressure=200000.0) # 2 bar
    net.add_node("OUT", fixed_pressure=100000.0) # 1 bar
    
    geom = PipeGeometry(
        internal_diameter=Q_(50, "mm"),
        roughness=Q_(0.05, "mm"),
        length=Q_(100, "m")
    )
    
    p1 = Pipe("Branch_A", "IN", "OUT", geom)
    p2 = Pipe("Branch_B", "IN", "OUT", geom)
    
    net.add_component(p1)
    net.add_component(p2)
    
    res = solve_network(net)
    
    m_a = res["branch_flows"]["Branch_A"]
    m_b = res["branch_flows"]["Branch_B"]
    
    print(f"Flujo en A: {m_a:.3f} kg/s")
    print(f"Flujo en B: {m_b:.3f} kg/s")
    
    assert math.isclose(m_a, m_b, rel_tol=1e-5), "Los flujos no son iguales"
    print("VERIFICACIÓN EXITOSA: Los flujos se dividen equitativamente.")

if __name__ == "__main__":
    main()
