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
from .services.geojson_builder import dataframe_to_geojson, gnss_to_geojson
from .services.interpretation_service import get_interpretation_cards, get_interpretation_summary
from .services.metadata_service import get_layer_catalog

bp = Blueprint("main", __name__)


@bp.route("/")
def inicio():
    return render_template("inicio.html", title="Inicio")


@bp.route("/marco-conceptual")
def marco_conceptual():
    return render_template("marco_conceptual.html", title="Marco conceptual")


@bp.route("/metodologia")
def metodologia():
    return render_template("metodologia.html", title="Metodología")


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


@bp.route("/figuras/<path:filename>")
def figuras(filename):
    return send_from_directory(current_app.config["FIGURES_DIR"], filename)


@bp.route("/api/status")
def api_status():
    output_dir = Path(current_app.config["OUTPUT_DIR"])
    required_files = [
        Path(current_app.config["GRID_FILE"]),
        Path(current_app.config["GNSS_FILE"]),
        Path(current_app.config["POINTS_FILE"]),
        Path(current_app.config["METADATA_FILE"]),
    ]

    return jsonify({
        "ok": output_dir.exists() and all(path.exists() for path in required_files),
        "output_dir": str(output_dir),
        "required_files": [str(path) for path in required_files],
        "missing": [str(path) for path in required_files if not path.exists()],
    })


@bp.route("/api/metadata")
def api_metadata():
    return jsonify(load_metadata())


@bp.route("/api/layers")
def api_layers():
    return jsonify(get_layer_catalog())


@bp.route("/api/figuras")
def api_figuras():
    return jsonify(load_figures())


@bp.route("/api/grilla")
def api_grilla():
    sample = request.args.get("sample", default=2, type=int)
    max_rows = request.args.get("max_rows", default=15000, type=int)

    records = load_grid(sample=sample, max_rows=max_rows)

    return jsonify({
        "count": len(records),
        "variables": get_available_variables(records),
        "records": records,
    })


@bp.route("/api/grilla/geojson")
def api_grilla_geojson():
    sample = request.args.get("sample", default=2, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)
    variable = request.args.get("variable", default="bouguer_mgal", type=str)

    records = load_grid(sample=sample, max_rows=max_rows)
    geojson = dataframe_to_geojson(records, lon_field="lon", lat_field="lat")
    geojson["selected_variable"] = variable

    return jsonify(geojson)


@bp.route("/api/gnss")
def api_gnss():
    records = load_gnss()

    return jsonify({
        "count": len(records),
        "records": records,
    })


@bp.route("/api/gnss/geojson")
def api_gnss_geojson():
    records = load_gnss()
    return jsonify(gnss_to_geojson(records))


@bp.route("/api/puntos-gravimetricos")
def api_puntos_gravimetricos():
    sample = request.args.get("sample", default=3, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)

    records = load_points(sample=sample, max_rows=max_rows)

    return jsonify({
        "count": len(records),
        "records": records,
    })


@bp.route("/api/puntos-gravimetricos/geojson")
def api_puntos_gravimetricos_geojson():
    sample = request.args.get("sample", default=3, type=int)
    max_rows = request.args.get("max_rows", default=12000, type=int)

    records = load_points(sample=sample, max_rows=max_rows)
    return jsonify(dataframe_to_geojson(records, lon_field="lon", lat_field="lat"))


@bp.route("/api/perfiles")
def api_perfiles():
    latitudes = request.args.get("latitudes", default="6.2,5.0,4.6,3.5", type=str)
    lat_values = []

    for item in latitudes.split(","):
        try:
            lat_values.append(float(item.strip()))
        except ValueError:
            continue

    profiles = build_profiles(lat_values=lat_values)
    return jsonify(profiles)


@bp.route("/api/interpretacion")
def api_interpretacion():
    return jsonify(get_interpretation_summary())


@bp.route("/api/interpretacion/cards")
def api_interpretacion_cards():
    return jsonify(get_interpretation_cards())