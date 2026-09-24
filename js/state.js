const STORAGE_KEY = "botw-korok-collected-v1";

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

export const state = {
  koroks: [],
  collected: readCollected(),
  region: "all",
  onlyUncollected: false,
  selectedId: null,
};

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
  if (state.region !== "all" && k.region !== state.region) return false;
  if (state.onlyUncollected && state.collected.has(k.id)) return false;
  return true;
}
