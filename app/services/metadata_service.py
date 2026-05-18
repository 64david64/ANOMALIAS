from .data_loader import load_metadata, get_available_variables


def get_layer_catalog():
    """
    Catálogo base de capas para el visor.

    Mantiene nombres, unidades y advertencias consistentes entre plantillas,
    rutas API y textos metodológicos.
    """
    return [
        {
            "id": "aire_libre_mgal",
            "name": "Anomalía de aire libre",
            "unit": "mGal",
            "type": "grid",
            "description": (
                "Anomalía gravimétrica derivada considerando el efecto de la altura. "
                "Se emplea para observar variaciones regionales del campo gravitatorio."
            ),
            "visible": True,
        },
        {
            "id": "bouguer_mgal",
            "name": "Anomalía de Bouguer",
            "unit": "mGal",
            "type": "grid",
            "description": (
                "Anomalía gravimétrica corregida considerando el efecto de la masa topográfica. "
                "Se usa para resaltar contrastes regionales de densidad cortical."
            ),
            "visible": True,
        },
        {
            "id": "gradiente_mgal_km",
            "name": "Gradiente horizontal de Bouguer",
            "unit": "mGal/km",
            "type": "grid",
            "description": (
                "Cambio espacial de la anomalía de Bouguer. Las zonas de alto gradiente "
                "se interpretan como posibles lineamientos gravimétricos o áreas de interés estructural."
            ),
            "visible": False,
        },
        {
            "id": "altura_m",
            "name": "Altura / topografía",
            "unit": "m",
            "type": "grid",
            "description": (
                "Variable altimétrica usada para comparar relieve y comportamiento gravimétrico."
            ),
            "visible": False,
        },
        {
            "id": "gnss",
            "name": "Estaciones GNSS retenidas",
            "unit": "mm/año",
            "type": "points",
            "description": (
                "Estaciones GNSS usadas para representar velocidades medias derivadas "
                "de desplazamientos acumulados durante la serie temporal."
            ),
            "visible": True,
        },
        {
            "id": "puntos_gravimetricos",
            "name": "Puntos gravimétricos clasificados",
            "unit": "",
            "type": "points",
            "description": (
                "Puntos gravimétricos considerados para análisis contextual por proximidad espacial. "
                "No se interpretan como pertenecientes directamente a una estación GNSS."
            ),
            "visible": False,
        },
    ]


def get_variable_description(variable_name):
    metadata = load_metadata()

    if isinstance(metadata, dict):
        if "variables" in metadata and variable_name in metadata["variables"]:
            return metadata["variables"][variable_name]

        if variable_name in metadata and isinstance(metadata[variable_name], dict):
            return metadata[variable_name]

    for layer in get_layer_catalog():
        if layer["id"] == variable_name:
            return layer

    return {
        "id": variable_name,
        "name": variable_name.replace("_", " ").title(),
        "unit": "",
        "description": "Variable disponible en los datos procesados.",
    }


def get_project_metadata():
    return {
        "title": "Visor sismotectónico integrado de Colombia",
        "short_title": "SismoTectoLab",
        "description": (
            "Aplicación web para visualizar e interpretar de forma pedagógica anomalías "
            "gravimétricas, gradiente horizontal de Bouguer y velocidades GNSS en un "
            "contexto sismotectónico regional."
        ),
        "reference_frame": "IGS20 / ITRF2020",
        "gnss_note": (
            "Las velocidades GNSS se estiman a partir de desplazamientos acumulados "
            "durante la serie temporal."
        ),
        "gravity_gnss_relation": (
            "La relación entre puntos gravimétricos y estaciones GNSS se interpreta "
            "únicamente de forma contextual por proximidad espacial."
        ),
    }


def get_available_layers():
    return get_layer_catalog()


def get_metadata():
    return load_metadata()


def get_variables_catalog():
    return get_available_variables()