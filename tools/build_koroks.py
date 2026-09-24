#!/usr/bin/env python3
"""Build data/koroks.json from zeldamods sources.

Sources:
- korok_ids.json: coordinates for all 900 koroks
- radar.zeldamods.org: korok_type / korok_id / field_area
- static.json + LocationMarker text: nearest landmark names
"""
from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_PATH = DATA_DIR / "koroks.json"
OVERRIDES_PATH = DATA_DIR / "overrides.json"

KOROK_IDS_URL = "https://raw.githubusercontent.com/zeldamods/objmap/master/korok_ids.json"
STATIC_URL = "https://objmap.zeldamods.org/game_files/map_summary/MainField/static.json"
TEXT_LIST_URL = "https://objmap.zeldamods.org/game_files/text/list.json"
RADAR_ROOT = "https://radar.zeldamods.org"

REGION_BY_LETTER = {
    "A": "akkala",
    "C": "central",
    "D": "duelingpeaks",
    "E": "eldin",
    "F": "faron",
    "G": "gerudo",
    "H": "hebra",
    "K": "woodland",
    "L": "lake",
    "N": "hateno",
    "P": "plateau",
    "R": "ridgeland",
    "T": "tabantha",
    "W": "wasteland",
    "X": "castle",
    "Z": "lanayru",
}

REGION_ZH = {
    "akkala": "阿卡拉",
    "central": "中央海拉鲁",
    "castle": "海拉鲁城堡",
    "duelingpeaks": "双子山",
    "eldin": "奥尔汀",
    "faron": "费罗尼",
    "gerudo": "格鲁德",
    "hebra": "赫布拉",
    "hateno": "哈特诺",
    "lake": "湖之国",
    "lanayru": "拉聂尔",
    "plateau": "初始台地",
    "ridgeland": "里脊之地",
    "tabantha": "塔邦达",
    "wasteland": "荒野",
    "woodland": "迷途森林",
}

TYPE_ZH = {
    "Acorn in a Hole": "橡子入洞",
    "Ball and Chain": "铁球锁链",
    "Burn the Leaves (Goatee)": "烧掉树叶",
    "Circle of Rocks": "石圈投石",
    "Cube Puzzle": "方块拼图",
    "Dive": "跳水入环",
    "Flower Order": "数字花朵",
    "Flower Trail": "追随花朵",
    "Goal Ring (Race)": "限时竞速",
    "Hanging Acorn": "悬挂橡子",
    "Jump the Fences": "跨栏竞速",
    "Light Torch": "点燃火把",
    "Matching Trees": "果树配对",
    "Melt Ice Block": "融化冰块",
    "Moving Lights": "追逐光点",
    "Offering Plate": "供品摆放",
    "Pinwheel Acorns": "风车橡子",
    "Pinwheel Balloons": "风车气球",
    "Remove Luminous Stone": "移走夜光石",
    "Rock Lift": "搬起石头",
    "Rock Lift (Boulder)": "搬起巨石",
    "Rock Lift (Door)": "搬石开门",
    "Rock Lift (Leaves)": "搬开树叶下的石头",
    "Rock Lift (Rock Pile)": "搬开石堆下的石头",
    "Rock Lift (Slab)": "搬起石板",
    "Rock Pattern": "补全石阵",
    "Roll a Boulder": "推滚巨石",
    "Shoot the Crest": "射击徽记",
    "Shoot the Targets": "射击靶子",
    "Stationary Balloon": "静止气球",
    "Stationary Lights": "静止光点",
    "Take Apple from Palm Tree": "摘棕榈果",
    "Take the Stick": "拿走木棍",
    "Unknown": "靠近调查",
}

