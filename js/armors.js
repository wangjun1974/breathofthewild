import { xyzToLatLng } from "./map.js?v=20260930-lm1";
import { hideSheet, toast } from "./popup.js?v=20260930-lm1";

const SLOT_LABEL = { head: "头", body: "身", legs: "腿" };
const STAR_LABEL = { star1: "★", star2: "★★", star3: "★★★", star4: "★★★★" };

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatMats(mats) {
  if (!mats?.length) return "—";
  return mats
    .map((m) => `${m.item || m.name || m.id} ×${m.count}`)
    .join("、");
}

export function createArmorUi({ map, ownedStore, onLocate, onBackToList }) {
  let sets = [];
  let hideOwned = false;
  let query = "";
  let tempMarker = null;

  const listEl = () => document.getElementById("armor-list");
  const searchEl = () => document.getElementById("armor-search");
  const progressEl = () => document.getElementById("progress-text");
  const sheet = () => document.getElementById("sheet");
  const sheetBody = () => document.getElementById("sheet-body");

  function pieceOwnedCount(set) {
    let n = 0;
    for (const p of set.pieces || []) {
      if (ownedStore.isOwned(p.id)) n += 1;
    }
    return n;
  }

  function filteredSets() {
    const q = query.trim().toLowerCase();
    return sets.filter((s) => {
      if (hideOwned && pieceOwnedCount(s) >= (s.pieces || []).length) return false;
      if (!q) return true;
      if ((s.name || "").toLowerCase().includes(q)) return true;
      return (s.pieces || []).some((p) => (p.name || "").toLowerCase().includes(q));
    });
  }

  function updateCount() {
    const el = progressEl();
    if (!el) return;
    let totalPieces = 0;
    for (const s of sets) totalPieces += (s.pieces || []).length;
    el.textContent = `套装 ${filteredSets().length}/${sets.length} · 已有 ${ownedStore.count()}/${totalPieces}`;
  }

  function formatUpgrades(set) {
    const ups = set.upgrades;
    if (!set.upgradable || !ups) {
      return '<p class="armor-note">不可强化。</p>';
    }
    let html = '<ul class="armor-upgrades">';
    for (const key of ["star1", "star2", "star3", "star4"]) {
      if (!ups[key]) continue;
      html += `<li><strong>${STAR_LABEL[key]}</strong>：${escapeHtml(formatMats(ups[key]))}</li>`;
    }
    html += "</ul>";
    return html;
  }

  function clearTempMarker() {
    if (tempMarker) {
      map.removeLayer(tempMarker);
      tempMarker = null;
    }
  }

  function closeArmorSheet() {
    const el = sheet();
    if (el) el.hidden = true;
    const topBtn = document.getElementById("btn-close-sheet-top");
    if (topBtn) topBtn.hidden = true;
  }

  function locatePiece(piece) {
    const loc = piece.location;
    if (!loc) return;
    clearTempMarker();
    const ll = xyzToLatLng(loc.x, loc.z);
    tempMarker = L.marker(ll, {
      title: piece.name,
      icon: L.divIcon({
        className: "armor-pin",
        html: '<span class="armor-pin-dot"></span>',
        iconSize: [18, 18],
        iconAnchor: [9, 9],
      }),
    }).addTo(map);
    closeArmorSheet();
    onLocate?.(piece, loc);
    setTimeout(() => {
      map.invalidateSize();
      map.setView(ll, Math.max(map.getZoom(), 5), { animate: true });
    }, 50);
    toast(`${piece.name} · ${loc.label || "地图定位"}`);
  }

  function openSet(set) {
    const el = sheet();
    const body = sheetBody();
    if (!el || !body) return;

    hideSheet();

    const bonus = set.setBonus || {};
    let bonusText = bonus.level2 || "无";
    if (bonus.note) bonusText += `（${bonus.note}）`;

    const tags = [];
    if (set.amiibo) tags.push("amiibo");
    if (set.dlc) tags.push("DLC");
    if (!set.upgradable) tags.push("不可强化");

    let html = "";
    if (tags.length) {
      html += `<div class="badges">${tags
        .map((t) => `<span class="badge">${escapeHtml(t)}</span>`)
        .join("")}</div>`;
    }
    html += `<h2>${escapeHtml(set.name)}</h2>`;
    html += `<p class="armor-desc">${escapeHtml(set.description || "")}</p>`;
    html += `<div class="meta-grid">
      <div class="meta-item"><span class="label">套装效果</span><span class="value">${escapeHtml(bonusText)}</span></div>
      <div class="meta-item"><span class="label">可强化</span><span class="value">${set.upgradable ? "是（大精灵）" : "否"}</span></div>
    </div>`;

    html += '<section class="armor-pieces"><h3>部件</h3>';
    for (const p of set.pieces || []) {
      html += `<article class="armor-piece">`;
      html += `<header><strong>${escapeHtml(SLOT_LABEL[p.slot] || p.slot)} · ${escapeHtml(p.name)}</strong></header>`;
      if (p.defense?.length) {
        html += `<p class="armor-def">防御：${escapeHtml(p.defense.join(" → "))}</p>`;
      }
      if (p.effect) {
        html += `<p class="armor-effect">效果：${escapeHtml(p.effect)}</p>`;
      }
      html += `<p>${escapeHtml(p.howToGet || "暂无获取说明。")}</p>`;
      html += `<label class="owned-check"><input type="checkbox" data-owned="${escapeHtml(p.id)}"${
        ownedStore.isOwned(p.id) ? " checked" : ""
      } /> 已拥有</label>`;
      if (p.location) {
        html += `<button type="button" class="btn locate-btn" data-locate="${escapeHtml(p.id)}">在地图上显示</button>`;
      }
      html += "</article>";
    }
    html += "</section>";

    html += '<section class="armor-upgrade-block"><h3>升级材料</h3>';
    html += formatUpgrades(set);
    html +=
      '<p class="armor-note">在大精灵之泉强化；已解放的大精灵数量决定可强化星级上限。BotW 强化本身不额外收取卢比。</p>';
    html += "</section>";

    body.innerHTML = html;
    el.hidden = false;
    const topBtn = document.getElementById("btn-close-sheet-top");
    if (topBtn) topBtn.hidden = false;
    el.scrollTop = 0;

    body.querySelectorAll("[data-owned]").forEach((input) => {
      input.addEventListener("change", () => {
        ownedStore.setOwned(input.getAttribute("data-owned"), input.checked);
        renderList();
      });
    });
    body.querySelectorAll("[data-locate]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-locate");
        const piece = (set.pieces || []).find((p) => p.id === id);
        if (piece) locatePiece(piece);
      });
    });
  }

  function renderList() {
    const host = listEl();
    if (!host) return;
    host.innerHTML = "";
    const list = filteredSets();
    if (!list.length) {
      const empty = document.createElement("p");
      empty.className = "armor-empty";
      empty.textContent = "没有匹配的套装";
      host.appendChild(empty);
      updateCount();
      return;
    }
    for (const s of list) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "armor-item";
      const owned = pieceOwnedCount(s);
      const total = (s.pieces || []).length;
      const tags = [];
      if (s.amiibo) tags.push("amiibo");
      if (s.dlc) tags.push("DLC");
      if (!s.upgradable) tags.push("不可强化");
      btn.innerHTML = `<span class="armor-item-name">${escapeHtml(s.name)}</span>
        <span class="armor-item-meta">${owned}/${total}${
        tags.length ? " · " + tags.join(" · ") : ""
      }</span>`;
      btn.addEventListener("click", () => openSet(s));
      host.appendChild(btn);
    }
    updateCount();
  }

  searchEl()?.addEventListener("input", (e) => {
    query = e.target.value || "";
    renderList();
  });

  document.getElementById("armor-back-map")?.addEventListener("click", () => {
    clearTempMarker();
    onBackToList?.();
  });

  return {
    load(payload) {
      sets = payload?.sets || [];
      renderList();
      return payload?.meta || {};
    },
    renderList,
    setHideOwned(value) {
      hideOwned = !!value;
      renderList();
    },
    closeSheet: closeArmorSheet,
    clearTempMarker,
    updateCount,
  };
}
