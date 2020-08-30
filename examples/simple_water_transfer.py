from piping_engine.core.units import Q_
from piping_engine.fluids.properties import ConstantFluid
from piping_engine.core.geometry import PipeGeometry
from piping_engine.components.pipe import Pipe
from piping_engine.network.graph import HydraulicNetwork
from piping_engine.network.solver import solve_network

def main():
    # 1. Definir fluido (Agua a 20°C aprox)
    water = ConstantFluid("Agua", rho=Q_(998.2, "kg/m**3"), mu=Q_(1.002e-3, "Pa*s"))
    
    # 2. Configurar la red
    net = HydraulicNetwork()
    net.set_fluid(water, T=Q_(20, "degC"), P_ref=Q_(1, "atm"))
    
    # Nodos
    net.add_node("T1", elevation=10.0, fixed_pressure=101325.0)  # Tanque elevado a 10m
    net.add_node("T2", elevation=0.0, fixed_pressure=101325.0)   # Tanque a nivel suelo
    
    # Tubería
    geom = PipeGeometry(
        internal_diameter=Q_(52.5, "mm"),
        roughness=Q_(0.045, "mm"),
        length=Q_(100, "m"),
        elevation_change=Q_(-10.0, "m")  # baja 10 metros
    )
    
    p1 = Pipe("P-101", from_node="T1", to_node="T2", geometry=geom)
    net.add_component(p1)
    
    # 3. Resolver
    results = solve_network(net)
    
    print("=== RESULTADOS ===")
    print(f"Convergió: {results['converged']} en {results['iterations']} iteraciones.")
    m_flow = results['branch_flows']["P-101"]
    v_flow_m3_h = (m_flow / 998.2) * 3600
    
    print(f"Flujo másico: {m_flow:.3f} kg/s")
    print(f"Flujo volumétrico: {v_flow_m3_h:.2f} m3/h")
    
    details = results['branch_details']["P-101"]
    print(f"Velocidad: {details['velocity']:.3f} m/s")
    print(f"Reynolds: {details['reynolds']:.0f}")
    print(f"Régimen: {details['regime']}")
    print(f"Factor fricción f: {details['friction_factor']:.5f}")
    print(f"Caída de presión fricción: {details['dp_friction']:.0f} Pa")
    print(f"Carga estática: {details['dp_static']:.0f} Pa")
    print(f"Caída de presión total: {details['dp_total']:.0f} Pa")

if __name__ == "__main__":
    main()
