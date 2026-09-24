# BotW 呀哈哈地图 HTML5 应用 — 实施计划

## 目标

在 `~/git/agent/mimocode/breathofthewild` 下做一个可在 **iPhone Safari** 上使用的 HTML5 应用：

- 在《旷野之息》海拉鲁地图上显示 **全部 900 个呀哈哈**
- 点击图标 → 底部弹层显示：**坐标、地点、区域、如何找到（详细攻略式提示）**
- 支持 **已收集标记**、**按区域筛选**
- 使用方式：**局域网本地服务 + 公网 HTTPS 部署（PWA 可加主屏幕）**

同时按用户要求：把计划正文落到项目目录的 markdown（`PLAN.md`），并在实现过程中随进度更新。

---

## 现状与调研结论

### 项目目录

`/Users/jwang/git/agent/mimocode/breathofthewild` 目前几乎为空（仅有 `.mimocode/` 工具文件），从零新建应用即可。

### 可用数据源（已实测）

| 用途 | 来源 | 状态 |
|------|------|------|
| 900 呀哈哈坐标 | `https://raw.githubusercontent.com/zeldamods/objmap/master/korok_ids.json` | ✅ 恰好 900 条：`id`, `Translate.X/Y/Z`, `hash_id`, `map_name`, `map_type` |
| 解谜类型 / 逐个 `korok_id` | `https://radar.zeldamods.org/obj/MainField/{map}/{hashId}` 或 `/objs/MainField/{map}?q=actor:Npc_HiddenKorokGround` | ✅ 返回 `korok_type`、`korok_id`、`field_area`；有 CORS |
| 地图底图切片 | `https://objmap.zeldamods.org/game_files/maptex/{z}/{x}/{y}.png` + `.../maptex/base.png` | ✅ HTTP 200；`maxNativeZoom: 7` |
| 投影参数 | Leaflet `CRS.Simple`，`MAP_SIZE=[24000,20000]`，`TILE_SIZE=256` | ✅ 见 objmap `src/util/map.ts`、`src/MapBase.ts` |
| 地名 | `game_files/text/StaticMsg/LocationMarker.json` + `map_summary/MainField/static.json` 的 Location/Place/Tower/Dungeon 标记 | ✅ 英文 MessageID→地名；可最近邻匹配 |
| 呀哈哈图标 | `https://raw.githubusercontent.com/zeldamods/objmap/master/public/icons/mapicon_korok.png` | ✅ 可本地化到项目 |

### 解谜类型（`korok_type`，约 30+ 实际类型）

包括：`Rock Lift`、`Rock Pattern`、`Flower Trail`、`Flower Order`、`Cube Puzzle`、`Ball and Chain`、`Pinwheel Balloons`、`Pinwheel Acorns`、`Goal Ring (Race)`、`Dive`、`Melt Ice Block`、`Matching Trees`、`Offering Plate`、`Moving Lights`、`Hanging Acorn`、`Stationary Balloon`、`Roll a Boulder` 等。

### 区域筛选

- 呀哈哈 `id` 首字母对应区域（objmap `classToColor` 映射）：`H=Hebra`, `T=Tabantha`, `G=Gerudo`, `R=Ridgeland`, `C=Central`, `P=Plateau`, `D=Dueling Peaks`, `K=Woodland`, `W=Wasteland`, `A=Akkala`, `E=Eldin`, `F=Faron`, `N=Hateno`, `L=Lake`, `Z=Lanayru`, `X=Castle` 等。
- 额外可用 `field_area`（0–93）做更细分组；实现时以 **id 首字母区域** 为主（稳定、全覆盖）。

### 许可与合规注意

- `zeldamods/objmap` 为 **GPL-3.0**：我们只 **引用公开 JSON 数据与切片 URL**，不复制其前端源码；应用自行实现，README 注明数据来源与许可。
- 不批量抓取/整段搬运 Game8、IGN、Zelda Dungeon 的攻略正文（站点声明禁止未授权复用）。  
  **“详细攻略”策略**：用官方数据 `korok_type` + 坐标/海拔/最近地名/地图格，生成 **中文类型化解谜步骤**（自写模板），并对少数特殊 ID 做人工补充备注文件。

---

## 产品范围（已确认）

