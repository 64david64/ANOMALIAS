def get_case_study_context():
    return {
        "title": "Caso de estudio: campo de velocidades geodésicas en Colombia",
        "description": (
            "Este visor toma como referencia conceptual el campo de velocidades geodésicas "
            "aplicado al análisis del marco de referencia geodésico de Colombia. El propósito "
            "no es replicar de forma completa un producto geodésico oficial, sino descomponer "
            "el proceso, dar zoom a un conjunto reducido de estaciones GNSS y relacionarlo "
            "de forma pedagógica con anomalías gravimétricas regionales."
        ),
        "data_source": (
            "Los datos GNSS fueron consultados a partir de productos públicos del Nevada "
            "Geodetic Laboratory. Las anomalías gravimétricas fueron integradas como insumo "
            "geofísico complementario para el análisis regional."
        ),
        "reference_frame": "IGS20 / ITRF2020",
        "scope": (
            "El análisis se plantea como una aproximación académica y pedagógica para visualizar "
            "relaciones espaciales entre deformación geodésica, anomalías gravimétricas y posibles "
            "zonas de interés estructural."
        ),
    }


def get_general_interpretation():
    return {
        "titulo": "Interpretación sismotectónica contextual",
        "descripcion": (
            "La integración entre anomalías gravimétricas y velocidades GNSS se interpreta "
            "de forma contextual por proximidad espacial. Los puntos gravimétricos no se "
            "consideran pertenecientes directamente a una estación GNSS, sino como información "
            "regional complementaria."
        ),
        "mensaje_clave": (
            "El visor permite explorar posibles relaciones entre contrastes gravimétricos, "
            "gradiente horizontal de Bouguer y velocidades GNSS retenidas, evitando "
            "sobreinterpretar los resultados como evidencia directa de fallas activas."
        ),
    }


def get_gravity_interpretation():
    return {
        "title": "Lectura gravimétrica",
        "items": [
            {
                "name": "Anomalía de aire libre",
                "text": (
                    "Permite observar variaciones del campo gravitatorio después de considerar "
                    "el efecto de la altura."
                ),
            },
            {
                "name": "Anomalía de Bouguer",
                "text": (
                    "Resalta contrastes gravimétricos asociados potencialmente a cambios de "
                    "densidad en la corteza."
                ),
            },
            {
                "name": "Gradiente horizontal",
                "text": (
                    "Identifica zonas donde la anomalía de Bouguer cambia con mayor rapidez, "
                    "compatibles con posibles lineamientos estructurales."
                ),
            },
        ],
    }


def get_gnss_interpretation():
    return {
        "title": "Lectura GNSS",
        "description": (
            "Las estaciones GNSS permiten analizar cambios de posición durante una serie temporal. "
            "En este proyecto, los desplazamientos acumulados se transforman en velocidades medias "
            "expresadas en mm/año."
        ),
        "important_notes": [
            "Las velocidades se interpretan dentro del marco IGS20 / ITRF2020.",
            "Se usan únicamente estaciones retenidas con comportamiento cinemático más consistente.",
            (
                "Los vectores residuales ayudan a observar diferencias relativas entre estaciones, "
                "sin asumir que representan por sí solos deformación local definitiva."
            ),
        ],
    }


def get_integrated_interpretation():
    return {
        "title": "Integración gravedad-GNSS",
        "description": (
            "La integración se realiza mediante superposición espacial y lectura contextual. "
            "Las zonas donde coinciden gradientes gravimétricos altos con cambios relativos en "
            "los vectores GNSS pueden considerarse áreas de interés estructural, pero no deben "
            "entenderse automáticamente como fallas activas confirmadas."
        ),
        "rules": [
            "Los puntos gravimétricos se emplean para construir superficies regionales.",
            "Las estaciones GNSS representan deformación geodésica estimada desde series temporales.",
            "La relación entre ambos insumos es contextual por proximidad, no una asociación directa.",
        ],
    }


def get_methodological_notes():
    return [
        {
            "title": "Caso de estudio existente con zoom pedagógico",
            "text": (
                "El proyecto parte de un caso de estudio ya existente sobre campo de velocidades "
                "geodésicas en Colombia. El visor propone una lectura más descompuesta y didáctica."
            ),
        },
        {
            "title": "Relación contextual gravedad-GNSS",
            "text": (
                "Los puntos gravimétricos no se asignan como pertenecientes directamente a una "
                "estación GNSS. Su relación se maneja por proximidad espacial."
            ),
        },
        {
            "title": "Lineamientos potenciales",
            "text": (
                "El visor no declara fallas activas. Las zonas de alto gradiente se presentan como "
                "lineamientos potenciales o áreas de interés estructural."
            ),
        },
    ]


def get_limitations():
    return [
        "El visor tiene un propósito académico y pedagógico; no reemplaza un estudio oficial.",
        "Las velocidades GNSS se calculan como tasas medias desde desplazamientos acumulados.",
        "La interpretación de lineamientos debe contrastarse con información geológica y sismológica.",
        "La integración entre gravedad y GNSS es contextual, no una relación causal directa.",
    ]


def get_interpretation_cards():
    return [
        {
            "title": "Anomalías gravimétricas",
            "text": (
                "Permiten observar variaciones regionales del campo gravitatorio y posibles "
                "contrastes de densidad cortical."
            ),
        },
        {
            "title": "Gradiente horizontal",
            "text": (
                "Resalta zonas donde la anomalía cambia rápidamente, útiles para identificar "
                "posibles lineamientos estructurales."
            ),
        },
        {
            "title": "Velocidades GNSS",
            "text": (
                "Representan la tendencia media de movimiento de estaciones geodésicas durante "
                "su serie temporal."
            ),
        },
        {
            "title": "Lectura integrada",
            "text": (
                "Relaciona de forma contextual las variables gravimétricas y GNSS para apoyar "
                "una interpretación sismotectónica regional."
            ),
        },
    ]


def get_interpretation_summary():
    return {
        "case_study": get_case_study_context(),
        "general": get_general_interpretation(),
        "gravity": get_gravity_interpretation(),
        "gnss": get_gnss_interpretation(),
        "integrated": get_integrated_interpretation(),
        "methodological_notes": get_methodological_notes(),
        "limitations": get_limitations(),
        "cards": get_interpretation_cards(),
    }


def build_interpretation():
    return get_interpretation_summary()


def get_interpretation():
    return get_interpretation_summary()


def get_project_interpretation():
    return get_interpretation_summary()


def get_context():
    return get_case_study_context()


def get_cards():
    return get_interpretation_cards()