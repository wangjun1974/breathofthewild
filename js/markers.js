import { state, matchesFilter, isCollected } from "./state.js";
import { xyzToLatLng } from "./map.js";

const ICON_URL = "./assets/korok.png";
const paneName = "koroks";

function makeIcon(k, selectedId) {
  const collected = isCollected(k.id);
  const selected = selectedId === k.id;
  const cls = ["korok-icon"];
  if (collected) cls.push("collected");
  if (selected) cls.push("selected");
  return L.divIcon({
    className: "korok-marker",
    html: `<span class="${cls.join(" ")}" data-id="${k.id}"></span>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

export function createMarkerLayer(map) {
  if (!map.getPane(paneName)) map.createPane(paneName);
  map.getPane(paneName).style.zIndex = "650";

  const layer = L.layerGroup();
  const byId = new Map();

  function render() {
    layer.clearLayers();
    byId.clear();
    for (const k of state.koroks) {
      if (!matchesFilter(k)) continue;
      const marker = L.marker(xyzToLatLng(k.x, k.z), {
        icon: makeIcon(k, state.selectedId),
        title: `${k.id} ${k.typeZh}`,
        riseOnHover: true,
        keyboard: true,
        alt: k.id,
        pane: paneName,
      });
      marker.on("click", () => {
        if (typeof window.onKorokClick === "function") {
          window.onKorokClick(k);
        }
      });
      marker.addTo(layer);
      byId.set(k.id, marker);
    }
  }

  layer.addTo(map);
  return {
    layer,
    render,
    refreshIcons() {
      for (const [id, marker] of byId) {
        const k = state.koroks.find((x) => x.id === id);
        if (k) marker.setIcon(makeIcon(k, state.selectedId));
      }
    },
    zoomTo(k) {
      map.setView(xyzToLatLng(k.x, k.z), Math.max(map.getZoom(), 7), {
        animate: true,
      });
    },
  };
}
