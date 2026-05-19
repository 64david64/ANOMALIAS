document.addEventListener("DOMContentLoaded", () => {
    const cardsContainer = document.getElementById("interpretationCards");
    const rulesContainer = document.getElementById("interpretationRules");

    if (!cardsContainer && !rulesContainer) return;

    function fallbackCards() {
        return [
            {
                kicker: "Gravedad",
                title: "Anomalías gravimétricas",
                text: "Permiten observar diferencias entre el campo gravitatorio real y un modelo de referencia.",
                bullets: [
                    "Aire libre: corrige principalmente el efecto de la altura.",
                    "Bouguer: incorpora el efecto de la masa topográfica.",
                    "La interpretación es regional."
                ]
            },
            {
                kicker: "Contrastes",
                title: "Gradiente horizontal",
                text: "Resalta zonas donde la anomalía de Bouguer cambia rápidamente.",
                bullets: [
                    "Identifica cambios espaciales fuertes.",
                    "Sugiere áreas de interés estructural.",
                    "No confirma fallas activas por sí solo."
                ]
            },
            {
                kicker: "Geodesia",
                title: "Velocidades GNSS",
                text: "Representan cambios de posición durante una serie temporal.",
                bullets: [
                    "Se expresan en mm/año.",
                    "Se interpretan en IGS20 / ITRF2020.",
                    "Funcionan como referencia cinemática regional."
                ]
            },
            {
                kicker: "Integración",
                title: "Relación contextual",
                text: "La relación gravedad-GNSS se interpreta por proximidad espacial.",
                bullets: [
                    "No hay asociación directa punto-estación.",
                    "La coincidencia espacial orienta la interpretación.",
                    "Se requiere contraste geológico adicional."
                ]
            }
        ];
    }

    function fallbackRules() {
        return [
            {
                title: "No declarar fallas activas sin contraste",
                text: "Las zonas de alto gradiente se presentan como lineamientos potenciales."
            },
            {
                title: "No asociar directamente gravedad y GNSS",
                text: "Ambos insumos se integran por superposición espacial y proximidad contextual."
            },
            {
                title: "Interpretar a escala regional",
                text: "El visor tiene propósito académico y pedagógico."
            }
        ];
    }

    function renderCards(cards) {
        if (!cardsContainer) return;

        cardsContainer.innerHTML = cards.map((card) => `
            <article class="interpretation-info-card">
                <span>${card.kicker || "Lectura"}</span>
                <h3>${card.title || "Componente interpretativo"}</h3>
                <p>${card.text || ""}</p>

                ${
                    Array.isArray(card.bullets)
                        ? `<ul>${card.bullets.map(item => `<li>${item}</li>`).join("")}</ul>`
                        : ""
                }
            </article>
        `).join("");
    }

    function renderRules(rules) {
        if (!rulesContainer) return;

        rulesContainer.innerHTML = rules.map((rule) => `
            <article class="interpretation-rule-card">
                <h3>${rule.title || "Criterio de interpretación"}</h3>
                <p>${rule.text || ""}</p>
            </article>
        `).join("");
    }

    fetch("/api/interpretacion")
        .then((response) => {
            if (!response.ok) {
                throw new Error("No se pudo consultar /api/interpretacion");
            }
            return response.json();
        })
        .then((payload) => {
            const cards = Array.isArray(payload)
                ? payload
                : (payload.cards || fallbackCards());

            const rules = payload.rules || fallbackRules();

            renderCards(cards);
            renderRules(rules);
        })
        .catch((error) => {
            console.warn("Usando contenido local de interpretación:", error);
            renderCards(fallbackCards());
            renderRules(fallbackRules());
        });
});