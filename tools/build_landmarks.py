#!/usr/bin/env python3
"""Build data/landmarks.json from zeldamods objmap sources.

Outputs 136 shrines (120 base + 16 DLC) and 15 Sheikah Towers with
coordinates, English names, and Chinese names.

Sources:
- map_summary/MainField/static.json: marker coordinates
- StaticMsg/LocationMarker.json: tower names, some shrine names
- StaticMsg/Dungeon.json: shrine names & subtitles
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_PATH = DATA_DIR / "landmarks.json"

STATIC_URL = "https://objmap.zeldamods.org/game_files/map_summary/MainField/static.json"
LOCATION_MARKER_URL = "https://objmap.zeldamods.org/game_files/text/StaticMsg%2FLocationMarker.json"
DUNGEON_TEXT_URL = "https://objmap.zeldamods.org/game_files/text/StaticMsg%2FDungeon.json"

# Chinese names for the 15 Sheikah Towers
TOWER_ZH: dict[str, str] = {
    "Tower01": "赫布拉之塔",
    "Tower02": "塔邦达之塔",
    "Tower03": "格鲁德之塔",
    "Tower04": "荒野之塔",
    "Tower05": "森林之塔",
    "Tower06": "中央之塔",
    "Tower07": "初始台地之塔",
    "Tower08": "双子山之塔",
    "Tower09": "湖之塔",
    "Tower10": "奥尔汀之塔",
    "Tower11": "阿卡拉之塔",
    "Tower12": "拉聂尔之塔",
    "Tower13": "哈特诺之塔",
    "Tower14": "费罗尼之塔",
    "Tower15": "丘陵之塔",
}

# Map Tower ID → region key (consistent with korok region names)
TOWER_REGION: dict[str, str] = {
    "Tower01": "hebra",
    "Tower02": "tabantha",
    "Tower03": "gerudo",
    "Tower04": "wasteland",
    "Tower05": "woodland",
    "Tower06": "central",
    "Tower07": "plateau",
    "Tower08": "duelingpeaks",
    "Tower09": "lake",
    "Tower10": "eldin",
    "Tower11": "akkala",
    "Tower12": "lanayru",
    "Tower13": "hateno",
    "Tower14": "faron",
    "Tower15": "ridgeland",
}

REGION_ZH: dict[str, str] = {
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
    "ridgeland": "丘陵",
    "tabantha": "塔邦达",
    "wasteland": "荒野",
    "woodland": "森林",
}

# Shrine region assignment: map-name letter → region
MAP_LETTER_REGION: dict[str, str] = {
    "A": "akkala",
    "B": "tabantha",
    "C": "hebra",
    "D": "woodland",
    "E": "central",
    "F": "ridgeland",
    "G": "gerudo",
    "H": "wasteland",
    "I": "hateno",
    "J": "faron",
}


def http_json(url: str, retries: int = 4, timeout: int = 60) -> dict | list:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "botw-landmarks-build/1.0", "Accept": "application/json,*/*"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"GET failed: {url}: {last}")


def guess_region_from_map(warp_map: str) -> str:
    """Derive region from WarpDestMapName like 'MainField/A-1'."""
    m = re.search(r"MainField/([A-Z])-\d+", warp_map or "")
    if m:
        letter = m.group(1)
        return MAP_LETTER_REGION.get(letter, "central")
    return "central"


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching static.json ...", flush=True)
    static = http_json(STATIC_URL)
    markers = static.get("markers", {})

    print("Fetching LocationMarker text ...", flush=True)
    loc_text = http_json(LOCATION_MARKER_URL)

    print("Fetching Dungeon text ...", flush=True)
    dungeon_text = http_json(DUNGEON_TEXT_URL)

    # --- Build Shrines ---
    dungeon_markers = markers.get("Dungeon", [])
    shrines: list[dict] = []
    for m in dungeon_markers:
        mid = m.get("MessageID", "")
        if not re.fullmatch(r"Dungeon\d+", mid):
            continue
        tr = m.get("Translate", {})
        x = round(float(tr.get("X", 0)), 2)
        y = round(float(tr.get("Y", 0)), 2)
        z = round(float(tr.get("Z", 0)), 2)

        # Name: try Dungeon.json first (full name like "Oman Au Shrine")
        name_en = dungeon_text.get(mid) or loc_text.get(mid) or mid
        # Short name (without " Shrine" suffix)
        short_name = dungeon_text.get(f"{mid}_master") or name_en.replace(" Shrine", "")
        # Subtitle / puzzle
        subtitle = dungeon_text.get(f"{mid}_sub") or ""

        warp = m.get("WarpDestMapName", "")
        map_name = re.sub(r"^MainField/", "", warp) if warp else ""
        region = guess_region_from_map(warp)

        shrines.append({
            "id": mid,
            "name": name_en,
            "nameShort": short_name,
            "subtitle": subtitle,
            "x": x,
            "y": y,
            "z": z,
            "mapUnit": map_name,
            "region": region,
            "regionZh": REGION_ZH.get(region, region),
        })

    shrines.sort(key=lambda s: s["id"])

    # --- Build Towers ---
    tower_markers = markers.get("Tower", [])
    towers: list[dict] = []
    for m in tower_markers:
        mid = m.get("MessageID", "")
        if not re.fullmatch(r"Tower\d+", mid):
            continue
        tr = m.get("Translate", {})
        x = round(float(tr.get("X", 0)), 2)
        y = round(float(tr.get("Y", 0)), 2)
        z = round(float(tr.get("Z", 0)), 2)

        name_en = loc_text.get(mid) or mid
        name_zh = TOWER_ZH.get(mid, name_en)
        region = TOWER_REGION.get(mid, "central")

        warp = m.get("WarpDestMapName", "")
        map_name = re.sub(r"^MainField/", "", warp) if warp else ""

        towers.append({
            "id": mid,
            "name": name_en,
            "nameZh": name_zh,
            "x": x,
            "y": y,
            "z": z,
            "mapUnit": map_name,
            "region": region,
            "regionZh": REGION_ZH.get(region, region),
        })

    towers.sort(key=lambda t: t["id"])

    # --- Output ---
    payload = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {
            "static": STATIC_URL,
            "locationMarker": LOCATION_MARKER_URL,
            "dungeonText": DUNGEON_TEXT_URL,
            "licenseNote": "Data derived from ZeldaMods objmap (GPL-3.0).",
        },
        "stats": {
            "shrineCount": len(shrines),
            "towerCount": len(towers),
        },
        "shrines": shrines,
        "towers": towers,
    }
    OUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(
        f"Wrote {OUT_PATH}  shrines={len(shrines)}  towers={len(towers)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
