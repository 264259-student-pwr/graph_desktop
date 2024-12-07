def get_country_crs():
    """Zwraca CRS dla Polski."""
    return "EPSG:2180"

def get_default_zoom():
    """Zwraca domyślną wartość zoom dla Polski."""
    return 8

def country_specific_settings():
    """Zwraca specyficzne ustawienia dla Polski."""
    return {
        "crs": get_country_crs(),
        "zoom": get_default_zoom(),
        "description": "Polska - Województwa"
    }
