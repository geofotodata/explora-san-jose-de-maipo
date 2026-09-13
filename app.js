const state = {
  places: [],
  routes: [],
  filter: "todos",
  search: "",
  favorites: new Set(readFavorites()),
};

function readFavorites() {
  try {
    const value = JSON.parse(localStorage.getItem("zoit-favorites") || "[]");
    return Array.isArray(value) ? value : [];
  } catch (error) {
    console.warn("No se pudieron recuperar los favoritos locales", error);
    return [];
  }
}

const palette = {
  maipo: "linear-gradient(135deg, #769784, #315d4e)",
  colorado: "linear-gradient(135deg, #9c806b, #4d443c)",
  yeso: "linear-gradient(135deg, #70a7b4, #345c69)",
  volcan: "linear-gradient(135deg, #978878, #495248)",
};

const categoryNames = {
  naturaleza: "Naturaleza",
  patrimonio: "Patrimonio",
  aventura: "Aventura",
  bienestar: "Bienestar",
};

const territoryNames = {
  maipo: "Valle del Maipo",
  colorado: "Valle del Colorado",
  yeso: "Valle del Yeso",
  volcan: "Valle del Volcán",
};

const symbols = { naturaleza: "⌁", patrimonio: "◇", aventura: "↗", bienestar: "≈" };

async function loadData() {
  try {
    const [placesResponse, routesResponse] = await Promise.all([
      fetch("data/places.json"),
      fetch("data/routes.json"),
    ]);
    if (!placesResponse.ok || !routesResponse.ok) throw new Error("No fue posible cargar los datos");
    state.places = await placesResponse.json();
    state.routes = await routesResponse.json();
    renderPlaces();
    renderRoutes();
  } catch (error) {
    document.querySelector("#place-grid").innerHTML = `<p class="empty-state">${error.message}. Recarga la página para intentar nuevamente.</p>`;
  }
}

function getVisiblePlaces() {
  const query = state.search.trim().toLocaleLowerCase("es");
  return state.places.filter((place) => {
    const categoryMatch = state.filter === "todos" || place.categories.includes(state.filter) || place.territory === state.filter;
    const searchMatch = !query || `${place.name} ${place.summary} ${territoryNames[place.territory]}`.toLocaleLowerCase("es").includes(query);
    return categoryMatch && searchMatch;
  });
}

function renderPlaces() {
  const grid = document.querySelector("#place-grid");
  const empty = document.querySelector("#empty-state");
  const places = getVisiblePlaces();
  empty.hidden = places.length > 0;
  grid.innerHTML = places.map((place) => `
    <article class="place-card">
      <div class="place-visual" style="--place-color:${palette[place.territory]}">
        <span class="place-badge">${categoryNames[place.categories[0]]}</span>
        <button class="favorite-button ${state.favorites.has(place.id) ? "saved" : ""}" type="button" data-favorite="${place.id}" aria-label="${state.favorites.has(place.id) ? "Quitar de favoritos" : "Guardar en favoritos"}" aria-pressed="${state.favorites.has(place.id)}">${state.favorites.has(place.id) ? "♥" : "♡"}</button>
        <span class="place-symbol" aria-hidden="true">${symbols[place.categories[0]]}</span>
      </div>
      <div class="place-body">
        <p class="place-meta">${territoryNames[place.territory]}</p>
        <h3>${place.name}</h3>
        <p>${place.summary}</p>
        <div class="place-footer">
          <span class="status">${place.status}</span>
          <button class="detail-button" type="button" data-place="${place.id}">Ver ficha →</button>
        </div>
      </div>
    </article>
  `).join("");
}

function renderRoutes() {
  document.querySelector("#route-list").innerHTML = state.routes.map((route, index) => `
    <article class="route-card">
      <span class="route-number">${String(index + 1).padStart(2, "0")}</span>
      <div><h3>${route.name}</h3><p>${route.summary}</p></div>
      <div class="route-stats">
        <span><strong>${route.duration}</strong>Duración</span>
        <span><strong>${route.distance}</strong>Distancia</span>
        <span><strong>${route.difficulty}</strong>Dificultad</span>
      </div>
    </article>
  `).join("");
}

