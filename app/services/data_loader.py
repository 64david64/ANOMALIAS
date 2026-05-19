from pathlib import Path
import csv
import json


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed" / "salidas_sismotectonicas"
FIGURES_DIR = DATA_DIR / "figuras"


def _read_csv(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def _to_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _sample_records(records, sample=1, max_rows=None):
    try:
        sample = int(sample)
    except (TypeError, ValueError):
        sample = 1

    sample = max(sample, 1)

    sampled = records[::sample]

    if max_rows is not None:
        try:
            max_rows = int(max_rows)
            sampled = sampled[:max_rows]
        except (TypeError, ValueError):
            pass

    return sampled


def load_grid(sample=1, max_rows=None):
    path = DATA_DIR / "grilla_bouguer_gradiente.csv"
    records = _read_csv(path)
    return _sample_records(records, sample=sample, max_rows=max_rows)


def load_grid_data(sample=1, max_rows=None):
    return load_grid(sample=sample, max_rows=max_rows)


def load_gnss():
    path = DATA_DIR / "gnss_resumen_estaciones.csv"
    return _read_csv(path)


def load_gnss_data():
    return load_gnss()


def load_points(sample=1, max_rows=None):
    path = DATA_DIR / "puntos_gravimetricos_clasificados.csv"
    records = _read_csv(path)
    return _sample_records(records, sample=sample, max_rows=max_rows)


def load_gravity_points(sample=1, max_rows=None):
    return load_points(sample=sample, max_rows=max_rows)


def load_metadata():
    path = DATA_DIR / "metadata_variables.json"

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_metadata():
    return load_metadata()


def load_figures():
    if not FIGURES_DIR.exists():
        return []

    figures = []

    for path in sorted(FIGURES_DIR.glob("*.png")):
        figures.append({
            "filename": path.name,
            "url": f"/figura/{path.name}"
        })

    return figures


def list_figures():
    return load_figures()


def get_figures():
    return load_figures()


def get_available_variables(records=None):
    metadata = load_metadata()
    variables = []

    if isinstance(metadata, dict):
        if "variables" in metadata and isinstance(metadata["variables"], dict):
            for key, info in metadata["variables"].items():
                variables.append({
                    "key": key,
                    "name": info.get("nombre", info.get("name", key)),
                    "unit": info.get("unidad", info.get("unit", "")),
                    "description": info.get("descripcion", info.get("description", ""))
                })
            return variables

        for key, info in metadata.items():
            if isinstance(info, dict):
                variables.append({
                    "key": key,
                    "name": info.get("nombre", info.get("name", key)),
                    "unit": info.get("unidad", info.get("unit", "")),
                    "description": info.get("descripcion", info.get("description", ""))
                })

        if variables:
            return variables

    if records is None:
        records = load_grid(sample=20, max_rows=1)

    if not records:
        return []

    excluded = {"lat", "lon", "latitud", "longitud"}

    for column in records[0].keys():
        if column not in excluded:
            variables.append({
                "key": column,
                "name": column.replace("_", " ").title(),
                "unit": "",
                "description": "Variable exportada desde el procesamiento MATLAB."
            })

    return variables


def build_profiles(lat_values=None):
    """
    Construye perfiles W-E desde la grilla exportada.

    Corrección importante:
    antes los perfiles podían quedarse vacíos si ninguna latitud de la grilla
    caía exactamente dentro de una tolerancia fija. Ahora se toma la latitud
    disponible más cercana a cada latitud objetivo.
    """

    records = load_grid(sample=1, max_rows=None)

    if not records:
        return {
            "profiles": [],
            "message": "No se encontró grilla procesada para construir perfiles."
        }

    if lat_values is None:
        lat_values = [6.2, 5.0, 4.6, 3.5]

    profile_names = {
        6.2: "~6.2° N - Medellín",
        5.0: "~5.0° N - Manizales",
        4.6: "~4.6° N - Bogotá",
        3.5: "~3.5° N - Neiva"
    }

    # Latitudes únicas disponibles en la grilla
    available_lats = sorted({
        round(_to_float(row.get("lat") or row.get("latitud")), 6)
        for row in records
        if _to_float(row.get("lat") or row.get("latitud")) is not None
    })

    if not available_lats:
        return {
            "profiles": [],
            "message": "La grilla no contiene latitudes válidas."
        }

    profiles = []

    for target_lat in lat_values:
        try:
            target_lat = float(target_lat)
        except (TypeError, ValueError):
            continue

        nearest_lat = min(available_lats, key=lambda value: abs(value - target_lat))

        points = []

        for row in records:
            lat = _to_float(row.get("lat") or row.get("latitud"))
            lon = _to_float(row.get("lon") or row.get("longitud"))

            if lat is None or lon is None:
                continue

            if round(lat, 6) != nearest_lat:
                continue

            points.append({
                "lon": lon,
                "lat": lat,
                "bouguer_mgal": _to_float(row.get("bouguer_mgal")),
                "aire_libre_mgal": _to_float(row.get("aire_libre_mgal")),
                "gradiente_mgal_km": _to_float(row.get("gradiente_mgal_km")),
                "altura_m": _to_float(row.get("altura_m")),
                "gravity_anomaly_base_mgal": _to_float(row.get("gravity_anomaly_base_mgal"))
            })

        points = sorted(points, key=lambda item: item["lon"])

        profiles.append({
            "id": f"profile_{str(target_lat).replace('.', '_')}",
            "name": profile_names.get(round(target_lat, 1), f"Perfil ~{target_lat:.1f}° N"),
            "target_lat": target_lat,
            "actual_lat": nearest_lat,
            "points": points
        })

    return {
        "profiles": profiles,
        "message": "Perfiles construidos usando la latitud más cercana disponible en la grilla."
    }


def load_profiles():
    return build_profiles()


def get_profiles():
    return build_profiles()