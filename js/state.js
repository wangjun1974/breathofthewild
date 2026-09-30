const STORAGE_KEY = "botw-korok-collected-v1";
const HIDE_KEY = "botw-korok-hide-v1";
const HIDE_SHRINE_KEY = "botw-shrine-hide-v1";
const HIDE_TOWER_KEY = "botw-tower-hide-v1";

function readCollected() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw);
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}

function readBool(key, fallback = false) {
  try {
    const v = localStorage.getItem(key);
    if (v === null) return fallback;
    return v === "1";
  } catch {
    return fallback;
  }
}

export const state = {
  koroks: [],
  shrines: [],
  towers: [],
  collected: readCollected(),
  region: "all",
  onlyUncollected: false,
  hideKoroks: readBool(HIDE_KEY),
  hideShrines: readBool(HIDE_SHRINE_KEY),
  hideTowers: readBool(HIDE_TOWER_KEY),
  /** 套装定位等临时强制隐藏，不写入偏好 */
  forceHideKoroks: false,
  selectedId: null,
};

export function setHideKoroks(value) {
  state.hideKoroks = !!value;
  try {
    localStorage.setItem(HIDE_KEY, state.hideKoroks ? "1" : "0");
  } catch {
    /* ignore */
  }
}

export function setHideShrines(value) {
  state.hideShrines = !!value;
  try {
    localStorage.setItem(HIDE_SHRINE_KEY, state.hideShrines ? "1" : "0");
  } catch {
    /* ignore */
  }
}

export function setHideTowers(value) {
  state.hideTowers = !!value;
  try {
    localStorage.setItem(HIDE_TOWER_KEY, state.hideTowers ? "1" : "0");
  } catch {
    /* ignore */
  }
}

export function saveCollected() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.collected]));
  } catch {
    // private mode / non-browser: keep in-memory only
  }
}

export function isCollected(id) {
  return state.collected.has(id);
}

export function toggleCollected(id) {
  if (state.collected.has(id)) state.collected.delete(id);
  else state.collected.add(id);
  saveCollected();
}

export function clearCollected() {
  state.collected.clear();
  saveCollected();
}

export function matchesFilter(k) {
  if (state.hideKoroks || state.forceHideKoroks) return false;
  if (state.region !== "all" && k.region !== state.region) return false;
  if (state.onlyUncollected && state.collected.has(k.id)) return false;
  return true;
}
