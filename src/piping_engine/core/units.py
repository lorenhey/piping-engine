import pint

# Inicializar el registro de unidades de pint
ureg = pint.UnitRegistry(system="mks", autoconvert_offset_to_baseunit=True)

# Definir unidades de uso común en ingeniería
# Pint ya incluye la mayoría, pero aseguramos la configuración correcta.
# Configurar pint para soportar 'bar' y temperaturas.
ureg.formatter.default_format = "~P"

# Pint usa delta_degC para diferencias de temperatura, y degC para valores absolutos
Q_ = ureg.Quantity

def to_si(quantity: pint.Quantity) -> float:
    """
    Convierte una cantidad a la unidad base del sistema SI (MKS) y devuelve el valor numérico.
    Si la entrada no es una Quantity, asume que ya está en SI y la devuelve tal cual.
    """
    if isinstance(quantity, pint.Quantity):
        return quantity.to_base_units().magnitude
    return float(quantity)

def ensure_quantity(value, default_unit: str) -> pint.Quantity:
    """
    Asegura que el valor sea una cantidad de Pint. Si es numérico, le asigna la unidad por defecto.
    """
    if isinstance(value, pint.Quantity):
        return value
    return Q_(value, default_unit)
