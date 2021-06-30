import yaml
from piping_engine.network.graph import HydraulicNetwork
from piping_engine.core.units import Q_
from piping_engine.fluids.properties import ConstantFluid, CoolPropFluid
from piping_engine.core.geometry import PipeGeometry
from piping_engine.components.pipe import Pipe
from piping_engine.components.pump import Pump, PumpCurve
from piping_engine.components.valve import Valve
from piping_engine.components.control_valve import ControlValve
from piping_engine.components.compressible_pipe import CompressiblePipe

def load_network_from_yaml(filepath: str) -> HydraulicNetwork:
    """Carga una red hidráulica desde un archivo YAML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Validar versión (simplificado)
    if 'schema_version' not in data:
        pass # Podría lanzar advertencia
        
    net = HydraulicNetwork()
    
    # 1. Fluido
    f_data = data.get('fluid', {})
    name = f_data.get('name', 'Water')
    T = Q_(f_data.get('temperature', '20 degC'))
    P_ref = Q_(f_data.get('pressure', '1 atm'))
    backend = f_data.get('property_backend', 'constant')
    
    if backend.lower() == 'constant':
        rho = Q_(f_data.get('density', '1000 kg/m**3'))
        mu = Q_(f_data.get('viscosity', '1e-3 Pa*s'))
        fluid = ConstantFluid(name, rho, mu)
    elif backend.lower() == 'coolprop':
        fluid = CoolPropFluid(name)
    else:
        raise ValueError(f"Backend de fluido no soportado: {backend}")
        
    net.set_fluid(fluid, T, P_ref)
    
    # 2. Nodos
    for node_name, n_data in data.get('nodes', {}).items():
        fixed_p = n_data.get('pressure')
        if fixed_p is not None:
            fixed_p = Q_(fixed_p).to("Pa").magnitude
            
        flow_demand = n_data.get('flow_demand')
        if flow_demand is not None:
            flow_demand = Q_(flow_demand).to("kg/s").magnitude
        else:
            flow_demand = 0.0
            
        elevation = Q_(n_data.get('elevation', '0 m')).to("m").magnitude
        
        net.add_node(node_name, elevation=elevation, fixed_pressure=fixed_p, flow_demand=flow_demand)
        
    # 3. Ramas / Componentes
    for edge_name, e_data in data.get('edges', {}).items():
        ctype = e_data.get('type')
        from_node = e_data.get('from')
        to_node = e_data.get('to')
        
        if ctype == 'pipe':
            geom = PipeGeometry(
                internal_diameter=Q_(e_data.get('internal_diameter')),
                roughness=Q_(e_data.get('roughness', '0.045 mm')),
                length=Q_(e_data.get('length')),
                elevation_change=Q_(e_data.get('elevation_change', '0 m'))
            )
            comp = Pipe(edge_name, from_node, to_node, geom)
            
        elif ctype == 'compressible_pipe':
            geom = PipeGeometry(
                internal_diameter=Q_(e_data.get('internal_diameter')),
                roughness=Q_(e_data.get('roughness', '0.045 mm')),
                length=Q_(e_data.get('length'))
            )
            comp = CompressiblePipe(edge_name, from_node, to_node, geom)
            
        elif ctype == 'valve':
            d_str = e_data.get('internal_diameter')
            d_q = Q_(d_str) if d_str else None
            comp = Valve(
                edge_name, from_node, to_node,
                K=e_data.get('K'),
                Kv=e_data.get('Kv'),
                Cv=e_data.get('Cv'),
                diameter=d_q
            )
            
        elif ctype == 'control_valve':
            d_str = e_data.get('internal_diameter')
            d_q = Q_(d_str) if d_str else None
            comp = ControlValve(
                edge_name, from_node, to_node,
                Kv_max=e_data.get('Kv_max'),
                diameter=d_q,
                characteristic=e_data.get('characteristic', 'linear'),
                opening_percent=e_data.get('opening_percent', 100.0)
            )
            
        elif ctype == 'pump':
            curve_data = e_data.get('curve', {})
            flows = [Q_(q) for q in curve_data.get('flows', [])]
            heads = [Q_(h) for h in curve_data.get('heads', [])]
            speed = e_data.get('speed_hz', 50.0)
            
            pcurve = PumpCurve(flows, heads, speed_hz=curve_data.get('speed_hz', 50.0))
            comp = Pump(edge_name, from_node, to_node, pcurve, speed_hz=speed)
            
        else:
            raise ValueError(f"Tipo de componente desconocido: {ctype}")
            
        net.add_component(comp)
        
    return net
