from .data_loader import load_metadata, get_available_variables


def get_layer_catalog():
    return [
        {
            "id": "aire_libre_mgal",
            "name": "Anomalía de aire libre",
            "unit": "mGal",
            "type": "grid",
            "description": (
                "Anomalía gravimétrica corregida por el efecto de la altura. "
                "Permite observar variaciones regionales del campo gravitatorio."
            ),
            "visible": True
        },
        {
            "id": "bouguer_mgal",
            "name": "Anomalía de Bouguer",
            "unit": "mGal",
            "type": "grid",
            "description": (
                "Anomalía gravimétrica corregida considerando el efecto de la "
                "masa topográfica. Se emplea para resaltar contrastes regionales "
                "de densidad cortical."
            ),
            "visible": True
        },
        {
            "id": "gradiente_mgal_km",
            "name": "Gradiente horizontal de Bouguer",
            "unit": "mGal/km",
            "type": "grid",
            "description": (
                "Cambio espacial de la anomalía de Bouguer. Las zonas de alto "
                "gradiente se interpretan como posibles lineamientos o bordes "
                "corticales potenciales."
            ),
            "visible": False
        },
        {
            "id": "altura_m",
            "name": "Topografía / altura",
            "unit": "m",
            "type": "grid",
            "description": (
                "Altura asociada a los datos procesados. Se usa para comparar "
                "relieve y comportamiento gravimétrico."
            ),
            "visible": False
        },
        {
            "id": "gnss",
            "name": "Estaciones GNSS retenidas",
            "unit": "mm/año",
            "type": "points",
            "description": (
                "Estaciones GNSS usadas para representar velocidades medias "
                "estimadas a partir de desplazamientos acumulados durante la "
                "serie temporal. Los vectores se interpretan en IGS20 / ITRF2020."
            ),
            "visible": True
        },
        {
            "id": "puntos_gravimetricos",
            "name": "Puntos gravimétricos clasificados",
            "unit": "",
            "type": "points",
            "description": (
                "Puntos gravimétricos usados para lectura contextual por "
                "proximidad espacial. No se interpretan como pertenecientes "
                "directamente a una estación GNSS."
            ),
            "visible": False
        }
    ]


