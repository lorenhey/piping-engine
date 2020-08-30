import datetime
from jinja2 import Template
from piping_engine.network.graph import HydraulicNetwork
from typing import Dict, Any

def generate_report(network: HydraulicNetwork, results: Dict[str, Any], output_path: str):
    """Genera un reporte HTML con los resultados del cálculo."""
    
    template_str = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Memoria de Cálculo Hidráulico</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; margin: 40px; }
            h1 { color: #004080; border-bottom: 2px solid #004080; padding-bottom: 10px; }
            h2 { color: #0059b3; margin-top: 30px; }
            table { border-collapse: collapse; width: 100%; margin-top: 15px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #f2f2f2; color: #333; font-weight: bold; }
            .success { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
            .info-box { background-color: #e6f2ff; border-left: 4px solid #004080; padding: 15px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Memoria de Cálculo Hidráulico - piping-engine</h1>
        
        <div class="info-box">
            <p><strong>Fecha de cálculo:</strong> {{ timestamp }}</p>
            <p><strong>Fluido:</strong> {{ fluid_name }} @ {{ fluid_T }} / {{ fluid_P }}</p>
            <p><strong>Convergencia:</strong> <span class="{% if converged %}success{% else %}error{% endif %}">{{ 'Exitosa' if converged else 'Fallida' }}</span> ({{ iterations }} iteraciones)</p>
        </div>

        <h2>Resultados por Nodo</h2>
        <table>
            <tr>
                <th>Nodo</th>
                <th>Elevación (m)</th>
                <th>Presión Absoluta (bar)</th>
            </tr>
            {% for name, node in nodes.items() %}
            <tr>
                <td>{{ name }}</td>
                <td>{{ "%.2f"|format(node.elevation) }}</td>
                <td>{{ "%.4f"|format(node.pressure_result / 100000.0) }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>Resultados por Componente</h2>
        <table>
            <tr>
                <th>Componente</th>
                <th>Flujo Másico (kg/s)</th>
                <th>Pérdida de Presión (bar)</th>
                <th>Detalles Adicionales</th>
            </tr>
            {% for comp in components %}
            <tr>
                <td>{{ comp.name }}</td>
                <td>{{ "%.3f"|format(branch_flows[comp.name]) }}</td>
                <td>{{ "%.4f"|format(branch_details[comp.name].get('dp_total', 0) / 100000.0) }}</td>
                <td>
                    {% if branch_details[comp.name].get('velocity') is not none %}
                    V = {{ "%.2f"|format(branch_details[comp.name].get('velocity', 0)) }} m/s<br>
                    {% endif %}
                    {% if branch_details[comp.name].get('regime') %}
                    Régimen: {{ branch_details[comp.name].get('regime') }}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        
        <br><br>
        <hr>
        <p><small>Generado automáticamente por piping-engine. Este software no reemplaza el criterio profesional de un ingeniero matriculado.</small></p>
    </body>
    </html>
    """
    
    template = Template(template_str)
    
    html = template.render(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        fluid_name=network.fluid.name if network.fluid else "Desconocido",
        fluid_T=str(network.fluid_T) if network.fluid_T is not None else "N/A",
        fluid_P=str(network.fluid_P_ref) if network.fluid_P_ref is not None else "N/A",
        converged=results['converged'],
        iterations=results['iterations'],
        nodes=network.nodes,
        components=network.components,
        branch_flows=results['branch_flows'],
        branch_details=results['branch_details']
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
