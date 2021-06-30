import numpy as np
import scipy.optimize
from typing import Dict, Any, Tuple
from piping_engine.network.graph import HydraulicNetwork
from piping_engine.core.exceptions import ConvergenceError, InvalidSystemError

def solve_network(network: HydraulicNetwork, tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Resuelve la red hidráulica.
    Asume propiedades constantes a lo largo de toda la red evaluadas a (fluid_T, fluid_P_ref)
    por simplicidad en la versión 1, para fluidos incompresibles.
    """
    if not network.fluid:
        raise InvalidSystemError("Fluido no configurado en la red.")

    # Evaluar densidad y viscosidad de referencia
    rho_val = network.fluid.density(network.fluid_T, network.fluid_P_ref).to("kg/m**3").magnitude
    mu_val = network.fluid.dynamic_viscosity(network.fluid_T, network.fluid_P_ref).to("Pa*s").magnitude

    unknown_nodes = []
    fixed_nodes = []
    for name, node in network.nodes.items():
        if node.fixed_pressure is not None:
            fixed_nodes.append(name)
        else:
            unknown_nodes.append(name)

    N_un = len(unknown_nodes)
    N_b = len(network.components)

    if N_un == len(network.nodes):
        raise InvalidSystemError("El sistema no tiene nodos con presión fijada. Está subdeterminado.")

    node_idx = {name: i for i, name in enumerate(unknown_nodes)}
    comp_idx = {comp.name: i for i, comp in enumerate(network.components)}

    # Guess inicial: 
    # Presiones desconocidas = promedio de las conocidas (o 1 atm si no hay)
    fixed_pressures = [network.nodes[n].fixed_pressure for n in fixed_nodes]
    if fixed_pressures:
        p_guess_val = sum(fixed_pressures) / len(fixed_pressures)
    else:
        p_guess_val = 101325.0
    
    x0 = np.zeros(N_un + N_b)
    x0[:N_un] = p_guess_val
    # Flujos iniciales: 0.1 kg/s (para evitar singularidades en f'(v))
    x0[N_un:] = 0.1

    def residuals(x):
        res = np.zeros_like(x)
        
        P_un = x[:N_un]
        m_flows = x[N_un:]

        # Ecuaciones de nodos (balance de masa)
        # res[:N_un] -> suma de flujos que salen - suma de flujos que entran + demanda = 0
        for i, name in enumerate(unknown_nodes):
            res[i] = network.nodes[name].flow_demand

        # Ecuaciones de componentes (balance de energía)
        for i, comp in enumerate(network.components):
            m = m_flows[i]
            
            # Presiones
            if comp.from_node in node_idx:
                p_from = P_un[node_idx[comp.from_node]]
            else:
                p_from = network.nodes[comp.from_node].fixed_pressure
                
            if comp.to_node in node_idx:
                p_to = P_un[node_idx[comp.to_node]]
            else:
                p_to = network.nodes[comp.to_node].fixed_pressure
                
            # p_from - p_to = dp(m)
            dp, _ = comp.pressure_drop(m, rho_val, mu_val, p_from=p_from)
            res[N_un + i] = ((p_from - p_to) - dp) / 100000.0
            
            # Sumar al balance de masa de los nodos
            if comp.from_node in node_idx:
                res[node_idx[comp.from_node]] += m
            if comp.to_node in node_idx:
                res[node_idx[comp.to_node]] -= m

        return res

    # Resolver usando el método de Powell híbrido o similar
    sol = scipy.optimize.root(residuals, x0, method='hybr', tol=tolerance)

    if not sol.success:
        raise ConvergenceError(f"El solver no convergió: {sol.message}")

    # Extraer resultados
    P_final = sol.x[:N_un]
    m_final = sol.x[N_un:]

    # Asignar resultados a la red
    for i, name in enumerate(unknown_nodes):
        network.nodes[name].pressure_result = P_final[i]
    for name in fixed_nodes:
        network.nodes[name].pressure_result = network.nodes[name].fixed_pressure

    results = {
        "converged": sol.success,
        "iterations": sol.nfev,
        "max_residual": np.max(np.abs(sol.fun)),
        "node_pressures": {name: network.nodes[name].pressure_result for name in network.nodes},
        "branch_flows": {comp.name: m_final[i] for i, comp in enumerate(network.components)},
        "branch_details": {}
    }

    # Calcular info detallada de componentes
    for i, comp in enumerate(network.components):
        if comp.from_node in node_idx:
            p_from_final = P_final[node_idx[comp.from_node]]
        else:
            p_from_final = network.nodes[comp.from_node].fixed_pressure
            
        _, info = comp.pressure_drop(m_final[i], rho_val, mu_val, p_from=p_from_final)
        results["branch_details"][comp.name] = info

    return results
