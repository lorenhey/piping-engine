import typer
from rich.console import Console
from rich.table import Table
from piping_engine.core.project_file import load_network_from_yaml
from piping_engine.network.solver import solve_network
from piping_engine.reporting.html_report import generate_report

app = typer.Typer(help="piping-engine: Motor de cálculo hidráulico.")
console = Console()

@app.command()
def solve(project_file: str, report: bool = typer.Option(False, "--report", help="Generar reporte HTML")):
    """Resuelve la red hidráulica definida en el archivo YAML."""
    console.print(f"[bold blue]Cargando proyecto:[/bold blue] {project_file}")
    
    try:
        net = load_network_from_yaml(project_file)
        console.print(f"[green]Proyecto cargado. Nodos: {len(net.nodes)}, Ramas: {len(net.components)}[/green]")
        
        console.print("[yellow]Resolviendo red...[/yellow]")
        results = solve_network(net)
        
        if results['converged']:
            console.print(f"[bold green]¡Convergencia exitosa en {results['iterations']} iteraciones![/bold green]")
        else:
            console.print(f"[bold red]El solver no convergió.[/bold red]")
            return

        # Mostrar resultados de nodos
        table_nodes = Table(title="Resultados - Nodos")
        table_nodes.add_column("Nodo", style="cyan")
        table_nodes.add_column("Presión (bar)", justify="right", style="magenta")
        table_nodes.add_column("Elevación (m)", justify="right")
        
        for name, node in net.nodes.items():
            p_bar = node.pressure_result / 1e5
            table_nodes.add_row(name, f"{p_bar:.4f}", f"{node.elevation:.2f}")
            
        console.print(table_nodes)
        
        # Mostrar resultados de ramas
        table_branches = Table(title="Resultados - Componentes")
        table_branches.add_column("Componente", style="cyan")
        table_branches.add_column("Flujo (kg/s)", justify="right", style="green")
        table_branches.add_column("dP (bar)", justify="right", style="red")
        
        for comp in net.components:
            m_flow = results['branch_flows'][comp.name]
            info = results['branch_details'][comp.name]
            dp_bar = info.get('dp_total', 0.0) / 1e5
            table_branches.add_row(comp.name, f"{m_flow:.3f}", f"{dp_bar:.4f}")
            
        console.print(table_branches)
        
        if report:
            generate_report(net, results, f"{project_file}_report.html")
            console.print(f"[green]Reporte generado: {project_file}_report.html[/green]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def validate(project_file: str):
    """Valida la sintaxis y conectividad del archivo YAML."""
    try:
        net = load_network_from_yaml(project_file)
        console.print("[bold green]El proyecto es válido.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Proyecto inválido:[/bold red] {str(e)}")

@app.command()
def explain(project_file: str, component_name: str):
    """Explica el cálculo de un componente en particular."""
    try:
        net = load_network_from_yaml(project_file)
        results = solve_network(net)
        if not results['converged']:
            console.print("[red]La red no convergió, los resultados pueden no ser válidos.[/red]")
            
        if component_name in results['branch_details']:
            info = results['branch_details'][component_name]
            comp = next(c for c in net.components if c.name == component_name)
            
            console.print(f"[bold cyan]=== EXPLICACIÓN: {component_name} ===[/bold cyan]")
            console.print(f"Tipo: {type(comp).__name__}")
            console.print(f"Flujo másico: {results['branch_flows'][component_name]:.3f} kg/s")
            console.print(f"Pérdida de presión total: {info.get('dp_total', 0)/100000.0:.4f} bar")
            
            if 'velocity' in info:
                console.print(f"Velocidad: {info['velocity']:.2f} m/s")
            if 'reynolds' in info:
                console.print(f"Número de Reynolds: {info['reynolds']:.0f}")
                console.print(f"Factor de fricción: {info.get('friction_factor', 0):.5f}")
            if 'regime' in info:
                console.print(f"Régimen de flujo: {info['regime']}")
            if 'solver_info' in info:
                console.print(f"Modelo de fricción: {info['solver_info'].get('method')}")
                
            console.print("[bold green]Cálculo completado según física de tuberías determinista.[/bold green]")
        else:
            console.print(f"[red]Componente '{component_name}' no encontrado.[/red]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

from piping_engine.ui.main_window import run_app

@app.command()
def gui():
    """Abre la interfaz gráfica (GUI) de piping-engine."""
    run_app()

if __name__ == "__main__":
    app()