1. **全部 900 个呀哈哈** 图标
2. **点击弹层**：坐标（X/Y/Z）、海拔、地图格、区域、最近地名、类型、**如何找到**（详细）
3. **已收集标记**：localStorage 持久化，可一键重置；筛选“仅未收集”
4. **按区域筛选**（Hebra / Central / … 中文名）
5. **双访问路径**：本机 `http://<Mac-LAN-IP>` + 公网 HTTPS 部署说明（可选 GitHub Pages / Cloudflare Pages）
6. **iPhone 友好**：viewport、触控缩放、底部 sheet、大点击热区、PWA manifest（可“添加到主屏幕”）

非首版（可列为后续）：搜索框、神庙/塔叠层、多设备同步、离线 Service Worker 缓存全部切片。

---

## 技术方案（推荐）

### 架构：纯静态 SPA，无后端

```
breathofthewild/
  PLAN.md                 # 项目计划与进度（实现中持续更新）
  README.md               # 使用/部署说明
  index.html              # 入口
  manifest.webmanifest    # PWA
  css/app.css
  js/
    app.js                # 启动
    map.js                # Leaflet 初始化、切片、CRS
    markers.js            # 900 marker + 聚合/性能
    popup.js              # 详情弹层
    state.js              # 区域筛选 + localStorage 已收集
    i18n.js / hints.js    # 类型中文名与找法模板
  data/
    koroks.json           # 构建期合并后的主数据
    locations.json        # 最近地名（可选预处理）
    overrides.json        # 人工补充特殊攻略
  assets/korok.png
  tools/build_koroks.py   # 数据抓取/合并脚本（仅开发时运行）
```

- **地图**：Leaflet 1.9（本地 vendored 或 CDN，部署优先本地文件，减少外网依赖）
- **底图**：复用 `objmap.zeldamods.org/game_files/maptex` 远程切片（首版不自托管 24000×20000 切片，体积过大）
- **坐标投影**（与 objmap 一致）：
  - CRS: `L.CRS.Simple`，`transformation = (4/256, 24000/256, 4/256, 20000/256)`
  - marker：`lat = Z`, `lng = X`
  - zoom：min 2 / default 3 / max 10，`maxNativeZoom: 7`
- **性能**：900 个 marker 用 Canvas 渲染或按缩放分级显示（低缩放显示聚合计数/缩小图标，高缩放全量）；避免 DOM marker 卡顿
- **弹层**：移动端 bottom sheet（非桌面 popup），显示完整信息 +「标记已收集」

### 主数据结构（`data/koroks.json` 每项）

```json
{
  "id": "H23",
  "x": -4424.15, "y": 497.16, "z": -3215.94,
  "hashId": 3077381654,
  "mapUnit": "A-1",
  "region": "hebra",
  "type": "Rock Lift",
  "typeZh": "搬起石头",
  "nearest": "Rito Village / 附近山峰",
  "hint": "【中文详细找法】…",
  "note": "可选人工补充"
}
```

`hint` 生成规则（详细、可复用）：

1. `typeZh` + 标准解谜步骤（例如 Rock Lift：检查孤石/山顶/树下，按 A 搬起）
2. 地理上下文：海拔 → “高处峰顶闪光 / 水边 / 树下 / 桥下”启发式
3. 最近 Location 标记（距离 < ~800 世界单位）
4. `overrides.json` 中按 `id` 的人工文案覆盖

---

## 实施步骤

### Phase 0 — 落盘计划文档（第 1 步必做）

1. 将本计划同步写入 `~/git/agent/mimocode/breathofthewild/PLAN.md`
2. 之后每个 Phase 完成后更新 `PLAN.md` 的「进度」与「验收记录」章节

### Phase 1 — 数据构建

1. 编写 `tools/build_koroks.py`：
   - 下载 `korok_ids.json`（900）
   - 按 `map_name` 分组，批量调用 radar `objs`/`obj` 取 `korok_type`（限速、重试）
   - 下载 `static.json` + `StaticMsg/LocationMarker.json`，为每个坐标找最近地标名
   - 计算 `region`（id 首字母映射）
   - 映射 `typeZh` + 生成 `hint`
   - 合并 `overrides.json`
   - 输出 `data/koroks.json`（校验 count==900）
2. 记录缺失 `korok_type` 的 ID 列表（少数图块可能在城堡内图等），用 `overrides` 或二次查询补全
3. 更新 `PLAN.md`：数据覆盖率（类型命中率、最近地名命中率）

### Phase 2 — 核心地图 UI

