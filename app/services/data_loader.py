from pathlib import Path
import csv
import json

from flask import current_app


def _get_config_path(name, fallback):
    try:
        return Path(current_app.config[name])
    except RuntimeError:
        # Permite probar el módulo fuera del contexto Flask.
        return fallback


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = BASE_DIR / "data" / "processed" / "salidas_sismotectonicas"
DEFAULT_FIGURES_DIR = DEFAULT_OUTPUT_DIR / "figuras"


def output_dir():
    return _get_config_path("OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def figures_dir():
    return _get_config_path("FIGURES_DIR", DEFAULT_FIGURES_DIR)


def grid_file():
    return _get_config_path("GRID_FILE", DEFAULT_OUTPUT_DIR / "grilla_bouguer_gradiente.csv")


def gnss_file():
    return _get_config_path("GNSS_FILE", DEFAULT_OUTPUT_DIR / "gnss_resumen_estaciones.csv")


def points_file():
    return _get_config_path("POINTS_FILE", DEFAULT_OUTPUT_DIR / "puntos_gravimetricos_clasificados.csv")


def metadata_file():
    return _get_config_path("METADATA_FILE", DEFAULT_OUTPUT_DIR / "metadata_variables.json")


def _read_csv(path):
    path = Path(path)

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sample_records(records, sample=1, max_rows=None):
    """
    Reduce registros para visualización web.

    sample=1 conserva todos.
    sample=2 toma uno de cada dos, etc.
    """
    try:
        sample = int(sample)
    except (TypeError, ValueError):
        sample = 1

    if sample < 1:
        sample = 1

    sampled = records[::sample]

    if max_rows is not None:
        try:
            max_rows = int(max_rows)
            sampled = sampled[:max_rows]
        except (TypeError, ValueError):
            pass

    return sampled


def load_grid_data(sample=1, max_rows=None):
    records = _read_csv(grid_file())
    return _sample_records(records, sample=sample, max_rows=max_rows)


def load_grid(sample=1, max_rows=None):
    return load_grid_data(sample=sample, max_rows=max_rows)


def load_gnss_data():
    return _read_csv(gnss_file())


def load_gnss():
    return load_gnss_data()


def load_gravity_points(sample=1, max_rows=None):
    records = _read_csv(points_file())
    return _sample_records(records, sample=sample, max_rows=max_rows)


def load_points(sample=1, max_rows=None):
    return load_gravity_points(sample=sample, max_rows=max_rows)


def load_gravity(sample=1, max_rows=None):
    return load_gravity_points(sample=sample, max_rows=max_rows)


def load_metadata():
    path = metadata_file()

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_metadata():
    return load_metadata()


def list_figures():
    directory = figures_dir()

    if not directory.exists():
        return []

    figures = []

    for path in sorted(directory.glob("*.png")):
        figures.append({
            "filename": path.name,
            "url": f"/figuras/{path.name}",
        })

    return figures


def load_figures():
    return list_figures()


def get_figures():
    return list_figures()


def get_available_variables(records=None):
    """
    Devuelve variables disponibles para el visor.

    Usa primero metadata_variables.json.
    Si no existe, infiere columnas desde la grilla.
    """
    metadata = load_metadata()
    variables = []

    if isinstance(metadata, dict):
        if "variables" in metadata and isinstance(metadata["variables"], dict):
            for key, info in metadata["variables"].items():
                variables.append({
                    "key": key,
                    "name": info.get("nombre", info.get("name", key)),
                    "unit": info.get("unidad", info.get("unit", "")),
                    "description": info.get("descripcion", info.get("description", "")),
                })
            return variables

        for key, info in metadata.items():
            if isinstance(info, dict):
                variables.append({
                    "key": key,
                    "name": info.get("nombre", info.get("name", key)),
                    "unit": info.get("unidad", info.get("unit", "")),
                    "description": info.get("descripcion", info.get("description", "")),
                })

        if variables:
            return variables

    if records is None:
        records = load_grid_data(sample=1, max_rows=1)

    if not records:
        return []

    excluded = {"lat", "lon", "latitud", "longitud", "x", "y"}

    for column in records[0].keys():
        if column.lower() not in excluded:
            variables.append({
                "key": column,
                "name": column.replace("_", " ").title(),
                "unit": "",
                "description": "Variable exportada desde el procesamiento gravimétrico.",
            })

    return variables


def load_variables():
    return get_available_variables()


def _get_value(row, candidates):
    for name in candidates:
        if name in row and row[name] not in ("", None):
            return row[name]
    return None


def build_profiles(lat_values=None, tolerance=0.05):
    """
    Construye perfiles W-E aproximados desde la grilla exportada.

    No reemplaza la figura oficial de perfiles generada por MATLAB, pero permite
    una exploración simple desde el visor.
    """
    records = load_grid_data(sample=1)

    if not records:
        return []

    if lat_values is None:
        lat_values = [6.2, 5.0, 4.6, 3.5]

    profile_names = {
        6.2: "~6.2° N - Medellín",
        5.0: "~5.0° N - Manizales",
        4.6: "~4.6° N - Bogotá",
        3.5: "~3.5° N - Neiva",
    }

    profiles = []

    for target_lat in lat_values:
        candidates = []

        for row in records:
            lon = _to_float(_get_value(row, ["lon", "longitud", "longitude", "x", "X"]))
            lat = _to_float(_get_value(row, ["lat", "latitud", "latitude", "y", "Y"]))

            bouguer = _to_float(_get_value(row, [
                "bouguer_mgal",
                "anomalia_bouguer_mgal",
                "Anomalia_Bouguer",
                "bouguer",
            ]))

            altura = _to_float(_get_value(row, [
                "altura_m",
                "altura",
                "h_m",
                "height_m",
            ]))

            gradiente = _to_float(_get_value(row, [
                "gradiente_mgal_km",
                "gradiente_horizontal_mgal_km",
                "gradient_mgal_km",
            ]))

            if lon is None or lat is None:
                continue

            if abs(lat - target_lat) <= tolerance:
                candidates.append({
                    "lon": lon,
                    "lat": lat,
                    "bouguer_mgal": bouguer,
                    "altura_m": altura,
                    "gradiente_mgal_km": gradiente,
                })

        candidates = sorted(candidates, key=lambda item: item["lon"])

        profiles.append({
            "id": f"perfil_{str(target_lat).replace('.', '_')}",
            "name": profile_names.get(target_lat, f"Perfil latitud {target_lat}°"),
            "target_lat": target_lat,
            "points": candidates,
        })

    return profiles


def load_profiles():
    return build_profiles()


def get_profiles():
    return build_profiles()