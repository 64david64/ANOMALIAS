def get_case_study_context():
    return {
        "title": "Caso de estudio: campo de velocidades geodésicas en Colombia",
        "description": (
            "SismoTectoLab toma como referencia conceptual un caso de estudio "
            "sobre el campo de velocidades geodésicas en Colombia. El visor no "
            "replica un producto oficial, sino que descompone el proceso y da "
            "zoom pedagógico a un conjunto retenido de estaciones GNSS, integradas "
            "con anomalías gravimétricas."
        ),
        "reference_author": "Héctor Mora Páez, MSc, PhD",
        "institution": "Dirección de Gestión de Información Geográfica · IGAC, Colombia",
        "reference_frame": "IGS20 / ITRF2020",
        "data_source": "Nevada Geodetic Laboratory",
    }


def get_interpretation_cards():
    return [
        {
            "id": "gravity",
            "kicker": "Gravedad",
            "title": "Anomalías gravimétricas",
            "text": (
                "Las anomalías de aire libre y de Bouguer permiten observar "
                "diferencias entre el campo gravitatorio real y un modelo de "
                "referencia. En el visor se interpretan como superficies regionales "
                "útiles para reconocer contrastes de densidad cortical."
            ),
            "bullets": [
                "Aire libre: corrige principalmente el efecto de la altura.",
                "Bouguer: incorpora la corrección asociada a la masa topográfica.",
                "La interpretación es regional, no puntual definitiva.",
            ],
        },
        {
            "id": "gradient",
            "kicker": "Contrastes",
            "title": "Gradiente horizontal de Bouguer",
            "text": (
                "El gradiente horizontal resalta zonas donde la anomalía de Bouguer "
                "cambia rápidamente. Estas zonas pueden sugerir bordes de bloques "
                "corticales o lineamientos gravimétricos potenciales."
            ),
            "bullets": [
                "Valores altos indican cambios espaciales fuertes.",
                "Sirve para identificar zonas de interés estructural.",
                "No equivale por sí solo a una falla activa confirmada.",
            ],
        },
        {
            "id": "gnss",
            "kicker": "Geodesia",
            "title": "Velocidades GNSS retenidas",
            "text": (
                "Las estaciones GNSS registran cambios de posición en el tiempo. "
                "En este proyecto, los desplazamientos acumulados se transforman "
                "en velocidades medias expresadas en mm/año."
            ),
            "bullets": [
                "Se trabaja con estaciones retenidas para el análisis regional.",
                "El marco de referencia usado es IGS20 / ITRF2020.",
                "Los vectores apoyan una lectura cinemática contextual.",
            ],
        },
        {
            "id": "integration",
            "kicker": "Lectura integrada",
            "title": "Relación contextual, no causal directa",
            "text": (
                "La integración entre gravedad y GNSS se realiza por superposición "
                "espacial y proximidad contextual. Un punto gravimétrico no se "
                "considera perteneciente directamente a una estación GNSS."
            ),
            "bullets": [
                "Las anomalías describen patrones regionales del campo gravimétrico.",
                "GNSS describe cambios de posición durante una serie temporal.",
                "La coincidencia espacial sugiere áreas de interés, no conclusiones definitivas.",
            ],
        },
    ]


def get_interpretation_rules():
    return [
        {
            "title": "No declarar fallas activas sin contraste",
            "text": (
                "Las zonas de alto gradiente se presentan como lineamientos "
                "potenciales o áreas de interés estructural. Para declarar fallas "
                "activas se requiere contraste con información geológica y sismológica."
            ),
        },
        {
            "title": "No asociar directamente puntos gravimétricos y estaciones GNSS",
            "text": (
                "La relación entre ambos insumos se maneja por proximidad espacial. "
                "Los puntos gravimétricos alimentan superficies regionales; las "
                "estaciones GNSS aportan información cinemática puntual."
            ),
        },
        {
            "title": "Interpretar a escala regional",
            "text": (
                "El visor está diseñado para apoyar una lectura regional y pedagógica. "
                "No reemplaza un estudio geofísico, geodésico o sismotectónico oficial."
            ),
        },
    ]


def get_interpretation_summary():
    return {
        "case_study": get_case_study_context(),
        "hero": {
            "kicker": "Lectura integrada",
            "title": "Interpretación sismotectónica",
            "subtitle": (
                "Integración contextual de anomalías gravimétricas, gradiente "
                "horizontal de Bouguer y velocidades GNSS retenidas."
            ),
            "statement": "La integración es contextual, no causal directa",
            "statement_text": (
                "Las zonas donde coinciden gradientes gravimétricos altos con "
                "cambios relativos en vectores GNSS se consideran áreas de interés "
                "estructural. No se declaran fallas activas sin contraste geológico "
                "y sismológico adicional."
            ),
        },
        "cards": get_interpretation_cards(),
        "rules": get_interpretation_rules(),
        "closing": {
            "title": "Lectura final",
            "text": (
                "SismoTectoLab permite explorar cómo las anomalías gravimétricas, "
                "el gradiente horizontal y las velocidades GNSS pueden leerse en "
                "conjunto para reconocer posibles zonas de interés estructural. "
                "La interpretación se mantiene como una aproximación regional, "
                "pedagógica y contextual."
            ),
        },
    }


# Alias de compatibilidad para rutas antiguas o llamadas previas

def get_general_interpretation():
    return get_interpretation_summary()


def get_integrated_interpretation():
    return get_interpretation_summary()


def get_project_interpretation():
    return get_interpretation_summary()


def get_interpretation():
    return get_interpretation_summary()


def build_interpretation():
    return get_interpretation_summary()


def get_cards():
    return get_interpretation_cards()