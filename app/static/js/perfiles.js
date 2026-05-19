document.addEventListener("DOMContentLoaded", () => {
    const buttonsContainer = document.getElementById("profileButtons");
    const chartElement = document.getElementById("profileChart");
    const titleElement = document.getElementById("profileTitle");
    const subtitleElement = document.getElementById("profileSubtitle");
    const statusElement = document.getElementById("profileStatus");

    if (!buttonsContainer || !chartElement || typeof Plotly === "undefined") {
        console.warn("No se puede inicializar perfiles: falta contenedor o Plotly.");
        return;
    }

    let profiles = [];

    function setStatus(message) {
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    function toNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function cleanPoints(points) {
        return (points || [])
            .map(point => ({
                lon: toNumber(point.lon),
                lat: toNumber(point.lat),
                bouguer: toNumber(point.bouguer_mgal),
                aireLibre: toNumber(point.aire_libre_mgal),
                gradiente: toNumber(point.gradiente_mgal_km),
                altura: toNumber(point.altura_m)
            }))
            .filter(point => point.lon !== null)
            .sort((a, b) => a.lon - b.lon);
    }

    function renderButtons() {
        if (!profiles.length) {
            buttonsContainer.innerHTML = `
                <button class="profile-btn" disabled>No hay perfiles disponibles</button>
            `;
            return;
        }

        buttonsContainer.innerHTML = profiles.map((profile, index) => `
            <button class="profile-btn ${index === 0 ? "active" : ""}" data-profile-index="${index}">
                ${profile.name}
            </button>
        `).join("");

        buttonsContainer.querySelectorAll(".profile-btn").forEach(button => {
            button.addEventListener("click", () => {
                const index = Number(button.dataset.profileIndex);

                buttonsContainer.querySelectorAll(".profile-btn")
                    .forEach(item => item.classList.remove("active"));

                button.classList.add("active");
                renderProfile(index);
            });
        });
    }

    function renderProfile(index) {
        const profile = profiles[index];
        if (!profile) return;

        const points = cleanPoints(profile.points);

        if (!points.length) {
            chartElement.innerHTML = `
                <div class="loading-box">
                    <p>El perfil seleccionado no tiene puntos disponibles.</p>
                </div>
            `;
            setStatus("Perfil sin puntos disponibles.");
            return;
        }

        const lon = points.map(point => point.lon);
        const bouguer = points.map(point => point.bouguer);
        const altura = points.map(point => point.altura);
        const gradiente = points.map(point => point.gradiente);

        const traces = [
            {
                x: lon,
                y: bouguer,
                type: "scatter",
                mode: "lines",
                name: "Bouguer [mGal]",
                line: { width: 3 },
                yaxis: "y1",
                hovertemplate: "Lon: %{x:.4f}°<br>Bouguer: %{y:.2f} mGal<extra></extra>"
            },
            {
                x: lon,
                y: altura,
                type: "scatter",
                mode: "lines",
                name: "Altura [m]",
                line: { width: 3, dash: "dot" },
                yaxis: "y2",
                hovertemplate: "Lon: %{x:.4f}°<br>Altura: %{y:.0f} m<extra></extra>"
            },
            {
                x: lon,
                y: gradiente,
                type: "scatter",
                mode: "lines",
                name: "Gradiente [mGal/km]",
                line: { width: 2, dash: "dash" },
                yaxis: "y3",
                visible: "legendonly",
                hovertemplate: "Lon: %{x:.4f}°<br>Gradiente: %{y:.2f} mGal/km<extra></extra>"
            }
        ];

        const layout = {
            margin: { l: 62, r: 72, t: 24, b: 54 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(255,255,255,0.92)",
            hovermode: "x unified",
            legend: {
                orientation: "h",
                x: 0,
                y: 1.12
            },
            xaxis: {
                title: "Longitud [°]",
                showgrid: true,
                zeroline: false
            },
            yaxis: {
                title: "Anomalía de Bouguer [mGal]",
                side: "left",
                showgrid: true,
                zeroline: false
            },
            yaxis2: {
                title: "Altura [m]",
                overlaying: "y",
                side: "right",
                showgrid: false,
                zeroline: false
            },
            yaxis3: {
                title: "Gradiente [mGal/km]",
                overlaying: "y",
                side: "right",
                position: 0.97,
                showgrid: false,
                zeroline: false,
                visible: false
            }
        };

        Plotly.react(chartElement, traces, layout, {
            responsive: true,
            displaylogo: false
        });

        if (titleElement) {
            titleElement.textContent = profile.name;
        }

        if (subtitleElement) {
            subtitleElement.textContent =
                `Latitud objetivo: ${Number(profile.target_lat).toFixed(2)}° · ` +
                `Latitud usada: ${Number(profile.actual_lat).toFixed(4)}° · ` +
                `${points.length} puntos`;
        }

        setStatus("Perfil cargado correctamente.");
    }

    fetch("/api/perfiles")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(payload => {
            profiles = payload.profiles || [];

            renderButtons();

            if (profiles.length) {
                renderProfile(0);
                setStatus(payload.message || "Perfiles cargados correctamente.");
            } else {
                chartElement.innerHTML = `
                    <div class="loading-box">
                        <p>No se encontraron perfiles para visualizar.</p>
                    </div>
                `;
                setStatus(payload.message || "No se encontraron perfiles.");
            }
        })
        .catch(error => {
            console.error("Error cargando perfiles:", error);

            chartElement.innerHTML = `
                <div class="loading-box">
                    <p>No fue posible cargar los perfiles. Revisa la ruta /api/perfiles.</p>
                </div>
            `;

            setStatus("Error al cargar perfiles.");
        });

    window.addEventListener("resize", () => {
        if (chartElement && profiles.length) {
            Plotly.Plots.resize(chartElement);
        }
    });
});