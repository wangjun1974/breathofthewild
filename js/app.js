import { createMap } from "./map.js?v=20260930-lm2";
import { createMarkerLayer } from "./markers.js?v=20260930-lm2";
import { createLandmarkLayers } from "./landmarks.js?v=20260930-lm2";
import { showKorokSheet, showLandmarkSheet, hideSheet, toast } from "./popup.js?v=20260930-lm2";
import {
  state,
  clearCollected,
  isCollected,
  matchesFilter,
  setHideKoroks,
  setHideShrines,
  setHideTowers,
} from "./state.js?v=20260930-lm2";
import { createOwnedStore } from "./owned.js?v=20260930-lm2";
import { createArmorUi } from "./armors.js?v=20260930-lm2";

const REGION_LABELS = [
  ["all", "全部"],
  ["plateau", "初始台地"],
  ["central", "中央"],
  ["castle", "城堡"],
  ["duelingpeaks", "双子山"],
  ["hateno", "哈特诺"],
  ["lanayru", "拉聂尔"],
  ["akkala", "阿卡拉"],
  ["faron", "费罗尼"],
  ["lake", "湖"],
  ["gerudo", "格鲁德"],
  ["ridgeland", "里脊"],
  ["tabantha", "塔邦达"],
  ["hebra", "赫布拉"],
  ["woodland", "迷途森林"],
  ["eldin", "奥尔汀"],
  ["wasteland", "荒野"],
];

let mode = "korok";
let map;
let markers;
let landmarks;
let armors;
const ownedStore = createOwnedStore();

function showLoading(text) {
  removeLoading();
  const el = document.createElement("div");
  el.className = "loading-overlay";
  el.id = "loading-overlay";
  el.textContent = text;
  document.getElementById("app")?.appendChild(el);
}

function removeLoading() {
  document.getElementById("loading-overlay")?.remove();
}

function syncHideClass() {
  document.body.classList.toggle(
    "hide-koroks",
    !!(state.hideKoroks || state.forceHideKoroks)
  );
}

function updateKorokProgress() {
  const total = state.koroks.length;
  const collected = state.koroks.filter((k) => isCollected(k.id)).length;
  const visible = state.koroks.filter(matchesFilter).length;
  const el = document.getElementById("progress-text");
  if (!el) return;
  if (state.hideKoroks || state.forceHideKoroks) {
    el.textContent = `呀哈哈已隐藏 · 已收集 ${collected}/${total}`;
  } else {
    el.textContent = `显示 ${visible} · 已收集 ${collected}/${total}`;
  }
}

function renderRegionChips(onChange) {
  const host = document.getElementById("region-chips");
  if (!host) return;
  const present = new Set(state.koroks.map((k) => k.region));
  host.innerHTML = "";
  for (const [key, label] of REGION_LABELS) {
    if (key !== "all" && !present.has(key)) continue;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip" + (state.region === key ? " active" : "");
    btn.textContent = label;
    btn.dataset.region = key;
    btn.addEventListener("click", () => {
      state.region = key;
      renderRegionChips(onChange);
      onChange();
    });
    host.appendChild(btn);
  }
}

function setMode(next) {
  mode = next;
  document.querySelectorAll(".mode-btn").forEach((btn) => {
    const active = btn.getAttribute("data-mode") === mode;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-selected", active ? "true" : "false");
  });

  const brand = document.getElementById("brand-title");
  const filters = document.getElementById("korok-filters");
  const armorPanel = document.getElementById("armor-panel");
  const armorBack = document.getElementById("armor-back-map");
  const resetBtn = document.getElementById("btn-reset-collected");
  const hideText = document.getElementById("hide-found-text");

  armors?.clearTempMarker();
  if (armorBack) armorBack.hidden = true;
  hideSheet();
  armors?.closeSheet();

  if (mode === "korok") {
    if (brand) brand.textContent = "呀哈哈地图";
    if (filters) filters.hidden = false;
    if (armorPanel) armorPanel.hidden = true;
    if (resetBtn) {
      resetBtn.hidden = false;
      resetBtn.textContent = "重置收集";
    }
    if (hideText) hideText.textContent = "仅未收集";
    document.body.classList.remove("mode-armor", "armor-locating");
    state.forceHideKoroks = false;
    syncHideClass();
    updateKorokProgress();
    markers?.render();
    landmarks?.render();
  } else {
    if (brand) brand.textContent = "套装图鉴";
    if (filters) filters.hidden = true;
    if (armorPanel) armorPanel.hidden = false;
    if (resetBtn) {
      resetBtn.hidden = true;
    }
    if (hideText) hideText.textContent = "隐藏已拥有";
    document.body.classList.add("mode-armor");
    document.body.classList.remove("armor-locating");
    state.forceHideKoroks = false;
    syncHideClass();
    const only = document.getElementById("only-uncollected");
    armors?.setHideOwned(!!only?.checked);
    armors?.renderList();
  }
}

