# piping-engine

`piping-engine` resuelve de forma determinista redes hidráulicas en estado estacionario para sistemas de tuberías. Está diseñado por y para ingenieros, priorizando la transparencia y la trazabilidad técnica por sobre las "cajas negras".

## Características Principales

*   **Trazabilidad:** Cada cálculo puede ser "explicado", mostrando ecuaciones, suposiciones, propiedades y resultados intermedios.
*   **Gestión Rigurosa de Unidades:** Permite la especificación transparente de unidades (ej. `m3/h`, `bar`, `kPa`).
*   **Redes Hidráulicas:** Solucionador basado en grafos que admite sistemas en serie, ramificados y mallados (con bombas y múltiples nodos de demanda).
*   **Propiedades de Fluidos:** Permite propiedades fluidas simples y enlace con bases de datos avanzadas (ej. CoolProp) teniendo en cuenta estado (T, P).
*   **Reportes Técnicos:** Generación de memoria de cálculo profesional y trazable.
*   **Interfaces:** API en Python, herramienta de línea de comandos (CLI) y un entorno visual local.

## Instalación

```bash
# Entorno virtual
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# Instalación modo desarrollo
pip install -e .[dev,gui]
```

## Uso Rápido (CLI)

```bash
piping-engine --help
piping-engine solve proyecto.yaml
piping-engine explain pipe P-101
```

## Arquitectura

*   **core**: Unidades, topología, bases.
*   **fluids**: Propiedades físicas de los fluidos.
*   **correlations**: Fricción, válvulas, pérdidas localizadas.
*   **components**: Tuberías, bombas, fronteras de presión, válvulas.
*   **network**: Motor de resolución numérica de la red (masas y energía).
*   **reporting**: Generador de reportes.
*   **ui**: Entorno de usuario local.

## Advertencia Profesional

Este proyecto de software es de carácter ingenieril. Se debe aplicar el buen juicio profesional. Ningún software reemplaza los requerimientos jurisdiccionales, la firma de un ingeniero matriculado (cuando corresponda), la información del fabricante, la inspección en campo o la puesta en marcha real del sistema.