# Detailed how-to templates keyed by English korok_type.
TYPE_HINTS = {
    "Rock Lift": (
        "【如何找到】到坐标附近寻找一颗突兀的孤石（常见于山顶、树下、平台、桥面、悬崖边）。"
        "走近按互动键搬起石头，呀哈哈会出现并给你呀哈哈种子。若附近有落叶堆/石堆/石板，先清开再找石头。"
    ),
    "Rock Lift (Boulder)": (
        "【如何找到】在坐标点找明显偏大的巨石（常在山坡或开阔地）。搬起巨石即可出现呀哈哈；"
        "若巨石较重，先清空周围敌人再靠近互动。"
    ),
    "Rock Lift (Door)": (
        "【如何找到】坐标附近可能有可搬动的石块/石板门。先确认周围没有卡住的障碍，再搬起石头；"
        "若在遗迹门口，石头常压在门槛或门闩位置。"
    ),
    "Rock Lift (Leaves)": (
        "【如何找到】先用火焰/火焰武器烧掉坐标附近的落叶堆，或用双手武器扫开叶子，下面通常藏着可搬起的石头。"
    ),
    "Rock Lift (Rock Pile)": (
        "【如何找到】先用炸弹炸开坐标处的碎石堆/可破坏石墙，再搬起露出的石头。"
    ),
    "Rock Lift (Slab)": (
        "【如何找到】坐标附近有平铺石板或扁平岩石，搬起/掀开石板即可。若搬不动，检查是否需要用磁力抓取器。"
    ),
    "Rock Pattern": (
        "【如何找到】观察地面/水中的石头阵列，找出缺口形状。到附近找松散石块，对准缺口补齐图案；"
        "缺口方向往往对应要找的那块石头。若石头在水里，可站在高处抛投，或用造冰能力垫脚。"
    ),
    "Roll a Boulder": (
        "【如何找到】在坐标附近找到明显摆放的巨石与目标洞口/双树缝隙。把巨石推向洞中；"
        "斜坡可用静止器预瞄方向，平地可边推边调整，注意避开树木卡住。"
    ),
    "Flower Trail": (
        "【如何找到】在坐标一带寻找黄色小花。靠近一朵花它会消失并在前方出现下一朵；一路跟到白色终点花并调查。"
        "注意悬崖、树顶、屋顶等高低差。"
    ),
    "Flower Order": (
        "【如何找到】找到按数量分组的花丛。按从少到多的顺序依次触碰花朵（1朵→2朵→…），最后一朵白花处出现呀哈哈。"
    ),
    "Cube Puzzle": (
        "【如何找到】用磁力抓取器抓取金属方块，放入对应凹槽，使两侧方块图案/轮廓完全对称。对齐后呀哈哈出现。"
    ),
    "Ball and Chain": (
        "【如何找到】用磁力抓取器抓住锁链铁球，投入旁边的空心树洞/井口/容器中。球落到位后呀哈哈出现。"
    ),
    "Circle of Rocks": (
        "【如何找到】水中或地面有石圈缺口。捡起附近小石头，靠近缺口将石头抛入圈中心；"
        "水面可先造冰垫脚，注意抛物线方向。"
    ),
    "Dive": (
        "【如何找到】坐标附近的水面上有睡莲围成的圆环。从高处/岸边跃起，头朝下俯冲落入圆环正中即可。"
    ),
    "Goal Ring (Race)": (
        "【如何找到】踩上带叶子的树桩触发计时，再冲向金色圆环终点。可滑翔、走捷径；"
        "若距离远，先爬到高处再滑翔过去。"
    ),
    "Jump the Fences": (
        "【如何找到】踩树桩触发短跑计时，连续跳过栅栏/障碍冲到终点环。保持冲刺，别绕远路。"
    ),
    "Pinwheel Balloons": (
        "【如何找到】靠近坐标处的风车（转轮）会刷出若干气球。站在风车位置用弓箭把所有气球射爆；"
        "移动气球可预判轨迹或用静止器定住再射。"
    ),
    "Pinwheel Acorns": (
        "【如何找到】靠近风车后出现跳动的橡子。用弓箭射击全部橡子；难瞄时可用静止器短暂定住。"
        "若目标消失，退开几步再靠近风车刷新。"
    ),
    "Hanging Acorn": (
        "【如何找到】在树干中空、桥下、屋檐下寻找悬挂的橡子，用弓箭射断绳子/直接射中橡子。"
    ),
    "Acorn in a Hole": (
        "【如何找到】在树洞、石缝或柱子上的小洞里找橡子，用弓箭精准射入/射中。"
    ),
    "Stationary Balloon": (
        "【如何找到】在树冠、桥下、岩架或建筑边缘寻找单个静止气球，用弓箭射爆。"
    ),
    "Shoot the Targets": (
        "【如何找到】在坐标附近找靶子（风车或固定靶）。用弓箭射中所有靶子；多个靶注意先后与角度。"
    ),
    "Shoot the Crest": (
        "【如何找到】墙上的徽记/纹章需要用弓箭射击命中。站到正面角度，射中徽记中心即可。"
    ),
    "Matching Trees": (
        "【如何找到】观察一排果树/棕榈的数量差异。摘下多余的果实使每棵数量一致；"
        "也可能需要补种/移动果实。沙漠棕榈同样按此规则。"
    ),
    "Take Apple from Palm Tree": (
        "【如何找到】坐标附近棕榈树上果实数量与相邻树不一致，摘下多余果实使它们一致。"
    ),
    "Offering Plate": (
        "【如何找到】神像/祭坛前的供盘有空位。按空盘要求放入对应物品（常见苹果，也可能香蕉、辣椒等），"
        "放齐后呀哈哈出现。"
    ),
    "Melt Ice Block": (
        "【如何找到】坐标处有不规则冰块。用火焰武器、火把、火焰果实或升调技能融化冰块，随后调查闪光。"
    ),
    "Moving Lights": (
        "【如何找到】空中/地面有移动的光点（像萤火虫）。追上并调查光点；若点到坐标却消失，扩大半径在附近绕圈找。"
    ),
    "Stationary Lights": (
        "【如何找到】坐标处有静止的光点/闪光，靠近直接调查即可。"
    ),
    "Light Torch": (
        "【如何找到】附近有未点燃的火把或火盆。用火焰箭/火焰武器点燃指定火把，顺序若有多处则全部点亮。"
    ),
    "Remove Luminous Stone": (
        "【如何找到】用磁力抓取器或直接搬开压住闪光点的夜光石/矿石，随后调查露出的位置。"
    ),
    "Take the Stick": (
        "【如何找到】坐标处有一根突兀的木棍/树枝，直接拿走（互动）即可触发呀哈哈。"
    ),
    "Unknown": (
        "【如何找到】已在地图标出精确坐标。到达后在小范围内仔细听呀哈哈笑声/看叶子晃动，"
        "常见类型：孤石、闪光、供品、射靶、花丛。戴上呀哈哈面具可提示更近。"
    ),
}

