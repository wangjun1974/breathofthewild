# BotW 呀哈哈 + 套装图鉴 — 实施计划

## 当前进度

- **状态**：呀哈哈地图 + 套装图鉴（文字详情）**已完成**；Pages 已更新
- **在线地址**：https://wangjun1974.github.io/breathofthewild/
- **工作目录**：`~/git/agent/cursor/breathofthewild`
- **呀哈哈**：全量 **900**
- **套装**：**26 / 26**（77 部件；说明、获取、套装效果、升级材料、地图定位、已拥有）
- **穿戴图形**：不做（仅文字）

## 目标

1. **呀哈哈**：海拉鲁地图、找法、已收集（已完成）
2. **套装图鉴**：顶栏「呀哈哈 / 套装」；列表 / 搜索 / 文字详情 / 有坐标则地图定位

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

## 技术选型

- 纯静态 SPA：Leaflet + `data/koroks.json` / `data/armors.json`
- ES modules：`js/armors.js`、`js/owned.js`
- 套装详情仅文字与定位

## 验收标准

- [x] `PLAN.md` 与实现进度一致
- [x] 顶栏可切换「呀哈哈 / 套装」，呀哈哈不回退
- [x] 全部成套（含 amiibo、DLC）可浏览；详情含获取、效果、升级材料
- [x] 有坐标的部件可地图定位（51/77 部件有坐标）
- [x] GitHub Pages 已更新并可打开套装功能（`status: built`，`armors.json` HTTP 200）

## 进度日志

### 2026-09-29

- [x] 仓库 clone 至 `~/git/agent/cursor/breathofthewild`
- [x] Phase 1：26 套 / 77 部件；amiibo 可强化材料已收录
- [x] Phase 2：模式切换、列表、详情、已拥有、临时地图钉
- [x] Phase 3：推送 `948d67a` → Pages built

### 既有呀哈哈（历史）

- [x] 900 呀哈哈数据与地图
- [x] GitHub Pages：https://wangjun1974.github.io/breathofthewild/
