# Referencia Matemática y Física

Este documento describe los modelos y correlaciones utilizados en `piping-engine`. Todo cálculo puede ser inspeccionado utilizando el comando `piping-engine explain`.

## 1. Conservación de la Masa
En cualquier nodo de la red $i$, la suma de flujos másicos entrantes menos los salientes, sumados a la demanda impuesta al sistema, debe ser cero:
$$ \sum \dot{m}_{in} - \sum \dot{m}_{out} + \dot{m}_{demand} = 0 $$

## 2. Conservación de la Energía (Ecuación de Bernoulli Generalizada)
A través de cualquier rama $k$ que conecta los nodos $i$ y $j$, el balance de energía en estado estacionario (en unidades de presión, Pa) está dado por:
$$ P_i - P_j = \Delta P_{friccion} + \Delta P_{estatica} + \Delta P_{menores} - \Delta P_{bomba} $$
Donde $\Delta P > 0$ implica una pérdida de presión en la dirección del flujo.

## 3. Pérdidas por Fricción (Darcy-Weisbach)
Para tuberías rectas:
$$ \Delta P_f = f_D \frac{L}{D_{int}} \frac{\rho V^2}{2} $$
El factor de fricción de Darcy ($f_D$) se determina según el régimen de flujo ($Re = \frac{\rho V D_{int}}{\mu}$):

- **Laminar ($Re < 2300$):** $f_D = \frac{64}{Re}$
- **Turbulento ($Re \ge 4000$):** Se resuelve iterativamente la ecuación implícita de Colebrook-White:
  $$ \frac{1}{\sqrt{f_D}} = -2.0 \log_{10}\left( \frac{\epsilon}{3.7 D_{int}} + \frac{2.51}{Re \sqrt{f_D}} \right) $$
  *(Fallback o estimación inicial mediante ecuación de Haaland).*

## 4. Pérdidas Menores (Localizadas)
Válvulas y accesorios se modelan utilizando el coeficiente $K$:
$$ \Delta P_m = K \frac{\rho V^2}{2} $$
Para componentes definidos con $K_v$ o $C_v$, el $K$ se deriva asumiendo que:
$$ \Delta P \propto Q^2 $$
y utilizando las conversiones estándar (e.g. $K_v = 0.865 C_v$).

## 5. Bombas Centrífugas
Añaden presión (carga) al fluido, comportándose como una "caída de presión negativa":
$$ \Delta P_{bomba} = \rho g H(Q) $$
$H(Q)$ se obtiene evaluando la curva de la bomba suministrada.

Si la velocidad de la bomba $N$ varía respecto a la velocidad nominal $N_{ref}$, se aplican las Leyes de Afinidad:
$$ Q_{nuevo} = Q_{ref} \left(\frac{N}{N_{ref}}\right) $$
$$ H_{nuevo} = H_{ref} \left(\frac{N}{N_{ref}}\right)^2 $$