1. `index.html` + Leaflet + 自定义 CRS + 远程切片
2. 渲染 900 呀哈哈图标
3. 点击 → bottom sheet：坐标/区域/类型/最近地名/如何找到
4. 区域筛选 chips；已收集勾选 + localStorage
5. PWA manifest + 基础移动端样式（safe-area、100dvh）

### Phase 3 — 本机 iPhone 联调

1. `python3 -m http.server 8080` 或等价静态服务
2. 打印 Mac LAN IP，iPhone 同 WiFi 访问 `http://<ip>:8080`
3. 验收清单：
   - [x] 地图可缩放/拖动，切片正常（无头 Chrome：leaflet-container + 进度条「显示 900」）
   - [x] 900 图标齐全（DOM 中 korok-icon = 900；数据 typeHit/nearestHit = 900）
   - [x] 点击弹层信息完整，中文找法可读（代码路径 + 数据 hint 全覆盖；待真机点按确认）
   - [x] 区域筛选有效（state 单元逻辑 + 17 个区域 chips 已渲染）
   - [x] 标记已收集后刷新仍保留（localStorage；Node 逻辑测试通过）
   - [x] iOS Safari 触控不误拖、sheet 可滚动关闭（用户真机已测）

### Phase 4 — 公网 HTTPS 部署

1. 推荐：**Cloudflare Pages / GitHub Pages / Vercel** 静态托管（任选其一，写入 README）
2. 附：添加到 iPhone 主屏幕步骤（分享 → 添加到主屏幕）
3. 更新 `PLAN.md` 部署链接与验证结果

### Phase 5 — 打磨

1. 图标缩放/性能优化
2. 类型筛选（可选）或搜索（可选，若时间允许）
3. `README.md` 最终说明 + 数据来源致谢（ZeldaMods objmap / radar，GPL-3.0）

---

## 关键文件

| 路径 | 动作 |
|------|------|
| `~/git/agent/mimocode/breathofthewild/PLAN.md` | 新建；进度持续更新 |
| `index.html`, `css/`, `js/`, `data/`, `tools/`, `manifest.webmanifest` | 新建 |
| `/Users/jwang/.local/share/mimocode/plans/1790238784355-stellar-river.md` | 系统计划文件（本文件） |

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| radar 偶发超时/500 | 脚本重试 + 按 map unit 分批；失败项记入 overrides |
| 部分 `korok_type` 缺失 | 二次按 hash 单查；仍缺则 hint 用通用+坐标 |
| 远程切片依赖第三方 | README 标注；后续可自托管关键 zoom 层 |
| 地名仅英文 | 首版英文地名 + 中文区域/类型；可选维护中文别名表 |
| 900 marker 卡顿 | Canvas 渲染 + 缩放分级显示 |
| 攻略版权 | 不整站抓取；类型化自写中文步骤 + 人工 overrides |

---

## 验收标准

1. iPhone Safari 打开后可浏览完整海拉鲁地图并看到呀哈哈图标  
2. 点击任一图标能看到 **坐标 + 地点 + 如何找到** 的完整中文说明  
3. 区域筛选与已收集状态可用且刷新不丢  
4. 本机 LAN 与 HTTPS 部署路径均有可操作文档  
5. 项目根目录 `PLAN.md` 与实现进度一致  

---

## 进度日志（实现时填写）

- [x] 计划已同步到项目 `PLAN.md`
- [x] Phase 1 数据构建完成（900/900，typeHit=900，nearestHit=900）
- [x] Phase 2 地图与交互完成（Leaflet + 底部弹层 + 区域筛选 + 已收集）
- [x] Phase 3 iPhone 联调通过（用户真机已测）
- [x] Phase 4 公网部署完成（GitHub Pages：https://wangjun1974.github.io/breathofthewild/）
- [x] Phase 5 README/打磨完成

### 2026-09-24 实现记录

- 本地服务：`python3 -m http.server 8080 --bind 0.0.0.0`
- LAN URL：`http://10.208.167.52:8080`
- 数据：`data/koroks.json`（900 条，33 种类型全覆盖）
- 构建脚本：`tools/build_koroks.py`（map 批量 + 并发 detail 回退）

### 部署记录

- GitHub: https://github.com/wangjun1974/breathofthewild
- GitHub Pages URL: https://wangjun1974.github.io/breathofthewild/
- 分支: main / 根目录 `/`
- 验证: index/data/js/leaflet 均 HTTP 200
