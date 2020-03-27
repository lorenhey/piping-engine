class PipingEngineError(Exception):
    """Clase base para excepciones del motor de tuberías."""
    pass

class UnitError(PipingEngineError):
    """Error relacionado con las unidades o conversiones."""
    pass

class FluidPropertyError(PipingEngineError):
    """Error al obtener propiedades termofísicas del fluido."""
    pass

class ConvergenceError(PipingEngineError):
    """Error cuando el solver de la red no converge."""
    pass

class InvalidSystemError(PipingEngineError):
    """Error cuando la red está mal definida (ej. componentes desconectados)."""
    pass

class PhysicsWarning(UserWarning):
    """Advertencia sobre suposiciones físicas (ej. flujo transicional)."""
    pass
