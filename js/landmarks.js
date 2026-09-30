/**
 * Shrine and Sheikah Tower marker layers.
 * Similar to markers.js (koroks) but simpler — no collected state, just show/hide.
 */
import { state } from "./state.js?v=20260930-lm3";
import { xyzToLatLng } from "./map.js?v=20260930-lm3";

function shrineIcon() {
  return L.divIcon({
    className: "shrine-marker",
    html: '<span class="shrine-icon"></span>',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

function towerIcon() {
  return L.divIcon({
    className: "tower-marker",
    html: '<span class="tower-icon"></span>',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
}

export function createLandmarkLayers(map) {
  // --- Shrine layer ---
  const shrinePane = map.createPane("shrines");
  shrinePane.style.zIndex = "640";
  const shrineLayer = L.layerGroup();

  // --- Tower layer ---
  const towerPane = map.createPane("towers");
  towerPane.style.zIndex = "630";
  const towerLayer = L.layerGroup();

  function setPaneVisible(pane, visible) {
    pane.style.display = visible ? "" : "none";
    pane.style.visibility = visible ? "" : "hidden";
    pane.style.pointerEvents = visible ? "" : "none";
  }

  function matchesRegion(item) {
    if (state.region === "all") return true;
    return item.region === state.region;
  }

  function renderShrines() {
    shrineLayer.clearLayers();
    if (state.hideShrines || state.forceHideKoroks) {
      setPaneVisible(shrinePane, false);
      if (map.hasLayer(shrineLayer)) map.removeLayer(shrineLayer);
      return;
    }
    setPaneVisible(shrinePane, true);
    if (!map.hasLayer(shrineLayer)) shrineLayer.addTo(map);

    for (const s of state.shrines) {
      if (!matchesRegion(s)) continue;
      const marker = L.marker(xyzToLatLng(s.x, s.z), {
        icon: shrineIcon(),
        title: s.name,
        riseOnHover: true,
        pane: "shrines",
      });
      marker.on("click", () => {
        if (typeof window.onShrineClick === "function") {
          window.onShrineClick(s);
        }
      });
      marker.addTo(shrineLayer);
    }
  }

  function renderTowers() {
    towerLayer.clearLayers();
    if (state.hideTowers || state.forceHideKoroks) {
      setPaneVisible(towerPane, false);
      if (map.hasLayer(towerLayer)) map.removeLayer(towerLayer);
      return;
    }
    setPaneVisible(towerPane, true);
    if (!map.hasLayer(towerLayer)) towerLayer.addTo(map);

    for (const t of state.towers) {
      if (!matchesRegion(t)) continue;
      const marker = L.marker(xyzToLatLng(t.x, t.z), {
        icon: towerIcon(),
        title: t.nameZh || t.name,
        riseOnHover: true,
        pane: "towers",
      });
      marker.on("click", () => {
        if (typeof window.onTowerClick === "function") {
          window.onTowerClick(t);
        }
      });
      marker.addTo(towerLayer);
    }
  }

  return {
    renderShrines,
    renderTowers,
    render() {
      renderShrines();
      renderTowers();
    },
  };
}
