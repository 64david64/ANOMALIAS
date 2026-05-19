def _to_float(value):
    try:
        if value in (None, ""):
            return None
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


def dataframe_to_geojson(data, lon_field="lon", lat_field="lat", **kwargs):
    records = _records_from_input(data)
    features = []

    for record in records:
        lon = _to_float(
            record.get(lon_field)
            or record.get("longitud")
            or record.get("longitude")
            or record.get("Lon")
            or record.get("LON")
            or record.get("x")
            or record.get("X")
        )

        lat = _to_float(
            record.get(lat_field)
            or record.get("latitud")
            or record.get("latitude")
            or record.get("Lat")
            or record.get("LAT")
            or record.get("y")
            or record.get("Y")
        )

        if lon is None or lat is None:
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": dict(record)
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def gnss_to_geojson(data):
    records = _records_from_input(data)
    features = []

    for record in records:
        lon = _to_float(
            record.get("lon")
            or record.get("longitud")
            or record.get("station_lon")
            or record.get("gnss_lon")
            or record.get("X")
        )

        lat = _to_float(
            record.get("lat")
            or record.get("latitud")
            or record.get("station_lat")
            or record.get("gnss_lat")
            or record.get("Y")
        )

        if lon is None or lat is None:
            continue

        properties = dict(record)

        vel_e_abs = _to_float(
            record.get("vel_e_abs_mm_yr")
            or record.get("vel_e_mm_yr")
            or record.get("east_mm_yr")
            or record.get("e_mm_yr")
        )

        vel_n_abs = _to_float(
            record.get("vel_n_abs_mm_yr")
            or record.get("vel_n_mm_yr")
            or record.get("north_mm_yr")
            or record.get("n_mm_yr")
        )

        vel_u_abs = _to_float(
            record.get("vel_u_abs_mm_yr")
            or record.get("vel_up_mm_yr")
            or record.get("vel_u_mm_yr")
            or record.get("up_mm_yr")
            or record.get("u_mm_yr")
        )

        vel_e_res = _to_float(
            record.get("vel_e_res_mm_yr")
            or record.get("vel_e_residual_mm_yr")
        )

        vel_n_res = _to_float(
            record.get("vel_n_res_mm_yr")
            or record.get("vel_n_residual_mm_yr")
        )

        vel_u_res = _to_float(
            record.get("vel_u_res_mm_yr")
            or record.get("vel_u_residual_mm_yr")
        )

        if vel_e_abs is not None:
            properties["vel_e_abs_visual"] = vel_e_abs

        if vel_n_abs is not None:
            properties["vel_n_abs_visual"] = vel_n_abs

        if vel_u_abs is not None:
            properties["vel_u_abs_visual"] = vel_u_abs

        if vel_e_res is not None:
            properties["vel_e_res_visual"] = vel_e_res

        if vel_n_res is not None:
            properties["vel_n_res_visual"] = vel_n_res

        if vel_u_res is not None:
            properties["vel_u_res_visual"] = vel_u_res

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def points_to_geojson(data):
    return dataframe_to_geojson(data)


def grid_to_geojson(data):
    return dataframe_to_geojson(data)