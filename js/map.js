export const TILE_SIZE = 256;
export const MAP_SIZE = [24000, 20000];
export const MIN_ZOOM = 2;
export const MAX_ZOOM = 10;
export const DEFAULT_ZOOM = 3;
export const TILE_URL =
  "https://objmap.zeldamods.org/game_files/maptex/{z}/{x}/{y}.png";
export const BASE_IMAGE_URL =
  "https://objmap.zeldamods.org/game_files/maptex/base.png";

export function createMap(elementId) {
  const crs = L.Util.extend({}, L.CRS.Simple);
  crs.transformation = new L.Transformation(
    4 / TILE_SIZE,
    MAP_SIZE[0] / TILE_SIZE,
    4 / TILE_SIZE,
    MAP_SIZE[1] / TILE_SIZE
  );

  const map = L.map(elementId, {
    crs,
    minZoom: MIN_ZOOM,
    maxZoom: MAX_ZOOM,
    zoom: DEFAULT_ZOOM,
    zoomControl: false,
    attributionControl: false,
    maxBoundsViscosity: 1.0,
    preferCanvas: true,
    renderer: L.canvas({ padding: 0.5 }),
    tap: false,
  });

  const rc = {
    width: MAP_SIZE[0],
    height: MAP_SIZE[1],
    unproject(point) {
      return map.unproject(point, map.getZoom());
    },
    project(latlng) {
      return map.project(latlng, map.getZoom());
    },
  };

  const southWest = rc.unproject([0, rc.height]);
  const northEast = rc.unproject([rc.width, 0]);
  const bounds = new L.LatLngBounds(southWest, northEast);
  map.setMaxBounds(bounds.pad(0.05));

  const basePane = map.createPane("base").style;
  basePane.zIndex = "0";

  L.imageOverlay(BASE_IMAGE_URL, bounds, { pane: "base" }).addTo(map);

  L.tileLayer(TILE_URL, {
    maxNativeZoom: 7,
    maxZoom: MAX_ZOOM,
    bounds,
    pane: "base",
    keepBuffer: 2,
  }).addTo(map);

  L.control.zoom({ position: "bottomright" }).addTo(map);
  map.setView([0, 0], DEFAULT_ZOOM);
  return map;
}

export function xyzToLatLng(x, z) {
  return [z, x];
}
