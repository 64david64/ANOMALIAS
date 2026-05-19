document.addEventListener("DOMContentLoaded", () => {
    const cardsContainer = document.getElementById("gnssCards");
    const tableBody = document.getElementById("gnssTableBody");

    if (!cardsContainer && !tableBody) return;

    const stationDescriptions = {
        BER1: {
            entorno: "Estación GNSS retenida para análisis regional.",
            descripcion: "Punto de control geodésico para contraste cinemático regional."
        },
        MEDE: {
            entorno: "Estación asociada al entorno de Medellín.",
            descripcion: "Referencia para observar comportamiento relativo en el sector noroccidental del área de estudio."
        },
        NEV1: {
            entorno: "Estación asociada al entorno de Neiva.",
            descripcion: "Referencia para observar comportamiento relativo en el sector sur del área de estudio."
        },
        PER2: {
            entorno: "Estación asociada al entorno de Pereira / eje cafetero.",
            descripcion: "Referencia para comparar velocidades GNSS con contrastes gravimétricos andinos."
        },
        TUNA: {
            entorno: "Estación asociada al entorno de Tunja.",
            descripcion: "Referencia para observar comportamiento relativo en el sector centro-oriental."
        },
        VIVI: {
            entorno: "Estación asociada al entorno de Villavicencio.",
            descripcion: "Referencia para evaluar el cambio entre el piedemonte y la zona oriental."
        }
    };

    function getValue(row, keys, fallback = "") {
        for (const key of keys) {
            if (row[key] !== undefined && row[key] !== null && row[key] !== "") {
                return row[key];
            }
        }
        return fallback;
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

    function normalizeStation(row) {
        const name = getValue(row, ["estacion", "station", "nombre", "codigo", "name"], "Sin código");

        const info = stationDescriptions[name] || {
            entorno: "Estación GNSS retenida para análisis regional.",
            descripcion: "Estación usada como referencia cinemática dentro del visor."
        };

        return {
            name,
            lat: toNumber(getValue(row, ["lat", "latitud", "station_lat", "gnss_lat"], null)),
            lon: toNumber(getValue(row, ["lon", "longitud", "station_lon", "gnss_lon"], null)),
            altura: toNumber(getValue(row, ["altura_m", "altura", "h_m"], null)),
            marco: getValue(row, ["marco_referencia"], "IGS20 / ITRF2020"),

            duracion: toNumber(getValue(row, ["duracion_yr", "duration_yr", "duracion_anios"], null)),

            velEAbs: toNumber(getValue(row, ["vel_e_abs_mm_yr"], null)),
            velNAbs: toNumber(getValue(row, ["vel_n_abs_mm_yr"], null)),
            velUAbs: toNumber(getValue(row, ["vel_u_abs_mm_yr"], null)),
            velHAbs: toNumber(getValue(row, ["vel_horizontal_abs_mm_yr"], null)),

            velERes: toNumber(getValue(row, ["vel_e_res_mm_yr"], null)),
            velNRes: toNumber(getValue(row, ["vel_n_res_mm_yr"], null)),
            velURes: toNumber(getValue(row, ["vel_u_res_mm_yr"], null)),
            velHRes: toNumber(getValue(row, ["vel_horizontal_res_mm_yr"], null)),

            distMed: toNumber(getValue(row, ["dist_med_km"], null)),
            claseContexto: getValue(row, ["clase_contexto_espacial"], "Contextual"),

            entorno: info.entorno,
            descripcion: info.descripcion
        };
    }

    function renderCards(stations) {
        if (!cardsContainer) return;

        if (!stations.length) {
            cardsContainer.innerHTML = `
                <div class="content-card">
                    <p>No se encontraron estaciones GNSS retenidas.</p>
                </div>
            `;
            return;
        }

        cardsContainer.innerHTML = stations.map((station) => `
            <article class="gnss-card">
                <div class="gnss-card-header">
                    <span class="station-code">${station.name}</span>
                    <span class="station-frame">${station.marco}</span>
                </div>

                <h3>${station.name}</h3>
                <p>${station.entorno}</p>

                <div class="gnss-metrics">
                    <div>
                        <span>Este</span>
                        <strong>${formatNumber(station.velEAbs)}</strong>
                        <small>mm/año</small>
                    </div>
                    <div>
                        <span>Norte</span>
                        <strong>${formatNumber(station.velNAbs)}</strong>
                        <small>mm/año</small>
                    </div>
                    <div>
                        <span>Up</span>
                        <strong>${formatNumber(station.velUAbs)}</strong>
                        <small>mm/año</small>
                    </div>
                </div>

                <div class="gnss-context">
                    <p>${station.descripcion}</p>
                    <p>
                        <strong>Vel. horizontal:</strong> ${formatNumber(station.velHAbs)} mm/año
                        ${station.duracion !== null ? ` · <strong>Duración:</strong> ${formatNumber(station.duracion, 2)} años` : ""}
                    </p>
                </div>
            </article>
        `).join("");
    }

    function renderTable(stations) {
        if (!tableBody) return;

        tableBody.innerHTML = stations.map((station) => `
            <tr>
                <td><strong>${station.name}</strong></td>
                <td>${formatNumber(station.lat, 4)}</td>
                <td>${formatNumber(station.lon, 4)}</td>
                <td>${formatNumber(station.velEAbs)}</td>
                <td>${formatNumber(station.velNAbs)}</td>
                <td>${formatNumber(station.velUAbs)}</td>
                <td>${formatNumber(station.velHAbs)}</td>
            </tr>
        `).join("");
    }

    fetch("/api/gnss")
        .then((response) => response.json())
        .then((payload) => {
            const records = payload.records || [];
            const stations = records.map(normalizeStation);

            renderCards(stations);
            renderTable(stations);
        })
        .catch((error) => {
            console.error("Error cargando datos GNSS:", error);

            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="content-card">
                        <p>No fue posible cargar la información GNSS.</p>
                    </div>
                `;
            }
        });
});