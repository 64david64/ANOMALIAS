document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("interpretationCards");
    if (!container) return;

    fetch("/api/interpretacion/cards")
        .then((response) => response.json())
        .then((cards) => {
            container.innerHTML = "";

            cards.forEach((card) => {
                const item = document.createElement("article");
                item.className = "interpretation-card";
                item.innerHTML = `
                    <h3>${card.title}</h3>
                    <p>${card.text}</p>
                `;

                container.appendChild(item);
            });
        })
        .catch((error) => {
            console.error("Error cargando interpretación:", error);
            container.innerHTML = "<p>No fue posible cargar las tarjetas de interpretación.</p>";
        });
});