async function main() {
  showLoading("加载数据…");
  map = createMap("map");
  markers = createMarkerLayer(map);
  landmarks = createLandmarkLayers(map);

  armors = createArmorUi({
    map,
    ownedStore,
    onLocate() {
      document.getElementById("armor-panel").hidden = true;
      document.getElementById("armor-back-map").hidden = false;
      document.body.classList.add("armor-locating");
      document.body.classList.remove("mode-armor");
      state.forceHideKoroks = true;
      syncHideClass();
      markers.render();
      landmarks.render();
      updateKorokProgress();
    },
    onBackToList() {
      document.getElementById("armor-panel").hidden = false;
      document.getElementById("armor-back-map").hidden = true;
      document.body.classList.add("mode-armor");
      document.body.classList.remove("armor-locating");
      state.forceHideKoroks = false;
      armors?.clearTempMarker();
      syncHideClass();
      markers.render();
      landmarks.render();
    },
  });

  let korokData;
  let armorData;
  let landmarkData;
  try {
    const [kRes, aRes, lRes] = await Promise.all([
      fetch("./data/koroks.json"),
      fetch("./data/armors.json"),
      fetch("./data/landmarks.json"),
    ]);
    if (!kRes.ok) throw new Error(`koroks HTTP ${kRes.status}`);
    if (!aRes.ok) throw new Error(`armors HTTP ${aRes.status}`);
    if (!lRes.ok) throw new Error(`landmarks HTTP ${lRes.status}`);
    korokData = await kRes.json();
    armorData = await aRes.json();
    landmarkData = await lRes.json();
  } catch (e) {
    removeLoading();
    toast(`数据加载失败：${e.message || e}`);
    throw e;
  }

  state.koroks = korokData.koroks || [];
  if (state.koroks.length !== 900) {
    console.warn("korok count", state.koroks.length);
  }
  state.shrines = landmarkData.shrines || [];
  state.towers = landmarkData.towers || [];
  console.info("[地标]", `${state.shrines.length} 神庙, ${state.towers.length} 希卡塔`);

  const meta = armors.load(armorData);
  console.info("[套装]", meta);

  function refreshKorok() {
    syncHideClass();
    markers.render();
    landmarks.render();
    updateKorokProgress();
  }

  window.onKorokClick = (k) => {
    if (mode !== "korok") return;
    state.selectedId = k.id;
    markers.refreshIcons();
    markers.zoomTo(k);
    showKorokSheet(k, { onToggle: refreshKorok });
    updateKorokProgress();
  };

  window.onShrineClick = (s) => {
    if (mode !== "korok") return;
    hideSheet();
    showLandmarkSheet(s, "shrine");
  };

  window.onTowerClick = (t) => {
    if (mode !== "korok") return;
    hideSheet();
    showLandmarkSheet(t, "tower");
  };

  renderRegionChips(refreshKorok);

  const hideKoroksEl = document.getElementById("hide-koroks");
  if (hideKoroksEl) {
    hideKoroksEl.checked = !!state.hideKoroks;
    const applyHide = () => {
      setHideKoroks(!!hideKoroksEl.checked);
      refreshKorok();
      toast(state.hideKoroks ? "已隐藏呀哈哈图标" : "已显示呀哈哈图标");
    };
    hideKoroksEl.addEventListener("change", applyHide);
    hideKoroksEl.addEventListener("input", applyHide);
  }

  const hideShrinesEl = document.getElementById("hide-shrines");
  if (hideShrinesEl) {
    hideShrinesEl.checked = !!state.hideShrines;
    const applyHide = () => {
      setHideShrines(!!hideShrinesEl.checked);
      landmarks.renderShrines();
      toast(state.hideShrines ? "已隐藏神庙图标" : "已显示神庙图标");
    };
    hideShrinesEl.addEventListener("change", applyHide);
    hideShrinesEl.addEventListener("input", applyHide);
  }

  const hideTowersEl = document.getElementById("hide-towers");
  if (hideTowersEl) {
    hideTowersEl.checked = !!state.hideTowers;
    const applyHide = () => {
      setHideTowers(!!hideTowersEl.checked);
      landmarks.renderTowers();
      toast(state.hideTowers ? "已隐藏希卡塔图标" : "已显示希卡塔图标");
    };
    hideTowersEl.addEventListener("change", applyHide);
    hideTowersEl.addEventListener("input", applyHide);
  }

  refreshKorok();

  document.getElementById("only-uncollected")?.addEventListener("change", (e) => {
    const checked = !!e.target.checked;
    if (mode === "korok") {
      state.onlyUncollected = checked;
      refreshKorok();
    } else {
      armors?.setHideOwned(checked);
    }
  });

  document.getElementById("btn-reset-collected")?.addEventListener("click", () => {
    if (mode !== "korok") return;
    if (!confirm("确定清空所有已收集标记？")) return;
    clearCollected();
    refreshKorok();
    if (state.selectedId) {
      const k = state.koroks.find((x) => x.id === state.selectedId);
      if (k) showKorokSheet(k, { onToggle: refreshKorok });
    }
    toast("已重置收集状态");
  });

  const closeSheet = () => {
    hideSheet();
    armors?.closeSheet();
    markers.refreshIcons();
  };
  document.getElementById("btn-close-sheet")?.addEventListener("click", closeSheet);
  document.getElementById("btn-close-sheet-top")?.addEventListener("click", closeSheet);

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => setMode(btn.getAttribute("data-mode")));
  });

  ownedStore.onChange(() => {
    if (mode === "armor") armors?.updateCount();
  });

  removeLoading();
  toast(`已加载 ${state.koroks.length} 呀哈哈 · ${state.shrines.length} 神庙 · ${state.towers.length} 塔 · ${meta.setCount || "?"} 套装`);
}

main().catch((e) => console.error(e));
