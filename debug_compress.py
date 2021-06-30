from piping_engine.core.units import Q_
from piping_engine.core.geometry import PipeGeometry
from piping_engine.components.compressible_pipe import CompressiblePipe

geom = PipeGeometry(internal_diameter=Q_("100 mm"), roughness=Q_("0.05 mm"), length=Q_("100 m"))
pipe = CompressiblePipe("T1", "IN", "OUT", geom, P_ref=101325.0)

for m in [0.1, 0.5, 1.0, 5.0]:
    dp, info = pipe.pressure_drop(m, 1.204, 1.8e-5, 600000.0)
    print(f"m={m}, dp={dp}, choked={info.get('choked')}")
