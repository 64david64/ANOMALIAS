from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    OUTPUT_DIR = PROCESSED_DIR / "salidas_sismotectonicas"

    GRID_FILE = OUTPUT_DIR / "grilla_bouguer_gradiente.csv"
    GNSS_FILE = OUTPUT_DIR / "gnss_resumen_estaciones.csv"
    POINTS_FILE = OUTPUT_DIR / "puntos_gravimetricos_clasificados.csv"
    METADATA_FILE = OUTPUT_DIR / "metadata_variables.json"

    FIGURES_DIR = OUTPUT_DIR / "figuras"

    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False