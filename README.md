# BotW 呀哈哈地图（HTML5 / iPhone）

在《塞尔达传说：旷野之息》海拉鲁地图上标出 **900 个呀哈哈**，点击图标查看 **坐标、地点与如何找到**。

## 功能

- 全部 900 个呀哈哈图标
- 点击弹层：X/Y/Z 坐标、海拔、地图格、区域、最近地名、解谜类型、中文找法
- 按区域筛选、仅看未收集
- 已收集标记（localStorage，刷新不丢）
- 移动端底部卡片 + PWA manifest（可添加到 iPhone 主屏幕）

## 本地运行（iPhone 同一 WiFi）

```bash
cd breathofthewild
python3 -m http.server 8080 --bind 0.0.0.0
```

查看 Mac 局域网 IP：

```bash
ipconfig getifaddr en0 || ifconfig | awk '/inet / && $2!="127.0.0.1"{print $2}'
```

iPhone Safari 打开：`http://<Mac-IP>:8080`

## 数据构建（开发时）

重新生成 `data/koroks.json`：

```bash
python3 tools/build_koroks.py
```

数据源：

- 坐标：`zeldamods/objmap` 的 `korok_ids.json`（GPL-3.0）
- 类型：`radar.zeldamods.org` API
- 底图切片：`objmap.zeldamods.org/game_files/maptex/...`
- 地名：`map_summary` + `StaticMsg/LocationMarker`

人工补充攻略可写入 `data/overrides.json`：

```json
{
  "H23": {
    "hint": "自定义中文找法…",
    "note": "备注"
  }
}
```

改完后重新运行 `tools/build_koroks.py`。

## 公网 HTTPS 部署

任选其一（静态托管，无需后端）：

### Cloudflare Pages

1. 将本目录推到 GitHub
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → 连接仓库
3. 构建命令留空，输出目录 `/`
4. 访问分配的 `https://xxx.pages.dev`

### GitHub Pages（已部署）

在线地址：**https://wangjun1974.github.io/breathofthewild/**

仓库：https://github.com/wangjun1974/breathofthewild

原步骤：

1. 仓库 Settings → Pages → Source: `main` / root
2. 访问 `https://<user>.github.io/<repo>/`

### Vercel

1. Import Repo → Framework: Other → 输出根目录
2. 得到 `https://xxx.vercel.app`

### 添加到 iPhone 主屏幕

1. Safari 打开上述 HTTPS 地址
2. 分享 → **添加到主屏幕**
3. 从主屏幕图标启动（全屏、独立窗口）

> 注意：局域网 `http://IP` 无法安装主屏幕 PWA；主屏幕请用 HTTPS 地址。

## 目录结构

```
index.html
manifest.webmanifest
css/app.css
js/{app,map,markers,popup,state}.js
data/koroks.json
data/overrides.json
tools/build_koroks.py
assets/korok.png
vendor/leaflet/
PLAN.md
```

## 许可与致谢

- 地图与对象数据思路来自 [ZeldaMods objmap](https://github.com/zeldamods/objmap)（GPL-3.0）及 radar API；本项目为独立实现，未复制其前端源码。
- 底图切片由 objmap 公开 `game_files/maptex` 提供，仅作个人学习/查询用途。
- 攻略文案为按官方 `korok_type` 生成的中文步骤，非抓取第三方攻略站正文。
