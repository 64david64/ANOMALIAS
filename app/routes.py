from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory

from .services.data_loader import (
    build_profiles,
    get_available_variables,
    load_figures,
    load_grid,
    load_gnss,
    load_metadata,
    load_points,
)

from .services.geojson_builder import (
    dataframe_to_geojson,
    gnss_to_geojson,
    points_to_geojson,
)

from .services.metadata_service import (
    get_layer_catalog,
    get_project_metadata,
)

from .services.interpretation_service import (
    get_interpretation_summary,
    get_interpretation_cards,
)

from .services.station_service import get_station_context


bp = Blueprint("main", __name__)


# ============================================================
# Helpers
# ============================================================

def _sample_records(records, sample: int = 1, max_rows: int | None = None):
    """
    Reduce la cantidad de registros enviados al navegador.

    sample = 1  -> usa todos los registros.
    sample = 2  -> usa uno de cada dos.
    sample = 3  -> usa uno de cada tres.
    """

    if not isinstance(records, list):
        return []

    if sample is None or sample < 1:
        sample = 1

    sampled = records[::sample]

    if max_rows is not None and max_rows > 0:
        sampled = sampled[:max_rows]

    return sampled


def _safe_count(records):
    if isinstance(records, list):
        return len(records)
    return 0


# ============================================================
# Páginas principales
# ============================================================

@bp.route("/")
def inicio():
    return render_template("inicio.html", title="Inicio")


@bp.route("/marco-conceptual")
def marco_conceptual():
    return render_template("marco_conceptual.html", title="Marco conceptual")


@bp.route("/metodologia")
def metodologia():
    return render_template("metodologia.html", title="Metodología")


@bp.route("/resultados")
def resultados():
    figures = load_figures()
    return render_template(
        "resultados.html",
        title="Resultados",
        figures=figures,
    )


@bp.route("/visor-2d")
def visor_2d():
    return render_template("visor_2d.html", title="Visor 2D")


@bp.route("/visor-3d")
def visor_3d():
    return render_template("visor_3d.html", title="Visor 3D")


@bp.route("/perfiles")
def perfiles():
    return render_template("perfiles.html", title="Perfiles W-E")


@bp.route("/gnss")
def gnss():
    return render_template("gnss.html", title="GNSS")


@bp.route("/interpretacion")
def interpretacion():
    return render_template("interpretacion.html", title="Interpretación")


@bp.route("/acerca")
def acerca():
    return render_template("acerca.html", title="Acerca del proyecto")


# ============================================================
# Figuras exportadas por MATLAB
# ============================================================

@bp.route("/figura/<path:filename>")
def figura(filename: str):
    figures_dir = current_app.config["FIGURES_DIR"]
    return send_from_directory(figures_dir, filename)


# ============================================================
# API general
# ============================================================

@bp.route("/api/status")
def api_status():
    output_dir = Path(current_app.config["OUTPUT_DIR"])

    required_files = [
        Path(current_app.config["GRID_FILE"]),
        Path(current_app.config["GNSS_FILE"]),
        Path(current_app.config["POINTS_FILE"]),
        Path(current_app.config["METADATA_FILE"]),
    ]

    missing = [str(path) for path in required_files if not path.exists()]

    return jsonify({
        "ok": output_dir.exists() and not missing,
        "output_dir": str(output_dir),
        "required_files": [str(path) for path in required_files],
        "missing": missing,
    })


@bp.route("/api/metadata")
def api_metadata():
    return jsonify(load_metadata())


@bp.route("/api/project")
def api_project():
    return jsonify(get_project_metadata())


@bp.route("/api/layers")
def api_layers():
    return jsonify(get_layer_catalog())


@bp.route("/api/figuras")
def api_figuras():
    return jsonify(load_figures())


# ============================================================
# API grilla procesada
# ============================================================

@bp.route("/api/grilla")
def api_grilla():
    sample = request.args.get("sample", default=1, type=int)
    max_rows = request.args.get("max_rows", default=15000, type=int)

    records = load_grid()
    sampled = _sample_records(records, sample=sample, max_rows=max_rows)

    return jsonify({
        "count": _safe_count(records),
        "returned": _safe_count(sampled),
        "variables": get_available_variables(),
        "records": sampled,
    })


@bp.route("/api/grilla/geojson")
def api_grilla_geojson():
    sample = request.args.get("sample", default=2, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)
    variable = request.args.get("variable", default="gradiente_mgal_km", type=str)

    records = load_grid()
    sampled = _sample_records(records, sample=sample, max_rows=max_rows)

    geojson = dataframe_to_geojson(sampled, lon_field="lon", lat_field="lat")
    geojson["selected_variable"] = variable

    return jsonify(geojson)


# ============================================================
# API GNSS
# ============================================================

@bp.route("/api/gnss")
def api_gnss():
    records = load_gnss()

    return jsonify({
        "count": _safe_count(records),
        "records": records,
    })


@bp.route("/api/gnss/geojson")
def api_gnss_geojson():
    records = load_gnss()
    return jsonify(gnss_to_geojson(records))


@bp.route("/api/estaciones/contexto")
def api_estaciones_contexto():
    stations = get_station_context()

    return jsonify({
        "count": _safe_count(stations),
        "records": stations,
    })


# ============================================================
# API puntos gravimétricos
# ============================================================

@bp.route("/api/puntos-gravimetricos")
def api_puntos_gravimetricos():
    sample = request.args.get("sample", default=1, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)

    records = load_points()
    sampled = _sample_records(records, sample=sample, max_rows=max_rows)

    return jsonify({
        "count": _safe_count(records),
        "returned": _safe_count(sampled),
        "records": sampled,
    })


@bp.route("/api/puntos-gravimetricos/geojson")
def api_puntos_gravimetricos_geojson():
    sample = request.args.get("sample", default=2, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)

    records = load_points()
    sampled = _sample_records(records, sample=sample, max_rows=max_rows)

    return jsonify(points_to_geojson(sampled))


# ============================================================
# API perfiles W-E
# ============================================================

@bp.route("/api/perfiles")
def api_perfiles():
    """
    Devuelve perfiles W-E construidos desde la grilla procesada.

    Si el data_loader acepta latitudes personalizadas, se pasan.
    Si no, usa las latitudes por defecto del servicio.
    """

    latitudes = request.args.get("latitudes", default="", type=str)
    lat_values = []

    if latitudes:
        for item in latitudes.split(","):
            try:
                lat_values.append(float(item.strip()))
            except ValueError:
                continue

    try:
        if lat_values:
            profiles = build_profiles(lat_values=lat_values)
        else:
            profiles = build_profiles()
    except TypeError:
        profiles = build_profiles()

    return jsonify(profiles)


# ============================================================
# API interpretación
# ============================================================

@bp.route("/api/interpretacion")
def api_interpretacion():
    return jsonify(get_interpretation_summary())


@bp.route("/api/interpretacion/tarjetas")
def api_interpretacion_tarjetas():
    return jsonify(get_interpretation_cards())