NEAR_THRESHOLD = 900.0


def http_get(url: str, *, retries: int = 4, timeout: int = 40, sleep: float = 0.4):
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "botw-korok-map-build/1.0",
                    "Accept": "application/json,*/*",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            time.sleep(sleep)
            return data
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.8 * (attempt + 1))
    raise RuntimeError(f"GET failed: {url}: {last_err}")


def http_json(url: str, **kwargs):
    return json.loads(http_get(url, **kwargs).decode("utf-8"))


def fetch_korok_ids() -> list[dict]:
    return http_json(KOROK_IDS_URL, retries=5)


def fetch_location_landmarks() -> list[dict]:
    static = http_json(STATIC_URL, retries=5)
    markers = static.get("markers", {})
    text = {}
    try:
        files = http_json(TEXT_LIST_URL, retries=3)
        if "StaticMsg/LocationMarker.json" in files:
            text = http_json(
                "https://objmap.zeldamods.org/game_files/text/StaticMsg%2FLocationMarker.json",
                retries=3,
            )
    except Exception as e:  # noqa: BLE001
        print(f"warn: text load failed: {e}", file=sys.stderr)

    landmarks: list[dict] = []
    for group in ("Location", "Place", "Tower", "Dungeon", "Labo", "Shop"):
        for m in markers.get(group, []) or []:
            tr = m.get("Translate") or {}
            if "X" not in tr or "Z" not in tr:
                continue
            mid = m.get("MessageID") or m.get("SaveFlag") or ""
            name = text.get(mid) or mid
            if group == "Place" and m.get("Icon") == "Village":
                name = f"{name} (Village)" if name else "Village"
            landmarks.append(
                {
                    "x": float(tr["X"]),
                    "z": float(tr["Z"]),
                    "name": name,
                    "group": group,
                }
            )
    return landmarks


