from .data_loader import load_gnss


STATION_DESCRIPTIONS = {
    "BER1": {
        "entorno": "Estación GNSS retenida para análisis regional.",
        "descripcion": "Punto de control geodésico para contraste cinemático regional."
    },
    "MEDE": {
        "entorno": "Estación asociada al entorno de Medellín.",
        "descripcion": "Referencia para observar comportamiento relativo en el sector noroccidental del área de estudio."
    },
    "NEV1": {
        "entorno": "Estación asociada al entorno de Neiva.",
        "descripcion": "Referencia para observar comportamiento relativo en el sector sur del área de estudio."
    },
    "PER2": {
        "entorno": "Estación asociada al entorno de Pereira / eje cafetero.",
        "descripcion": "Referencia para comparar velocidades GNSS con contrastes gravimétricos andinos."
    },
    "TUNA": {
        "entorno": "Estación asociada al entorno de Tunja.",
        "descripcion": "Referencia para observar comportamiento relativo en el sector centro-oriental."
    },
    "VIVI": {
        "entorno": "Estación asociada al entorno de Villavicencio.",
        "descripcion": "Referencia para evaluar el cambio entre el piedemonte y la zona oriental."
    }
}


def _get_first(row, candidates, default=""):
    for key in candidates:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def _to_float(value, default=0.0):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def get_station_context():
    records = load_gnss()
    stations = []

    for row in records:
        name = _get_first(row, [
            "estacion",
            "station",
            "nombre",
            "codigo",
            "name",
            "gnss_station"
        ])

        if not name:
            continue

        info = STATION_DESCRIPTIONS.get(name, {
            "entorno": "Estación GNSS retenida para análisis regional.",
            "descripcion": "Estación usada como referencia cinemática dentro del visor."
        })

        lat = _to_float(_get_first(row, [
            "lat",
            "latitud",
            "station_lat",
            "gnss_lat"
        ], None), None)

        lon = _to_float(_get_first(row, [
            "lon",
            "longitud",
            "station_lon",
            "gnss_lon"
        ], None), None)

        # Velocidades absolutas exportadas por MATLAB
        vel_e_abs = _to_float(_get_first(row, [
            "vel_e_abs_mm_yr",
            "vel_e_mm_yr",
            "east_mm_yr",
            "e_mm_yr"
        ], 0.0))

        vel_n_abs = _to_float(_get_first(row, [
            "vel_n_abs_mm_yr",
            "vel_n_mm_yr",
            "north_mm_yr",
            "n_mm_yr"
        ], 0.0))

        vel_u_abs = _to_float(_get_first(row, [
            "vel_u_abs_mm_yr",
            "vel_up_mm_yr",
            "vel_u_mm_yr",
            "up_mm_yr",
            "u_mm_yr"
        ], 0.0))

        vel_h_abs = _to_float(_get_first(row, [
            "vel_horizontal_abs_mm_yr",
            "vel_h_abs_mm_yr",
            "vel_horizontal_mm_yr"
        ], 0.0))

        # Velocidades residuales exportadas por MATLAB
        vel_e_res = _to_float(_get_first(row, [
            "vel_e_res_mm_yr",
            "vel_e_residual_mm_yr"
        ], 0.0))

        vel_n_res = _to_float(_get_first(row, [
            "vel_n_res_mm_yr",
            "vel_n_residual_mm_yr"
        ], 0.0))

        vel_u_res = _to_float(_get_first(row, [
            "vel_u_res_mm_yr",
            "vel_u_residual_mm_yr"
        ], 0.0))

        vel_h_res = _to_float(_get_first(row, [
            "vel_horizontal_res_mm_yr",
            "vel_h_res_mm_yr",
            "vel_horizontal_residual_mm_yr"
        ], 0.0))

        azimut_abs = _to_float(_get_first(row, [
            "azimut_abs_grados",
            "azimuth_abs_deg",
            "azimuth_deg"
        ], 0.0))

        azimut_res = _to_float(_get_first(row, [
            "azimut_res_grados",
            "azimuth_res_deg"
        ], 0.0))

        duration = _to_float(_get_first(row, [
            "duracion_yr",
            "duration_yr",
            "duracion_anios"
        ], 0.0))

        stations.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "reference_frame": _get_first(row, ["marco_referencia"], "IGS20 / ITRF2020"),

            "entorno": info["entorno"],
            "descripcion": info["descripcion"],

            "vel_e_abs": vel_e_abs,
            "vel_n_abs": vel_n_abs,
            "vel_u_abs": vel_u_abs,
            "vel_h_abs": vel_h_abs,

            "vel_e_res": vel_e_res,
            "vel_n_res": vel_n_res,
            "vel_u_res": vel_u_res,
            "vel_h_res": vel_h_res,

            # Compatibilidad con la plantilla actual
            "vel_e": vel_e_abs,
            "vel_n": vel_n_abs,
            "vel_u": vel_u_abs,
            "vel_h": vel_h_abs,

            "azimut_abs": azimut_abs,
            "azimut_res": azimut_res,
            "duration": duration,

            "role": "Estación GNSS retenida para análisis regional",
            "interpretation": (
                "Esta estación representa información cinemática usada de forma "
                "contextual junto con anomalías gravimétricas regionales."
            )
        })

    return stations