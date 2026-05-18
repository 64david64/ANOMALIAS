document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("gnssStations");
    if (!container) return;

    function getValue(row, keys, fallback = "—") {
        for (const key of keys) {
            if (row[key] !== undefined && row[key] !== null && row[key] !== "") {
                return row[key];
            }
        }
        return fallback;
    }

    fetch("/api/gnss")
        .then((response) => response.json())
        .then((payload) => {
            const records = payload.records || [];
            container.innerHTML = "";

            if (!records.length) {
                container.innerHTML = "<p>No hay estaciones GNSS disponibles.</p>";
                return;
            }

            records.forEach((row) => {
                const station = getValue(row, ["estacion", "station", "nombre", "name"], "GNSS");
                const east = getValue(row, ["vel_e_residual_mm_yr", "vel_e_mm_yr"], "—");
                const north = getValue(row, ["vel_n_residual_mm_yr", "vel_n_mm_yr"], "—");
                const up = getValue(row, ["vel_u_mm_yr", "vel_up_mm_yr"], "—");

                const card = document.createElement("article");
                card.className = "station-chip";
                card.innerHTML = `
                    <strong>${station}</strong>
                    <span>Este: ${east} mm/año</span>
                    <span>Norte: ${north} mm/año</span>
                    <span>Up: ${up} mm/año</span>
                `;

                container.appendChild(card);
            });
        })
        .catch((error) => {
            console.error("Error cargando GNSS:", error);
            container.innerHTML = "<p>No fue posible cargar las estaciones GNSS.</p>";
        });
});