def nearest_landmark(x: float, z: float, landmarks: list[dict]) -> tuple[str | None, float]:
    best = None
    best_d = math.inf
    for lm in landmarks:
        d = math.hypot(lm["x"] - x, lm["z"] - z)
        if d < best_d:
            best_d = d
            best = lm
    if best is None or best_d > NEAR_THRESHOLD:
        return None, best_d if best else math.inf
    return best["name"], best_d


def _fetch_one_detail(item: dict) -> tuple[str, dict | None]:
    hid = str(item["hash_id"])
    detail_url = (
        f"{RADAR_ROOT}/obj/MainField/{urllib.parse.quote(item['map_name'])}/{hid}"
    )
    try:
        obj = http_json(detail_url, retries=3, timeout=25, sleep=0.05)
        return hid, {
            "korok_type": obj.get("korok_type"),
            "korok_id": obj.get("korok_id"),
            "field_area": obj.get("field_area"),
        }
    except Exception:  # noqa: BLE001
        return hid, None


def fetch_types_by_map(koroks: list[dict]) -> dict[str, dict]:
    by_map: dict[str, list[dict]] = defaultdict(list)
    for k in koroks:
        by_map[k["map_name"]].append(k)

    type_by_hash: dict[str, dict] = {}

    for i, (map_name, items) in enumerate(sorted(by_map.items()), 1):
        url = (
            f"{RADAR_ROOT}/objs/MainField/{urllib.parse.quote(map_name)}?"
            + urllib.parse.urlencode(
                {"q": "actor:Npc_HiddenKorokGround", "limit": "500"}
            )
        )
        try:
            arr = http_json(url, retries=4, timeout=40, sleep=0.05)
        except Exception as e:  # noqa: BLE001
            print(f"warn: map {map_name} search failed: {e}", file=sys.stderr)
            arr = []
        for obj in arr:
            hid = str(obj.get("hash_id"))
            type_by_hash[hid] = {
                "korok_type": obj.get("korok_type"),
                "korok_id": obj.get("korok_id"),
                "field_area": obj.get("field_area"),
            }
        if i % 10 == 0 or i == len(by_map):
            print(f"  map progress {i}/{len(by_map)}", flush=True)

    missing_items = [
        k
        for k in koroks
        if not (type_by_hash.get(str(k["hash_id"])) or {}).get("korok_type")
    ]
    print(f"fallback detail fetch for {len(missing_items)} entries ...", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    missing_ids: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_fetch_one_detail, item) for item in missing_items]
        done = 0
        for fut in as_completed(futures):
            hid, info = fut.result()
            done += 1
            if info and info.get("korok_type"):
                type_by_hash[hid] = info
            else:
                # keep empty entry so build can report missing ids
                type_by_hash.setdefault(hid, info or {})
                missing_ids.append(hid)
            if done % 25 == 0 or done == len(missing_items):
                print(f"  fallback {done}/{len(missing_items)}", flush=True)

    if missing_ids:
        print(f"type still missing hashes: {len(missing_ids)}", file=sys.stderr)
    return type_by_hash


