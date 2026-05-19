document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("map");

    if (!mapElement || typeof L === "undefined") {
        console.warn("Leaflet no está disponible o no se encontró #map.");
        return;
    }

    const map = L.map("map", {
        center: [4.8, -74.3],
        zoom: 6,
        zoomControl: true,
        preferCanvas: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    setTimeout(() => map.invalidateSize(), 300);
    window.addEventListener("resize", () => map.invalidateSize());

    const statusBox = document.getElementById("mapStatus");

    function setStatus(message) {
        if (statusBox) statusBox.textContent = message;
    }

    function toNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function formatNumber(value, decimals = 2) {
        const number = toNumber(value);
        if (number === null) return "—";
        return number.toFixed(decimals);
    }

    function getValue(row, keys, fallback = "") {
        for (const key of keys) {
            if (row[key] !== undefined && row[key] !== null && row[key] !== "") {
                return row[key];
            }
        }
        return fallback;
    }

    const GRID_VARIABLES = {
        gradiente_mgal_km: {
            label: "Gradiente horizontal",
            unit: "mGal/km",
            decimals: 2,
            description: "Resalta zonas donde la anomalía de Bouguer cambia rápidamente. Es útil para identificar posibles lineamientos gravimétricos.",
            colors: ["#2b1a3f", "#d7191c", "#fdae61", "#ffffbf"]
        },
        bouguer_mgal: {
            label: "Anomalía de Bouguer",
            unit: "mGal",
            decimals: 1,
            description: "Representa contrastes gravimétricos corregidos por altura y masa topográfica. Se interpreta como apoyo regional para cambios de densidad cortical.",
            colors: ["#d7191c", "#f7f7f7", "#2c7bb6"]
        },
        aire_libre_mgal: {
            label: "Anomalía de aire libre",
            unit: "mGal",
            decimals: 1,
            description: "Corrige principalmente el efecto de la altura del punto de observación sobre la gravedad medida.",
            colors: ["#d7191c", "#f7f7f7", "#2c7bb6"]
        },
        altura_m: {
            label: "Altura",
            unit: "m",
            decimals: 0,
            description: "Representa la altura del terreno usada como variable de apoyo para comparar topografía y anomalías gravimétricas.",
            colors: ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#8c510a"]
        },
        gravity_anomaly_base_mgal: {
            label: "Anomalía base",
            unit: "mGal",
            decimals: 1,
            description: "Variable gravimétrica base de entrada antes de visualizar las anomalías derivadas del procesamiento.",
            colors: ["#d7191c", "#f7f7f7", "#2c7bb6"]
        }
    };

    let gridRecords = [];
    let gravityPointRecords = [];
    let currentGridVariable = "gradiente_mgal_km";

    const gnssLayer = L.layerGroup().addTo(map);
    const vectorLayer = L.layerGroup().addTo(map);
    const gravityLayer = L.layerGroup();
    const gridLayer = L.layerGroup();

    const gridCheckbox = document.getElementById("layer-grid");
    const gnssCheckbox = document.getElementById("layer-gnss");
    const vectorCheckbox = document.getElementById("layer-vectors");
    const gravityCheckbox = document.getElementById("layer-gravity-points");
    const gridVariableSelect = document.getElementById("gridVariableSelect");

    function percentile(values, p) {
        if (!values.length) return null;

        const sorted = [...values].sort((a, b) => a - b);
        const index = (p / 100) * (sorted.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);

        if (lower === upper) return sorted[lower];

        return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
    }

    function hexToRgb(hex) {
        const clean = hex.replace("#", "");
        return {
            r: parseInt(clean.substring(0, 2), 16),
            g: parseInt(clean.substring(2, 4), 16),
            b: parseInt(clean.substring(4, 6), 16)
        };
    }

    function rgbToHex(r, g, b) {
        return "#" + [r, g, b]
            .map(x => Math.round(x).toString(16).padStart(2, "0"))
            .join("");
    }

    function interpolateColor(colorA, colorB, t) {
        const a = hexToRgb(colorA);
        const b = hexToRgb(colorB);

        return rgbToHex(
            a.r + (b.r - a.r) * t,
            a.g + (b.g - a.g) * t,
            a.b + (b.b - a.b) * t
        );
    }

    function getColor(value, min, max, colors) {
        if (value === null || min === null || max === null || min === max) {
            return "#94a3b8";
        }

        const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
        const segments = colors.length - 1;
        const position = t * segments;
        const index = Math.min(Math.floor(position), segments - 1);
        const localT = position - index;

        return interpolateColor(colors[index], colors[index + 1], localT);
    }

    function getGridStats(variable) {
        const values = gridRecords
            .map(row => toNumber(row[variable]))
            .filter(value => value !== null);

        if (!values.length) {
            return { min: null, max: null };
        }

        return {
            min: percentile(values, 2),
            max: percentile(values, 98)
        };
    }

    function updateGridLegend(variable, min, max) {
        const config = GRID_VARIABLES[variable];
        const legendMin = document.getElementById("legendMin");
        const legendMax = document.getElementById("legendMax");
        const gradient = document.querySelector(".legend-gradient");
        const info = document.getElementById("gridVariableInfo");

        if (!config) return;

        if (gradient) {
            gradient.style.background = `linear-gradient(90deg, ${config.colors.join(", ")})`;
        }

        if (legendMin) {
            legendMin.textContent = min !== null
                ? `${min.toFixed(config.decimals)} ${config.unit}`
                : "mín";
        }

        if (legendMax) {
            legendMax.textContent = max !== null
                ? `${max.toFixed(config.decimals)} ${config.unit}`
                : "máx";
        }

        if (info) {
            info.textContent = config.description;
        }
    }

    function renderGridLayer() {
        gridLayer.clearLayers();

        const config = GRID_VARIABLES[currentGridVariable];
        if (!config || !gridRecords.length) return;

        const { min, max } = getGridStats(currentGridVariable);

        gridRecords.forEach(row => {
            const lat = toNumber(row.lat || row.latitud);
            const lon = toNumber(row.lon || row.longitud);
            const value = toNumber(row[currentGridVariable]);

            if (lat === null || lon === null || value === null) return;

            const color = getColor(value, min, max, config.colors);

            const marker = L.circleMarker([lat, lon], {
                radius: 3.2,
                stroke: false,
                fillColor: color,
                fillOpacity: 0.72
            });

            marker.bindPopup(`
                <div class="popup-title">${config.label}</div>
                <div class="popup-row"><span>Valor</span><span>${value.toFixed(config.decimals)} ${config.unit}</span></div>
                <div class="popup-row"><span>Latitud</span><span>${lat.toFixed(4)}</span></div>
                <div class="popup-row"><span>Longitud</span><span>${lon.toFixed(4)}</span></div>
            `);

            marker.addTo(gridLayer);
        });

        updateGridLegend(currentGridVariable, min, max);
    }

    function renderGravityPoints() {
        gravityLayer.clearLayers();

        gravityPointRecords.forEach(row => {
            const lat = toNumber(row.lat || row.latitud);
            const lon = toNumber(row.lon || row.longitud);
            const station = getValue(row, ["estacion_gnss_retenida", "estacion"], "Sin estación");
            const dist = toNumber(getValue(row, ["dist_gnss_km"], null));
            const clase = getValue(row, ["clase_distancia"], "Contextual");

            if (lat === null || lon === null) return;

            const marker = L.circleMarker([lat, lon], {
                radius: 3,
                color: "#e76f51",
                fillColor: "#e76f51",
                fillOpacity: 0.55,
                weight: 1
            });

            marker.bindPopup(`
                <div class="popup-title">Punto gravimétrico</div>
                <div class="popup-row"><span>Estación contextual</span><span>${station}</span></div>
                <div class="popup-row"><span>Distancia GNSS</span><span>${dist !== null ? dist.toFixed(1) + " km" : "—"}</span></div>
                <div class="popup-row"><span>Clase</span><span>${clase}</span></div>
                <p class="popup-note">Relación contextual por proximidad, no asociación directa.</p>
            `);

            marker.addTo(gravityLayer);
        });
    }

    function drawGnssVector(lat, lon, velE, velN, name) {
        if (velE === null || velN === null) return;

        const scale = 0.015;
        const endLat = lat + velN * scale;
        const endLon = lon + velE * scale;

        const line = L.polyline([[lat, lon], [endLat, endLon]], {
            color: "#e76f51",
            weight: 3,
            opacity: 0.9
        });

        const arrow = L.circleMarker([endLat, endLon], {
            radius: 4,
            color: "#e76f51",
            fillColor: "#e76f51",
            fillOpacity: 1,
            weight: 1
        });

        line.bindPopup(`
            <div class="popup-title">Vector GNSS residual · ${name}</div>
            <div class="popup-row"><span>Este residual</span><span>${velE.toFixed(2)} mm/año</span></div>
            <div class="popup-row"><span>Norte residual</span><span>${velN.toFixed(2)} mm/año</span></div>
        `);

        line.addTo(vectorLayer);
        arrow.addTo(vectorLayer);
    }

    function loadGnss() {
        return fetch("/api/gnss")
            .then(response => response.json())
            .then(payload => {
                const records = payload.records || [];

                records.forEach(row => {
                    const name = getValue(row, ["estacion", "station", "nombre", "codigo"], "Estación GNSS");
                    const lat = toNumber(getValue(row, ["lat", "latitud"], null));
                    const lon = toNumber(getValue(row, ["lon", "longitud"], null));

                    if (lat === null || lon === null) return;

                    const velEAbs = toNumber(row.vel_e_abs_mm_yr);
                    const velNAbs = toNumber(row.vel_n_abs_mm_yr);
                    const velUAbs = toNumber(row.vel_u_abs_mm_yr);

                    const velERes = toNumber(row.vel_e_res_mm_yr);
                    const velNRes = toNumber(row.vel_n_res_mm_yr);

                    const marker = L.circleMarker([lat, lon], {
                        radius: 7,
                        color: "#0f4c5c",
                        fillColor: "#0f4c5c",
                        fillOpacity: 0.92,
                        weight: 2
                    });

                    marker.bindPopup(`
                        <div class="popup-title">${name}</div>
                        <div class="popup-row"><span>Marco</span><span>IGS20 / ITRF2020</span></div>
                        <div class="popup-row"><span>Vel. Este</span><span>${formatNumber(velEAbs)} mm/año</span></div>
                        <div class="popup-row"><span>Vel. Norte</span><span>${formatNumber(velNAbs)} mm/año</span></div>
                        <div class="popup-row"><span>Vel. Up</span><span>${formatNumber(velUAbs)} mm/año</span></div>
                        <p class="popup-note">Estación GNSS retenida para lectura cinemática regional.</p>
                    `);

                    marker.addTo(gnssLayer);
                    drawGnssVector(lat, lon, velERes, velNRes, name);
                });
            });
    }

    function loadGrid() {
        return fetch("/api/grilla")
            .then(response => response.json())
            .then(payload => {
                gridRecords = payload.records || [];
                renderGridLayer();

                if (gridCheckbox && gridCheckbox.checked) {
                    gridLayer.addTo(map);
                }
            });
    }

    function loadGravityPoints() {
        return fetch("/api/puntos-gravimetricos")
            .then(response => response.json())
            .then(payload => {
                gravityPointRecords = payload.records || [];
                renderGravityPoints();

                if (gravityCheckbox && gravityCheckbox.checked) {
                    gravityLayer.addTo(map);
                }
            });
    }

    if (gnssCheckbox) {
        gnssCheckbox.addEventListener("change", () => {
            if (gnssCheckbox.checked) {
                gnssLayer.addTo(map);
            } else {
                map.removeLayer(gnssLayer);
            }
        });
    }

    if (vectorCheckbox) {
        vectorCheckbox.addEventListener("change", () => {
            if (vectorCheckbox.checked) {
                vectorLayer.addTo(map);
            } else {
                map.removeLayer(vectorLayer);
            }
        });
    }

    if (gravityCheckbox) {
        gravityCheckbox.addEventListener("change", () => {
            if (gravityCheckbox.checked) {
                gravityLayer.addTo(map);
            } else {
                map.removeLayer(gravityLayer);
            }
        });
    }

    if (gridCheckbox) {
        gridCheckbox.addEventListener("change", () => {
            if (gridCheckbox.checked) {
                renderGridLayer();
                gridLayer.addTo(map);
            } else {
                map.removeLayer(gridLayer);
            }
        });
    }

    if (gridVariableSelect) {
        gridVariableSelect.value = currentGridVariable;

        gridVariableSelect.addEventListener("change", () => {
            currentGridVariable = gridVariableSelect.value;
            renderGridLayer();

            if (gridCheckbox && gridCheckbox.checked && !map.hasLayer(gridLayer)) {
                gridLayer.addTo(map);
            }
        });
    }

    Promise.all([
        loadGnss(),
        loadGrid(),
        loadGravityPoints()
    ])
        .then(() => {
            setStatus("Capas cargadas correctamente.");
            map.invalidateSize();
        })
        .catch(error => {
            console.error("Error cargando capas del visor 2D:", error);
            setStatus("Algunas capas no pudieron cargarse. Revisa las rutas API.");
        });
});