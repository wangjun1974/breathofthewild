import { createMap } from "./map.js";
import { createMarkerLayer } from "./markers.js";
import { showKorokSheet, hideSheet, toast } from "./popup.js";
import {
  state,
  clearCollected,
  isCollected,
  matchesFilter,
} from "./state.js";

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

function updateProgress() {
  const total = state.koroks.length;
  const collected = state.koroks.filter((k) => isCollected(k.id)).length;
  const visible = state.koroks.filter(matchesFilter).length;
  const el = document.getElementById("progress-text");
  if (el) {
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

async function main() {
  showLoading("加载呀哈哈数据…");
  const map = createMap("map");
  const markers = createMarkerLayer(map);

  let data;
  try {
    const res = await fetch("./data/koroks.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (e) {
    removeLoading();
    toast(`数据加载失败：${e.message || e}`);
    throw e;
  }

  state.koroks = data.koroks || [];
  if (state.koroks.length !== 900) {
    console.warn("korok count", state.koroks.length);
  }

  function refresh() {
    markers.render();
    updateProgress();
  }

  window.onKorokClick = (k) => {
    state.selectedId = k.id;
    markers.refreshIcons();
    markers.zoomTo(k);
    showKorokSheet(k, { onToggle: refresh });
    updateProgress();
  };

  renderRegionChips(refresh);
  refresh();

  document.getElementById("only-uncollected")?.addEventListener("change", (e) => {
    state.onlyUncollected = !!e.target.checked;
    refresh();
  });

  document.getElementById("btn-reset-collected")?.addEventListener("click", () => {
    if (!confirm("确定清空所有已收集标记？")) return;
    clearCollected();
    refresh();
    if (state.selectedId) {
      const k = state.koroks.find((x) => x.id === state.selectedId);
      if (k) showKorokSheet(k, { onToggle: refresh });
    }
    toast("已重置收集状态");
  });

  document.getElementById("btn-close-sheet")?.addEventListener("click", () => {
    hideSheet();
    markers.refreshIcons();
  });
  document.getElementById("btn-close-sheet-top")?.addEventListener("click", () => {
    hideSheet();
    markers.refreshIcons();
  });

  // Close sheet on map drag start for cleaner mobile UX
  map.on("dragstart", () => {
    if (!document.getElementById("sheet")?.hidden) {
      // keep sheet open; user may pan while reading
    }
  });

  removeLoading();
  toast("已加载 900 个呀哈哈");
}

main().catch((e) => console.error(e));
