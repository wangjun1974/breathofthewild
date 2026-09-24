import { state, isCollected, toggleCollected } from "./state.js";

const sheet = () => document.getElementById("sheet");
const body = () => document.getElementById("sheet-body");

function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function hideSheet() {
  const el = sheet();
  if (el) el.hidden = true;
  const topBtn = document.getElementById("btn-close-sheet-top");
  if (topBtn) topBtn.hidden = true;
  state.selectedId = null;
}

export function showKorokSheet(k, { onToggle } = {}) {
  const collected = isCollected(k.id);
  const el = sheet();
  const content = body();
  if (!el || !content) return;

  content.innerHTML = `
    <div class="badges">
      <span class="badge">${escapeHtml(k.id)}</span>
      <span class="badge">${escapeHtml(k.typeZh)}</span>
      <span class="badge ${collected ? "on" : "off"}">${
        collected ? "已收集" : "未收集"
      }</span>
    </div>
    <h2>${escapeHtml(k.regionZh)} · ${escapeHtml(k.mapUnit)}</h2>
    <div class="meta-grid">
      <div class="meta-item">
        <span class="label">坐标 X / Z</span>
        <span class="value">${k.x.toFixed(1)}, ${k.z.toFixed(1)}</span>
      </div>
      <div class="meta-item">
        <span class="label">海拔 Y</span>
        <span class="value">${k.y.toFixed(1)}</span>
      </div>
      <div class="meta-item">
        <span class="label">地图格</span>
        <span class="value">${escapeHtml(k.mapUnit)}</span>
      </div>
      <div class="meta-item">
        <span class="label">类型</span>
        <span class="value">${escapeHtml(k.type)} / ${escapeHtml(k.typeZh)}</span>
      </div>
      <div class="meta-item" style="grid-column: 1 / -1">
        <span class="label">最近地点</span>
        <span class="value">${
          k.nearest
            ? `${escapeHtml(k.nearest)}${
                k.nearestDist != null ? ` · ${Math.round(k.nearestDist)} 单位` : ""
              }`
            : "附近无明显地标"
        }</span>
      </div>
    </div>
    <div class="hint">${escapeHtml(k.hint)}</div>
    ${k.note ? `<div class="note">备注：${escapeHtml(k.note)}</div>` : ""}
    <div class="sheet-actions">
      <button type="button" class="btn primary" id="btn-toggle-collected">
        ${collected ? "取消已收集" : "标记已收集"}
      </button>
      <button type="button" class="btn" id="btn-copy-coords">复制坐标</button>
    </div>
  `;

  el.hidden = false;
  const topBtn = document.getElementById("btn-close-sheet-top");
  if (topBtn) topBtn.hidden = false;
  el.scrollTop = 0;

  content.querySelector("#btn-toggle-collected")?.addEventListener("click", () => {
    toggleCollected(k.id);
    showKorokSheet(k, { onToggle });
    onToggle?.(k);
  });

  content.querySelector("#btn-copy-coords")?.addEventListener("click", async () => {
    const text = `${k.x.toFixed(1)}, ${k.y.toFixed(1)}, ${k.z.toFixed(1)}`;
    try {
      await navigator.clipboard.writeText(text);
      toast("坐标已复制");
    } catch {
      toast(text);
    }
  });
}

let toastTimer = null;
export function toast(msg) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.hidden = true;
  }, 2200);
}
