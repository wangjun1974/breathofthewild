# BotW 旷野之息助手 — 实施计划

## 当前进度

- **状态**：呀哈哈 + 套装 + 神庙 + 希卡塔 + **攻略** **已完成**；Pages 已更新
- **在线地址**：https://wangjun1974.github.io/breathofthewild/
- **工作目录**：`~/git/agent/opencode/breathofthewild`
- **呀哈哈**：全量 **900**
- **套装**：**26 / 26**（77 部件；说明、获取、套装效果、升级材料、地图定位、已拥有）
- **神庙**：**136**（120 本体 + 16 DLC）— 已完成
- **希卡塔**：**15** — 已完成
- **攻略**：主线流程攻略 + 试炼神庙攻略 — 已完成
- **穿戴图形**：不做（仅文字）

## 目标

1. **呀哈哈**：海拉鲁地图、找法、已收集（已完成）
2. **套装图鉴**：顶栏「呀哈哈 / 套装」；列表 / 搜索 / 文字详情 / 有坐标则地图定位
3. **神庙 + 希卡塔**：地图图标（可显示/隐藏）、点击查看名称与坐标
4. **攻略**：顶栏「攻略」模式；主线流程攻略（15 主线任务分步骤）+ 试炼神庙攻略（120 本体 + 16 DLC 含解法提示）

## 内容范围（已确认）

- 全部可成套防具（含 **amiibo**、**DLC**）
- 不收录耳环/腰带散件、单一面具、神兽头盔散件
- 每件获取方式 + 效果 + 防御阶梯；套装效果；★1–★4 材料（BotW 强化不收卢比）

## 任务清单

| ID | 任务 | 状态 |
| ---- | ---- | ---- |
| phase0-plan | Clone 至 cursor 目录并落盘本 PLAN | done |
| phase1-data | `tools/build_armors.py` → `data/armors.json` | done |
| phase2-ui | 顶栏切换 + 列表/详情/已拥有/定位 | done |
| phase3-pages | 推送 GitHub Pages + 更新本文件 | done |
| phase4-data | `tools/build_landmarks.py` → `data/landmarks.json`（136 神庙 + 15 希卡塔） | done |
| phase5-ui | 筛选栏增加「隐藏神庙」「隐藏希卡塔」开关 + 地图图标 + 点击弹层 | done |
| phase6-pages | 推送 GitHub Pages + 更新本文件 | done |
| phase7-data | `data/guides.json`（主线攻略）+ `data/shrine-guides.json`（神庙攻略） | done |
| phase8-ui | 顶栏增加「攻略」+ 攻略面板（分类/搜索/展开详情）+ `js/guides.js` | done |
| phase9-pages | 推送 GitHub Pages + 更新本文件 | done |

## 技术选型

- 纯静态 SPA：Leaflet + `data/koroks.json` / `data/armors.json` / `data/landmarks.json` / `data/guides.json` / `data/shrine-guides.json`
- ES modules：`js/armors.js`、`js/owned.js`、`js/landmarks.js`、`js/guides.js`
- 套装详情仅文字与定位
- 神庙 / 希卡塔：图标显示 + 隐藏开关 + 点击弹层（名称、坐标、复制坐标）
- 攻略：主线 / 神庙分类列表 + 搜索 + 展开步骤详情 + 神庙可地图定位

## 验收标准

- [x] `PLAN.md` 与实现进度一致
- [x] 顶栏可切换「呀哈哈 / 套装」，呀哈哈不回退
- [x] 全部成套（含 amiibo、DLC）可浏览；详情含获取、效果、升级材料
- [x] 有坐标的部件可地图定位（51/77 部件有坐标）
- [x] GitHub Pages 已更新并可打开套装功能（`status: built`，`armors.json` HTTP 200）
- [x] 神庙图标可显示/隐藏（136 个，含 DLC）
- [x] 希卡塔图标可显示/隐藏（15 个）
- [x] 点击神庙/希卡塔弹层显示名称与坐标
- [x] GitHub Pages 已更新（`landmarks.json` HTTP 200）
- [x] 顶栏「攻略」模式可切换
- [x] 主线流程攻略含 15 主线任务完整步骤
- [x] 试炼神庙攻略含 136 神庙解法提示（按区域分类、可搜索）
- [x] 神庙攻略可地图定位
- [x] GitHub Pages 已更新（`guides.json` / `shrine-guides.json` HTTP 200）

## 进度日志

### 2026-09-29

- [x] 仓库 clone 至 `~/git/agent/cursor/breathofthewild`
- [x] Phase 1：26 套 / 77 部件；amiibo 可强化材料已收录
- [x] Phase 2：模式切换、列表、详情、已拥有、临时地图钉
- [x] Phase 3：推送 `948d67a` → Pages built


### 2026-09-29（获取方式修正）

- [x] 重写全部套装部件 `howToGet` 与关键地图坐标（神庙/商店/支线/DLC/amiibo）
- [x] 推送 GitHub Pages


### 2026-09-29（呀哈哈隐藏）

- [x] 筛选栏增加「隐藏呀哈哈」开关（localStorage 持久化）
- [x] 套装地图定位时强制隐藏呀哈哈图标
- [x] 推送 GitHub Pages

### 2026-09-30（神庙 + 希卡塔）

- [x] `tools/build_landmarks.py`：从 objmap static.json + 文本获取 136 神庙 + 15 希卡塔
- [x] `data/landmarks.json` 生成（28 KB）
- [x] `js/landmarks.js`：神庙/希卡塔图标图层（菱形 = 神庙，方形 = 希卡塔）
- [x] `js/state.js`：hideShrines / hideTowers + localStorage
- [x] `index.html`：筛选栏增加两个 toggle
- [x] `css/app.css`：图标样式
- [x] `js/popup.js`：点击弹层（名称、坐标、复制坐标）
- [x] `js/app.js`：数据加载 + 连线
- [x] 推送 `64a14db` → Pages built

### 2026-09-30（攻略功能）

- [x] `data/guides.json`：15 条主线任务，每条含摘要、10步攻略、贴士、奖励
- [x] `data/shrine-guides.json`：136 座神庙（本体120 + DLC16），每座含中文名、类别、难度、到达说明、解法、贴士、宝箱
- [x] `js/guides.js`：攻略面板 UI（主线/神庙 Tab、搜索、展开详情、神庙地图定位）
- [x] `index.html`：顶栏新增「攻略」按钮 + `#guide-panel` 面板结构
- [x] `js/app.js`：集成攻略模式切换、并行加载 guides.json / shrine-guides.json
- [x] `css/app.css`：攻略面板、卡片、步骤、贴士、宝箱等全套样式
- [x] 本地验证通过（JSON格式、字段完整性、HTML/JS结构）
- [x] 推送 GitHub Pages

### 既有呀哈哈（历史）

- [x] 900 呀哈哈数据与地图
- [x] GitHub Pages：https://wangjun1974.github.io/breathofthewild/
