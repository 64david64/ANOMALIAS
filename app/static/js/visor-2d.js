document.addEventListener("DOMContentLoaded", () => {
    if (!window.L) {
        console.warn("Leaflet no está disponible.");
        return;
    }

    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    const map = L.map("map").setView([4.8, -74.5], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const layers = {
        gnss: L.layerGroup().addTo(map),
        gravityPoints: L.layerGroup(),
        grid: L.layerGroup(),
    };

    const layerGnss = document.getElementById("layer-gnss");
    const layerGravity = document.getElementById("layer-gravity-points");
    const layerGrid = document.getElementById("layer-grid");

    function getProp(props, keys, fallback = "") {
        for (const key of keys) {
            if (props[key] !== undefined && props[key] !== null && props[key] !== "") {
                return props[key];
            }
        }
        return fallback;
    }

    function popupFromProperties(title, props, keys) {
        const rows = keys.map(([label, candidates]) => {
            const value = getProp(props, candidates, "—");
            return `<div class="popup-row"><span>${label}</span><span>${value}</span></div>`;
        }).join("");

        return `<div><h3 class="popup-title">${title}</h3>${rows}</div>`;
    }

    function updateLayer(checkbox, layer) {
        if (!checkbox) return;

        if (checkbox.checked) {
            map.addLayer(layer);
        } else {
            map.removeLayer(layer);
        }
    }

    if (layerGnss) {
        layerGnss.addEventListener("change", () => updateLayer(layerGnss, layers.gnss));
    }

    if (layerGravity) {
        layerGravity.addEventListener("change", () => updateLayer(layerGravity, layers.gravityPoints));
    }

    if (layerGrid) {
        layerGrid.addEventListener("change", () => updateLayer(layerGrid, layers.grid));
    }

    fetch("/api/gnss/geojson")
        .then((response) => response.json())
        .then((geojson) => {
            const gnssLayer = L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, {
                        radius: 7,
                        color: "#073b46",
                        weight: 2,
                        fillColor: "#2a9d8f",
                        fillOpacity: 0.9,
                    });
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties || {};
                    const title = getProp(props, ["estacion", "station", "nombre", "name"], "Estación GNSS");

                    layer.bindPopup(
                        popupFromProperties(title, props, [
                            ["Vel. Este", ["vel_e_residual_mm_yr", "vel_e_mm_yr", "vel_e_visual"]],
                            ["Vel. Norte", ["vel_n_residual_mm_yr", "vel_n_mm_yr", "vel_n_visual"]],
                            ["Vel. Up", ["vel_u_mm_yr", "vel_up_mm_yr", "vel_u_visual"]],
                            ["Marco", ["marco", "reference_frame"]],
                        ])
                    );
                },
            });

            gnssLayer.addTo(layers.gnss);

            if (geojson.features && geojson.features.length > 0) {
                map.fitBounds(gnssLayer.getBounds(), { padding: [30, 30] });
            }
        })
        .catch((error) => console.error("Error cargando GNSS:", error));

    fetch("/api/puntos-gravimetricos/geojson?sample=3&max_rows=12000")
        .then((response) => response.json())
        .then((geojson) => {
            const pointsLayer = L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, {
                        radius: 3,
                        color: "#e76f51",
                        weight: 1,
                        fillColor: "#e76f51",
                        fillOpacity: 0.45,
                    });
                },
                onEachFeature: (feature, layer) => {
                    const props = feature.properties || {};
                    layer.bindPopup(
                        popupFromProperties("Punto gravimétrico", props, [
                            ["Bouguer", ["bouguer_mgal", "anomalia_bouguer_mgal"]],
                            ["Aire libre", ["aire_libre_mgal"]],
                            ["Distancia", ["dist_km", "distancia_km"]],
                            ["Clase", ["clase_distancia", "clase_proximidad"]],
                        ])
                    );
                },
            });

            pointsLayer.addTo(layers.gravityPoints);
            updateLayer(layerGravity, layers.gravityPoints);
        })
        .catch((error) => console.error("Error cargando puntos gravimétricos:", error));

    fetch("/api/grilla/geojson?sample=5&max_rows=8000")
        .then((response) => response.json())
        .then((geojson) => {
            const gridLayer = L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, {
                        radius: 2,
                        color: "#1d3557",
                        weight: 0,
                        fillColor: "#1d3557",
                        fillOpacity: 0.22,
                    });
                },
            });

            gridLayer.addTo(layers.grid);
            updateLayer(layerGrid, layers.grid);
        })
        .catch((error) => console.error("Error cargando grilla:", error));
});