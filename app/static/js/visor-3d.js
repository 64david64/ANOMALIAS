document.addEventListener("DOMContentLoaded", () => {
    const plotElement = document.getElementById("plot3d");
    const selectElement = document.getElementById("surfaceColorVariable");
    const statusElement = document.getElementById("surfaceStatus");

    if (!plotElement || typeof Plotly === "undefined") {
        console.warn("Plotly no está disponible o no existe #plot3d.");
        return;
    }

    const VARIABLES = {
        bouguer_mgal: {
            label: "Anomalía de Bouguer",
            unit: "mGal",
            colorscale: "RdBu",
            reversescale: true
        },
        aire_libre_mgal: {
            label: "Anomalía de aire libre",
            unit: "mGal",
            colorscale: "RdBu",
            reversescale: true
        },
        gradiente_mgal_km: {
            label: "Gradiente horizontal",
            unit: "mGal/km",
            colorscale: "Hot",
            reversescale: false
        },
        altura_m: {
            label: "Altura",
            unit: "m",
            colorscale: "Earth",
            reversescale: false
        },
        gravity_anomaly_base_mgal: {
            label: "Anomalía base",
            unit: "mGal",
            colorscale: "RdBu",
            reversescale: true
        }
    };

    let gridRecords = [];
    let currentVariable = "bouguer_mgal";

    function toNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function uniqueSorted(values) {
        return [...new Set(values)]
            .filter(value => value !== null)
            .sort((a, b) => a - b);
    }

    function setStatus(message) {
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    function buildMatrix(records, xValues, yValues, field) {
        const matrix = yValues.map(() => xValues.map(() => null));
        const xIndex = new Map(xValues.map((value, index) => [value.toFixed(6), index]));
        const yIndex = new Map(yValues.map((value, index) => [value.toFixed(6), index]));

        records.forEach(row => {
            const lon = toNumber(row.lon || row.longitud);
            const lat = toNumber(row.lat || row.latitud);
            const value = toNumber(row[field]);

            if (lon === null || lat === null || value === null) return;

            const xi = xIndex.get(lon.toFixed(6));
            const yi = yIndex.get(lat.toFixed(6));

            if (xi === undefined || yi === undefined) return;

            matrix[yi][xi] = value;
        });

        return matrix;
    }

    function renderSurface() {
        if (!gridRecords.length) {
            plotElement.innerHTML = `
                <div class="loading-box">
                    <p>No se encontraron datos de grilla para el visor 3D.</p>
                </div>
            `;
            return;
        }

        const config = VARIABLES[currentVariable] || VARIABLES.bouguer_mgal;

        const lons = uniqueSorted(gridRecords.map(row => toNumber(row.lon || row.longitud)));
        const lats = uniqueSorted(gridRecords.map(row => toNumber(row.lat || row.latitud)));

        const z = buildMatrix(gridRecords, lons, lats, "altura_m");
        const surfaceColor = buildMatrix(gridRecords, lons, lats, currentVariable);

        const trace = {
            type: "surface",
            x: lons,
            y: lats,
            z: z,
            surfacecolor: surfaceColor,
            colorscale: config.colorscale,
            reversescale: config.reversescale,
            colorbar: {
                title: `${config.label}<br>${config.unit}`,
                thickness: 14,
                len: 0.72
            },
            hovertemplate:
                "Longitud: %{x:.4f}°<br>" +
                "Latitud: %{y:.4f}°<br>" +
                "Altura: %{z:.0f} m<br>" +
                `${config.label}: %{surfacecolor:.2f} ${config.unit}<extra></extra>`
        };

        const layout = {
            margin: { l: 0, r: 0, t: 12, b: 0 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            scene: {
                xaxis: { title: "Longitud [°]" },
                yaxis: { title: "Latitud [°]" },
                zaxis: { title: "Altura [m]" },
                aspectmode: "manual",
                aspectratio: {
                    x: 1.55,
                    y: 1.0,
                    z: 0.42
                },
                camera: {
                    eye: { x: 1.55, y: -1.65, z: 0.95 }
                }
            }
        };

        const configPlot = {
            responsive: true,
            displaylogo: false
        };

        Plotly.react(plotElement, [trace], layout, configPlot);
        setStatus(`Superficie cargada: ${config.label}.`);
    }

    fetch("/api/grilla?sample=1&max_rows=30000")
        .then(response => response.json())
        .then(payload => {
            gridRecords = payload.records || [];
            renderSurface();
        })
        .catch(error => {
            console.error("Error cargando grilla para 3D:", error);
            setStatus("No fue posible cargar la superficie 3D.");
            plotElement.innerHTML = `
                <div class="loading-box">
                    <p>No fue posible cargar la superficie 3D.</p>
                </div>
            `;
        });

    if (selectElement) {
        selectElement.addEventListener("change", () => {
            currentVariable = selectElement.value;
            renderSurface();
        });
    }

    window.addEventListener("resize", () => {
        if (plotElement && gridRecords.length) {
            Plotly.Plots.resize(plotElement);
        }
    });
});