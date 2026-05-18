document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("profileList");
    const chart = document.getElementById("profileChart");

    if (!list || !chart || !window.Plotly) return;

    function renderProfile(profile) {
        const points = profile.points || [];

        const lon = points.map((p) => p.lon);
        const bouguer = points.map((p) => p.bouguer_mgal);
        const altura = points.map((p) => p.altura_m);
        const gradiente = points.map((p) => p.gradiente_mgal_km);

        const traces = [
            {
                x: lon,
                y: bouguer,
                name: "Bouguer [mGal]",
                type: "scatter",
                mode: "lines",
            },
            {
                x: lon,
                y: altura,
                name: "Altura [m]",
                type: "scatter",
                mode: "lines",
                yaxis: "y2",
            },
            {
                x: lon,
                y: gradiente,
                name: "Gradiente [mGal/km]",
                type: "scatter",
                mode: "lines",
            },
        ];

        const layout = {
            title: profile.name,
            xaxis: { title: "Longitud" },
            yaxis: { title: "Bouguer / Gradiente" },
            yaxis2: {
                title: "Altura [m]",
                overlaying: "y",
                side: "right",
            },
            margin: { l: 60, r: 60, t: 50, b: 60 },
            legend: { orientation: "h" },
        };

        Plotly.newPlot(chart, traces, layout, { responsive: true });
    }

    fetch("/api/perfiles")
        .then((response) => response.json())
        .then((profiles) => {
            list.innerHTML = "";

            if (!profiles.length) {
                chart.innerHTML = "<p>No hay perfiles disponibles.</p>";
                return;
            }

            profiles.forEach((profile, index) => {
                const button = document.createElement("button");
                button.className = "profile-btn";
                button.textContent = profile.name;

                if (index === 0) button.classList.add("active");

                button.addEventListener("click", () => {
                    document.querySelectorAll(".profile-btn").forEach((item) => {
                        item.classList.remove("active");
                    });
                    button.classList.add("active");
                    renderProfile(profile);
                });

                list.appendChild(button);
            });

            renderProfile(profiles[0]);
        })
        .catch((error) => {
            console.error("Error cargando perfiles:", error);
            chart.innerHTML = "<p>No fue posible cargar los perfiles.</p>";
        });
});