function openPlace(id) {
  const place = state.places.find((item) => item.id === id);
  if (!place) return;
  const dialog = document.querySelector("#place-dialog");
  document.querySelector("#dialog-content").innerHTML = `
    <div class="dialog-hero" style="--dialog-color:${palette[place.territory]}">
      <div><p>${territoryNames[place.territory]}</p><h2 id="dialog-title">${place.name}</h2></div>
    </div>
    <div class="dialog-body">
      <p class="dialog-intro">${place.description}</p>
      <div class="dialog-facts">
        <div><small>Estado</small><strong>${place.status}</strong></div>
        <div><small>Duración sugerida</small><strong>${place.duration}</strong></div>
        <div><small>Dificultad</small><strong>${place.difficulty}</strong></div>
        <div><small>Temporada</small><strong>${place.season}</strong></div>
        <div><small>Accesibilidad</small><strong>${place.accessibility}</strong></div>
        <div><small>Conectividad</small><strong>${place.connectivity}</strong></div>
      </div>
      <h3>Antes de ir</h3>
      <ul>${place.before.map((item) => `<li>${item}</li>`).join("")}</ul>
      <h3>Visita responsable</h3>
      <ul>${place.responsible.map((item) => `<li>${item}</li>`).join("")}</ul>
      <p class="pilot-note"><strong>Contenido piloto:</strong> esta ficha es referencial y debe validarse con fuentes oficiales y responsables del lugar antes de su publicación definitiva.</p>
    </div>
  `;
  dialog.showModal();
  document.body.classList.add("dialog-open");
}

function toggleFavorite(id) {
  if (state.favorites.has(id)) state.favorites.delete(id);
  else state.favorites.add(id);
  try { localStorage.setItem("zoit-favorites", JSON.stringify([...state.favorites])); }
  catch (error) { console.warn("Los favoritos solo se conservarán durante esta sesión", error); }
  renderPlaces();
}

document.addEventListener("click", (event) => {
  const placeButton = event.target.closest("[data-place]");
  const favoriteButton = event.target.closest("[data-favorite]");
  const territoryLink = event.target.closest("[data-territory]");
  const quickFilter = event.target.closest("[data-quick-filter]");
  if (placeButton) openPlace(placeButton.dataset.place);
  if (favoriteButton) toggleFavorite(favoriteButton.dataset.favorite);
  if (territoryLink) setFilter(territoryLink.dataset.territory);
  if (quickFilter) setFilter(quickFilter.dataset.quickFilter);
});

function setFilter(filter) {
  state.filter = filter;
  document.querySelectorAll(".filter").forEach((button) => button.classList.toggle("active", button.dataset.filter === filter));
  renderPlaces();
}

document.querySelectorAll(".filter").forEach((button) => button.addEventListener("click", () => setFilter(button.dataset.filter)));
document.querySelector("#place-search").addEventListener("input", (event) => { state.search = event.target.value; renderPlaces(); });

const dialog = document.querySelector("#place-dialog");
document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
dialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));

const menuButton = document.querySelector(".menu-toggle");
const nav = document.querySelector("#main-nav");
menuButton?.addEventListener("click", () => {
  const expanded = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!expanded));
  nav.classList.toggle("open", !expanded);
});
nav?.addEventListener("click", () => { nav.classList.remove("open"); menuButton.setAttribute("aria-expanded", "false"); });

document.querySelector("#planner").addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const interest = data.get("interest");
  const duration = data.get("duration");
  const candidates = state.places.filter((place) => place.categories.includes(interest));
  const preferred = candidates.find((place) => duration === "medio-dia" ? place.duration.includes("hora") : true) || candidates[0];
  const result = document.querySelector("#planner-result");
  result.innerHTML = preferred
    ? `<strong>Orientación inicial:</strong> considera ${preferred.name}. ${preferred.summary} Revisa su ficha y confirma las condiciones antes de viajar.`
    : "Aún no contamos con una recomendación para esa combinación.";
  result.hidden = false;
});

function updateConnectionStatus() {
  if (!document.querySelector("#connection-text")) return;
  const online = navigator.onLine;
  document.querySelector("#connection-text").textContent = online ? "Con conexión" : "Modo sin conexión";
  document.querySelector("#connection-dot").style.background = online ? "#74bd86" : "#f0b755";
}
window.addEventListener("online", updateConnectionStatus);
window.addEventListener("offline", updateConnectionStatus);
updateConnectionStatus();

let deferredInstallPrompt;
const installButton = document.querySelector("#install-button");
window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  if (installButton) installButton.hidden = false;
});
installButton?.addEventListener("click", async () => {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  installButton.hidden = true;
});

if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("service-worker.js"));

loadData();
