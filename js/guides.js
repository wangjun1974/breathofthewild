/**
 * guides.js — 攻略面板 UI
 * 支持「主线流程」和「试炼神庙」两种攻略，可搜索、展开详情。
 * 神庙攻略支持「在地图上显示」定位。
 */
import { xyzToLatLng } from "./map.js?v=20260930-g1";
import { toast } from "./popup.js?v=20260930-g1";

const CAT_COLOR = {
  puzzle:    { bg: "rgba(125,222,160,0.12)", border: "rgba(125,222,160,0.35)", text: "#7ddea0" },
  apparatus: { bg: "rgba(109,180,240,0.12)", border: "rgba(109,180,240,0.35)", text: "#6db4f0" },
  combat:    { bg: "rgba(255,123,114,0.12)", border: "rgba(255,123,114,0.35)", text: "#ff9c96" },
  blessing:  { bg: "rgba(240,199,94,0.12)",  border: "rgba(240,199,94,0.35)",  text: "#f0c75e" },
  teaching:  { bg: "rgba(180,150,240,0.12)", border: "rgba(180,150,240,0.35)", text: "#c4a0f5" },
};

function escHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function diffStars(n) {
  return "★".repeat(n) + "☆".repeat(5 - n);
}

export function createGuideUi({ map, onLocate, onBackToList }) {
  let mainData = null;   // guides.json → mainStory
  let shrineData = [];   // shrine-guides.json → shrines[]
  let activeTab = "main";
  let query = "";
  let tempMarker = null;
  let expandedId = null;

  const listEl  = () => document.getElementById("guide-list");
  const searchEl = () => document.getElementById("guide-search");
  const progressEl = () => document.getElementById("progress-text");

  // ---------- 临时地图标记 ----------
  function clearTempMarker() {
    if (tempMarker) { map.removeLayer(tempMarker); tempMarker = null; }
  }

  function locateShrine(shrine) {
    clearTempMarker();
    const ll = xyzToLatLng(shrine.x, shrine.z);
    tempMarker = L.marker(ll, {
      title: shrine.nameZh || shrine.name,
      icon: L.divIcon({
        className: "shrine-locate-pin",
        html: '<span class="shrine-locate-dot"></span>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      }),
    }).addTo(map);
    onLocate?.(shrine, ll);
    setTimeout(() => {
      map.invalidateSize();
      map.setView(ll, Math.max(map.getZoom(), 5), { animate: true });
    }, 50);
    toast(`${shrine.nameZh || shrine.name} · 已定位`);
  }

  // ---------- 渲染主线攻略 ----------
  function renderMainGuide() {
    const host = listEl();
    if (!host || !mainData) return;
    const q = query.trim().toLowerCase();
    const quests = (mainData.quests || []).filter(qst => {
      if (!q) return true;
      return (qst.name + (qst.nameEn || "") + (qst.chapter || "")).toLowerCase().includes(q);
    });

    const el = progressEl();
    if (el) el.textContent = `主线 ${quests.length}/${(mainData.quests || []).length} 个任务`;

    host.innerHTML = "";
    if (!quests.length) {
      host.innerHTML = '<p class="guide-empty">没有匹配的任务</p>';
      return;
    }

    for (const qst of quests) {
      const isOpen = expandedId === qst.id;
      const card = document.createElement("div");
      card.className = "guide-card" + (isOpen ? " is-open" : "");
      card.dataset.id = qst.id;

      const stepsHtml = (qst.steps || []).map((s, i) =>
        `<li class="guide-step"><span class="step-num">${i + 1}</span><span>${escHtml(s)}</span></li>`
      ).join("");
      const tipsHtml = (qst.tips || []).map(t =>
        `<li class="guide-tip">${escHtml(t)}</li>`
      ).join("");
      const rewardsHtml = (qst.rewards || []).map(r =>
        `<span class="guide-reward-tag">${escHtml(r)}</span>`
      ).join("");

      card.innerHTML = `
        <button type="button" class="guide-card-header" data-toggle="${escHtml(qst.id)}">
          <span class="guide-order">${escHtml(String(qst.order).padStart(2, "0"))}</span>
          <span class="guide-card-title">
            <strong>${escHtml(qst.name)}</strong>
            ${qst.chapter ? `<small>${escHtml(qst.chapter)}</small>` : ""}
          </span>
          <span class="guide-chevron">${isOpen ? "▲" : "▼"}</span>
        </button>
        <div class="guide-card-body" ${isOpen ? "" : 'hidden'}>
          ${qst.summary ? `<p class="guide-summary">${escHtml(qst.summary)}</p>` : ""}
          <ol class="guide-steps">${stepsHtml}</ol>
          ${tipsHtml ? `<ul class="guide-tips">${tipsHtml}</ul>` : ""}
          ${rewardsHtml ? `<div class="guide-rewards">${rewardsHtml}</div>` : ""}
        </div>
      `;
      host.appendChild(card);
    }

    // 展开/折叠
    host.querySelectorAll("[data-toggle]").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.toggle;
        expandedId = expandedId === id ? null : id;
        renderMainGuide();
      });
    });
  }

  // ---------- 渲染神庙攻略 ----------
  function renderShrineGuide() {
    const host = listEl();
    if (!host) return;
    const q = query.trim().toLowerCase();
    const filtered = shrineData.filter(s => {
      if (!q) return true;
      return (s.nameZh + s.name + s.regionZh + s.subtitleZh + s.categoryZh)
        .toLowerCase().includes(q);
    });

    const el = progressEl();
    if (el) el.textContent = `神庙 ${filtered.length}/${shrineData.length} 座`;

    host.innerHTML = "";
    if (!filtered.length) {
      host.innerHTML = '<p class="guide-empty">没有匹配的神庙</p>';
      return;
    }

    // 按区域分组
    const groups = {};
    for (const s of filtered) {
      const key = s.regionZh || s.region;
      if (!groups[key]) groups[key] = [];
      groups[key].push(s);
    }

    for (const [regionZh, shrines] of Object.entries(groups)) {
      const section = document.createElement("div");
      section.className = "guide-region-group";
      const header = document.createElement("div");
      header.className = "guide-region-header";
      header.textContent = `${regionZh}（${shrines.length}）`;
      section.appendChild(header);

      for (const shrine of shrines) {
        const isOpen = expandedId === shrine.id;
        const c = CAT_COLOR[shrine.category] || CAT_COLOR.puzzle;
        const card = document.createElement("div");
        card.className = "guide-card" + (isOpen ? " is-open" : "");
        card.dataset.id = shrine.id;

        const solHtml = (shrine.solution || []).map((s, i) =>
          `<li class="guide-step"><span class="step-num">${i + 1}</span><span>${escHtml(s)}</span></li>`
        ).join("");
        const tipsHtml = (shrine.tips || []).map(t =>
          `<li class="guide-tip">${escHtml(t)}</li>`
        ).join("");
        const chestHtml = (shrine.chestContents || []).map(c =>
          `<span class="guide-reward-tag">${escHtml(c)}</span>`
        ).join("");

        card.innerHTML = `
          <button type="button" class="guide-card-header" data-toggle="${escHtml(shrine.id)}">
            <span class="shrine-cat-dot" style="background:${c.text}"></span>
            <span class="guide-card-title">
              <strong>${escHtml(shrine.nameZh || shrine.name)}</strong>
              <small>${escHtml(shrine.subtitleZh || shrine.subtitle)}
                ${shrine.isDLC ? '<span class="badge-dlc">DLC</span>' : ""}</small>
            </span>
            <span class="guide-diff">${diffStars(shrine.difficulty)}</span>
            <span class="guide-chevron">${isOpen ? "▲" : "▼"}</span>
          </button>
          <div class="guide-card-body" ${isOpen ? "" : "hidden"}>
            <div class="shrine-meta-row">
              <span class="shrine-cat-badge" style="background:${c.bg};border-color:${c.border};color:${c.text}">${escHtml(shrine.categoryZh)}</span>
              <span class="shrine-region-label">${escHtml(shrine.regionZh)}</span>
              ${shrine.mapUnit ? `<span class="shrine-region-label">${escHtml(shrine.mapUnit)}</span>` : ""}
            </div>
            ${shrine.howToFind ? `<p class="guide-how-to-find">${escHtml(shrine.howToFind)}</p>` : ""}
            <ol class="guide-steps">${solHtml}</ol>
            ${tipsHtml ? `<ul class="guide-tips">${tipsHtml}</ul>` : ""}
            ${chestHtml ? `<div class="guide-rewards">${chestHtml}</div>` : ""}
            <button type="button" class="btn guide-locate-btn" data-locate="${escHtml(shrine.id)}">在地图上显示</button>
          </div>
        `;
        section.appendChild(card);
      }
      host.appendChild(section);
    }

    // 展开/折叠
    host.querySelectorAll("[data-toggle]").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.toggle;
        expandedId = expandedId === id ? null : id;
        renderShrineGuide();
        // 展开后滚动到该卡片
        if (expandedId === id) {
          setTimeout(() => {
            const card = host.querySelector(`[data-id="${id}"]`);
            card?.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }, 60);
        }
      });
    });

    // 地图定位
    host.querySelectorAll("[data-locate]").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.locate;
        const shrine = shrineData.find(s => s.id === id);
        if (shrine) locateShrine(shrine);
      });
    });
  }

  // ---------- 渲染（统一入口）----------
  function render() {
    if (activeTab === "main") renderMainGuide();
    else renderShrineGuide();
  }

  // ---------- 搜索 ----------
  searchEl()?.addEventListener("input", e => {
    query = e.target.value || "";
    expandedId = null;
    render();
  });

  // ---------- Tab 切换 ----------
  document.querySelectorAll(".guide-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      activeTab = btn.dataset.guide;
      expandedId = null;
      query = "";
      const s = searchEl();
      if (s) s.value = "";
      document.querySelectorAll(".guide-tab").forEach(b => {
        b.classList.toggle("is-active", b.dataset.guide === activeTab);
      });
      render();
    });
  });

  return {
    load(guidesPayload, shrineGuidesPayload) {
      mainData = guidesPayload?.mainStory || null;
      shrineData = shrineGuidesPayload?.shrines || [];
      render();
    },
    render,
    clearTempMarker,
    setActiveTab(tab) {
      activeTab = tab;
      expandedId = null;
    },
  };
}
