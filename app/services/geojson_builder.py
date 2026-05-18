def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _records_from_input(data):
    if data is None:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    if hasattr(data, "to_dict"):
        try:
            return data.to_dict(orient="records")
        except TypeError:
            return []

    return []


def _get_value(record, candidates):
    for name in candidates:
        if name in record and record[name] not in ("", None):
            return record[name]
    return None


def dataframe_to_geojson(
    data,
    lon_field="lon",
    lat_field="lat",
    lon_col=None,
    lat_col=None,
    properties=None,
):
    """
    Convierte registros con coordenadas a GeoJSON.

    El nombre se conserva por compatibilidad, pero no requiere pandas.
    """
    records = _records_from_input(data)
    features = []

    lon_candidates = [
        lon_col,
        lon_field,
        "lon",
        "longitud",
        "longitude",
        "x",
        "X",
        "LON",
        "Lon",
    ]

    lat_candidates = [
        lat_col,
        lat_field,
        "lat",
        "latitud",
        "latitude",
        "y",
        "Y",
        "LAT",
        "Lat",
    ]

    lon_candidates = [item for item in lon_candidates if item]
    lat_candidates = [item for item in lat_candidates if item]

    for record in records:
        lon = _to_float(_get_value(record, lon_candidates))
        lat = _to_float(_get_value(record, lat_candidates))

        if lon is None or lat is None:
            continue

        if properties:
            props = {key: record.get(key) for key in properties if key in record}
        else:
            props = dict(record)

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": props,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def gnss_to_geojson(data):
    records = _records_from_input(data)
    features = []

    for record in records:
        lon = _to_float(_get_value(record, [
            "lon",
            "longitud",
            "station_lon",
            "gnss_lon",
            "X",
        ]))

        lat = _to_float(_get_value(record, [
            "lat",
            "latitud",
            "station_lat",
            "gnss_lat",
            "Y",
        ]))

        if lon is None or lat is None:
            continue

        props = dict(record)

        vel_e = _to_float(_get_value(record, [
            "vel_e_residual_mm_yr",
            "vel_e_mm_yr",
            "east_mm_yr",
            "e_mm_yr",
            "velocidad_este_mm_yr",
        ]))

        vel_n = _to_float(_get_value(record, [
            "vel_n_residual_mm_yr",
            "vel_n_mm_yr",
            "north_mm_yr",
            "n_mm_yr",
            "velocidad_norte_mm_yr",
        ]))

        vel_u = _to_float(_get_value(record, [
            "vel_u_mm_yr",
            "vel_up_mm_yr",
            "up_mm_yr",
            "u_mm_yr",
            "velocidad_up_mm_yr",
        ]))

        if vel_e is not None:
            props["vel_e_visual"] = vel_e

        if vel_n is not None:
            props["vel_n_visual"] = vel_n

        if vel_u is not None:
            props["vel_u_visual"] = vel_u

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": props,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def points_to_geojson(data):
    return dataframe_to_geojson(data)


def grid_to_geojson(data):
    return dataframe_to_geojson(data)