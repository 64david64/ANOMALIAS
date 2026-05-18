document.addEventListener("DOMContentLoaded", () => {
    const plot = document.getElementById("plot3d");
    const select = document.getElementById("zVariable");

    if (!plot || !window.Plotly) return;

    let records = [];

    function toNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function render(variable) {
        const x = [];
        const y = [];
        const z = [];

        records.forEach((row) => {
            const lon = toNumber(row.lon || row.longitud || row.x || row.X);
            const lat = toNumber(row.lat || row.latitud || row.y || row.Y);
            const value = toNumber(row[variable]);

            if (lon !== null && lat !== null && value !== null) {
                x.push(lon);
                y.push(lat);
                z.push(value);
            }
        });

        const trace = {
            x,
            y,
            z,
            mode: "markers",
            type: "scatter3d",
            marker: {
                size: 3,
                color: z,
                opacity: 0.8,
                colorscale: "Viridis",
                showscale: true,
            },
        };

        const layout = {
            margin: { l: 0, r: 0, b: 0, t: 30 },
            scene: {
                xaxis: { title: "Longitud" },
                yaxis: { title: "Latitud" },
                zaxis: { title: variable },
            },
        };

        Plotly.newPlot(plot, [trace], layout, { responsive: true });
    }

    fetch("/api/grilla?sample=8&max_rows=6000")
        .then((response) => response.json())
        .then((payload) => {
            records = payload.records || [];
            render(select ? select.value : "bouguer_mgal");
        })
        .catch((error) => {
            console.error("Error cargando grilla 3D:", error);
            plot.innerHTML = "<p>No fue posible cargar la grilla para el visor 3D.</p>";
        });

    if (select) {
        select.addEventListener("change", () => render(select.value));
    }
});