def elevation_context(y: float) -> str:
    if y >= 600:
        return "位于高海拔（山峰/塔/树顶一带），优先检查最高点闪光、悬崖边与建筑顶端。"
    if y >= 250:
        return "位于中高海拔（山腰/台地），检查坡顶、岩架与树冠。"
    if y >= 80:
        return "位于中等高度，检查平原孤石、废墟与河岸。"
    return "位于低海拔（河谷/湖边/桥下），检查水面石圈、桥底气球与岸边供品。"


def load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        return json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"warn: overrides unreadable: {e}", file=sys.stderr)
        return {}


def build_hint(k: dict) -> str:
    type_en = k.get("type") or "Unknown"
    base = TYPE_HINTS.get(type_en, TYPE_HINTS["Unknown"])
    parts = [base, elevation_context(k["y"])]
    if k.get("nearest"):
        parts.append(f"参考地名：{k['nearest']}（约 {int(k.get('nearestDist', 0))} 单位）。")
    parts.append(
        f"地图格 {k['mapUnit']}，区域「{REGION_ZH.get(k['region'], k['region'])}」。"
        "到达坐标后缩小搜索半径，注意叶子晃动与笑声。"
    )
    return " ".join(parts)


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Fetching korok_ids.json ...", flush=True)
    raw = fetch_korok_ids()
    if len(raw) != 900:
        print(f"error: expected 900 koroks, got {len(raw)}", file=sys.stderr)
        return 1

    print("Fetching landmarks ...", flush=True)
    landmarks = fetch_location_landmarks()
    print(f"  landmarks: {len(landmarks)}", flush=True)

    print("Fetching korok types from radar ...", flush=True)
    type_by_hash = fetch_types_by_map(raw)

    overrides = load_overrides()
    out: list[dict] = []
    type_hit = 0
    near_hit = 0

    for item in raw:
        tr = item["Translate"]
        x, y, z = float(tr["X"]), float(tr["Y"]), float(tr["Z"])
        k_id = item["id"]
        letter = (k_id or "X")[0].upper()
        region = REGION_BY_LETTER.get(letter, "central")
        info = type_by_hash.get(str(item["hash_id"]), {})
        type_en = info.get("korok_type") or "Unknown"
        if type_en and type_en != "Unknown":
            type_hit += 1
        nearest, dist = nearest_landmark(x, z, landmarks)
        if nearest:
            near_hit += 1

        rec = {
            "id": k_id,
            "x": round(x, 2),
            "y": round(y, 2),
            "z": round(z, 2),
            "hashId": item["hash_id"],
            "mapUnit": item.get("map_name") or "",
            "region": region,
            "regionZh": REGION_ZH.get(region, region),
            "type": type_en,
            "typeZh": TYPE_ZH.get(type_en, TYPE_ZH["Unknown"]),
            "fieldArea": info.get("field_area"),
            "nearest": nearest,
            "nearestDist": None if nearest is None else round(dist, 1),
        }
        ov = overrides.get(k_id) or {}
        if ov.get("type"):
            rec["type"] = ov["type"]
            rec["typeZh"] = TYPE_ZH.get(ov["type"], rec["typeZh"])
        if ov.get("nearest"):
            rec["nearest"] = ov["nearest"]
        if ov.get("note"):
            rec["note"] = ov["note"]
        rec["hint"] = ov.get("hint") or build_hint(rec)
        out.append(rec)

    # Stable order by id
    out.sort(key=lambda r: r["id"])

    if len(out) != 900:
        print(f"error: output count {len(out)} != 900", file=sys.stderr)
        return 1

    payload = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {
            "korokIds": KOROK_IDS_URL,
            "radar": RADAR_ROOT,
            "tiles": "https://objmap.zeldamods.org/game_files/maptex",
            "licenseNote": "Data derived from ZeldaMods objmap (GPL-3.0) and radar API.",
        },
        "stats": {
            "count": len(out),
            "typeHit": type_hit,
            "nearestHit": near_hit,
            "typeMissing": 900 - type_hit,
        },
        "koroks": out,
    }
    OUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(
        f"Wrote {OUT_PATH} count={len(out)} typeHit={type_hit} nearestHit={near_hit}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
