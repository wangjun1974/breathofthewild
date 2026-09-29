/** Persist owned armor piece ids (separate from korok collected). */

const KEY = "botw-armor-owned-v1";

function loadMap() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) return {};
    const map = {};
    for (const id of arr) {
      if (typeof id === "string") map[id] = true;
    }
    return map;
  } catch {
    return {};
  }
}

function saveMap(map) {
  try {
    localStorage.setItem(KEY, JSON.stringify(Object.keys(map)));
  } catch (e) {
    console.warn("[套装] 无法保存已拥有状态", e);
  }
}

export function createOwnedStore() {
  const owned = loadMap();
  const listeners = [];

  function notify() {
    for (const fn of listeners) {
      try {
        fn();
      } catch {
        /* ignore */
      }
    }
  }

  return {
    isOwned(id) {
      return !!owned[id];
    },
    setOwned(id, value) {
      if (value) owned[id] = true;
      else delete owned[id];
      saveMap(owned);
      notify();
    },
    count() {
      return Object.keys(owned).length;
    },
    onChange(fn) {
      listeners.push(fn);
    },
  };
}