def get_figure_catalog():
    """
    Catálogo oficial de figuras generadas desde MATLAB.

    Cada entrada debe coincidir con el nombre real del archivo ubicado en:
    data/processed/salidas_sismotectonicas/figuras/
    """

    return [
        {
            "code": "F01",
            "filename": "01_anomalia_aire_libre_vectores_gnss.png",
            "title": "Anomalía de aire libre y vectores GNSS",
            "variable": "Aire libre + GNSS",
            "description": (
                "Representa la anomalía de aire libre en el área de estudio e "
                "integra los vectores GNSS retenidos para visualizar la relación "
                "regional entre variaciones gravimétricas y desplazamiento geodésico."
            ),
            "interpretation": (
                "Permite observar la respuesta del campo gravimétrico antes de "
                "la corrección de Bouguer y contrastarla con la dirección relativa "
                "de movimiento de las estaciones GNSS."
            ),
            "caution": (
                "La superposición con GNSS es contextual. No implica causalidad "
                "directa entre una anomalía local y una estación específica."
            )
        },
        {
            "code": "F02",
            "filename": "02_anomalia_bouguer_lineamientos_gnss.png",
            "title": "Anomalía de Bouguer, lineamientos potenciales y GNSS",
            "variable": "Bouguer + lineamientos",
            "description": (
                "Muestra la anomalía de Bouguer como superficie principal de "
                "interpretación gravimétrica, junto con lineamientos potenciales "
                "derivados de cambios espaciales relevantes."
            ),
            "interpretation": (
                "Las zonas de contraste en Bouguer pueden relacionarse con cambios "
                "laterales de densidad cortical o bordes estructurales regionales."
            ),
            "caution": (
                "Los lineamientos son potenciales. No deben presentarse como fallas "
                "activas confirmadas sin validación geológica adicional."
            )
        },
        {
            "code": "F03",
            "filename": "03_gradiente_horizontal_bouguer_gnss.png",
            "title": "Gradiente horizontal de anomalía de Bouguer",
            "variable": "Gradiente Bouguer",
            "description": (
                "Presenta el gradiente horizontal de la anomalía de Bouguer, usado "
                "para resaltar zonas donde el campo gravimétrico cambia rápidamente."
            ),
            "interpretation": (
                "Los máximos de gradiente son útiles para reconocer posibles "
                "bordes de bloques corticales, contactos laterales o lineamientos "
                "estructurales potenciales."
            ),
            "caution": (
                "El gradiente resalta cambios espaciales, pero no identifica por sí "
                "solo la naturaleza geológica exacta de la estructura."
            )
        },
        {
            "code": "F04",
            "filename": "04_perfiles_we_bouguer_topografia.png",
            "title": "Perfiles W-E de Bouguer y topografía",
            "variable": "Perfiles espaciales",
            "description": (
                "Compara perfiles oeste-este de anomalía de Bouguer y topografía "
                "en latitudes de referencia asociadas a ciudades o franjas regionales."
            ),
            "interpretation": (
                "Ayuda a observar si las variaciones gravimétricas acompañan o no "
                "los cambios topográficos, permitiendo diferenciar patrones de relieve "
                "y posibles contrastes corticales."
            ),
            "caution": (
                "Los perfiles representan cortes específicos; no deben generalizarse "
                "sin revisar el patrón espacial completo."
            )
        },
        {
            "code": "F05",
            "filename": "05_velocidades_gnss_estaciones_retenidas.png",
            "title": "Velocidades GNSS de estaciones retenidas",
            "variable": "GNSS",
            "description": (
                "Resume las velocidades medias estimadas para las estaciones GNSS "
                "retenidas, calculadas a partir de desplazamientos acumulados durante "
                "su serie temporal."
            ),
            "interpretation": (
                "Permite comparar componentes Este, Norte y vertical, así como "
                "evaluar diferencias relativas entre estaciones dentro del marco "
                "IGS20 / ITRF2020."
            ),
            "caution": (
                "Las velocidades se interpretan como tasas medias y no como una "
                "descripción completa de la serie temporal."
            )
        },
        {
            "code": "F06",
            "filename": "06_mapa_integrado_sismotectonico.png",
            "title": "Mapa integrado sismotectónico",
            "variable": "Integración",
            "description": (
                "Integra anomalía de Bouguer, lineamientos potenciales y vectores "
                "GNSS retenidos en una sola representación espacial."
            ),
            "interpretation": (
                "Funciona como síntesis visual para reconocer zonas donde coinciden "
                "contrastes gravimétricos y diferencias relativas de movimiento GNSS."
            ),
            "caution": (
                "El mapa sintetiza evidencias complementarias, pero no constituye "
                "por sí solo una delimitación oficial de estructuras tectónicas activas."
            )
        },
        {
            "code": "F07",
            "filename": "07_correlacion_bouguer_topografia.png",
            "title": "Correlación entre Bouguer y topografía",
            "variable": "Relación estadística",
            "description": (
                "Explora la relación entre la anomalía de Bouguer y la altura, "
                "permitiendo evaluar la dependencia entre respuesta gravimétrica "
                "y relieve."
            ),
            "interpretation": (
                "Sirve para revisar si los patrones gravimétricos están dominados "
                "por la topografía o si reflejan variaciones adicionales asociadas "
                "a contrastes de densidad."
            ),
            "caution": (
                "La correlación no implica causalidad directa; debe leerse junto "
                "con mapas, perfiles y contexto geofísico."
            )
        }
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
        "description": "Variable disponible en los datos procesados."
    }


def get_project_metadata():
    return {
        "title": "Visor sismotectónico integrado de Colombia",
        "short_title": "SismoTectoLab",
        "description": (
            "Aplicación web para visualizar e interpretar anomalías gravimétricas, "
            "gradiente horizontal de Bouguer y velocidades GNSS en un contexto "
            "sismotectónico regional."
        ),
        "reference_frame": "IGS20 / ITRF2020",
        "gravity_gnss_relation": (
            "La relación entre puntos gravimétricos y estaciones GNSS se interpreta "
            "únicamente de forma contextual por proximidad espacial."
        )
    }


def get_available_layers():
    return get_layer_catalog()


def get_metadata():
    return load_metadata()


def get_variables_catalog():
    return get_available_variables()