#!/usr/bin/env python3
"""Build data/landmarks.json from zeldamods objmap sources.

Outputs 136 shrines (120 base + 16 DLC) and 15 Sheikah Towers with
coordinates, English names, and Chinese names.

Region assignment uses the nearest korok from koroks.json so that
shrine/tower regions match the region chips exactly.

Sources:
- map_summary/MainField/static.json: marker coordinates
- StaticMsg/LocationMarker.json: tower names, some shrine names
- StaticMsg/Dungeon.json: shrine names & subtitles
- data/koroks.json: region reference points (900 koroks)
"""
from __future__ import annotations

import json
import math
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


# Tower name → region key (matches korok region chips)
TOWER_NAME_REGION: dict[str, str] = {
    "Hebra Tower": "hebra",
    "Tabantha Tower": "tabantha",
    "Gerudo Tower": "gerudo",
    "Wasteland Tower": "wasteland",
    "Woodland Tower": "woodland",
    "Central Tower": "central",
    "Great Plateau Tower": "plateau",
    "Dueling Peaks Tower": "duelingpeaks",
    "Lake Tower": "lake",
    "Eldin Tower": "eldin",
    "Akkala Tower": "akkala",
    "Lanayru Tower": "lanayru",
    "Hateno Tower": "hateno",
    "Faron Tower": "faron",
    "Ridgeland Tower": "ridgeland",
}

# Official shrine → tower-region mapping (game map regions).
# 120 base shrines + 16 DLC (Champions' Ballad) = 136 total.
# Key = shrine short name (Dungeon.json _master value).
SHRINE_REGION: dict[str, str] = {
    # Great Plateau Tower (plateau) — 4 base + 4 DLC
    "Oman Au": "plateau", "Ja Baij": "plateau",
    "Keh Namut": "plateau", "Owa Daim": "plateau",
    "Yowaka Ita": "plateau", "Rohta Chigah": "plateau",
    "Ruvo Korbah": "plateau", "Etsu Korima": "plateau",
    # Central Tower (central) — 7
    "Katah Chuki": "central", "Wahgo Katta": "central",
    "Rota Ooh": "central", "Noya Neha": "central",
    "Namika Ozz": "central", "Kaam Ya'tak": "central",
    "Saas Ko'sah": "central",
    # Dueling Peaks Tower (duelingpeaks) — 9
    "Bosh Kala": "duelingpeaks", "Ha Dahamar": "duelingpeaks",
    "Ree Dahee": "duelingpeaks", "Shee Venath": "duelingpeaks",
    "Shee Vaneer": "duelingpeaks", "Toto Sah": "duelingpeaks",
    "Hila Rao": "duelingpeaks", "Lakna Rokee": "duelingpeaks",
    "Ta'loh Naeg": "duelingpeaks",
    # Hateno Tower (hateno) — 7
    "Myahm Agana": "hateno", "Dow Na'eh": "hateno",
    "Kam Urog": "hateno", "Chaas Qeta": "hateno",
    "Jitan Sa'mi": "hateno", "Mezza Lo": "hateno",
    "Tahno O'ah": "hateno",
    # Lanayru Tower (lanayru) — 8 base + 4 DLC
    "Ne'ez Yohma": "lanayru", "Sheh Rata": "lanayru",
    "Dagah Keek": "lanayru", "Rucco Maag": "lanayru",
    "Soh Kofi": "lanayru", "Daka Tuss": "lanayru",
    "Kaya Wan": "lanayru", "Kah Mael": "lanayru",
    "Sato Koda": "lanayru", "Kee Dafunia": "lanayru",
    "Mah Eliya": "lanayru", "Shai Yota": "lanayru",
    # Akkala Tower (akkala) — 9
    "Dah Hesho": "akkala", "Ke'nai Shakah": "akkala",
    "Katosa Aug": "akkala", "Ze Kasho": "akkala",
    "Tutsuwa Nima": "akkala", "Zuna Kai": "akkala",
    "Ritaag Zumo": "akkala", "Tu Ka'loh": "akkala",
    "Dah Kaso": "akkala",
    # Eldin Tower (eldin) — 9 base + 3 DLC
    "Mo'a Keet": "eldin", "Sah Dahaj": "eldin",
    "Daqa Koh": "eldin", "Shora Hah": "eldin",
    "Kayra Mah": "eldin", "Shae Mo'sah": "eldin",
    "Gorae Torr": "eldin", "Qua Raym": "eldin",
    "Tah Muhl": "eldin", "Kamia Omuna": "eldin",
    "Rinu Honika": "eldin", "Sharo Lun": "eldin",
    # Woodland Tower (woodland) — 8
    "Mirro Shaz": "woodland", "Keo Ruug": "woodland",
    "Monya Toma": "woodland", "Kuhn Sidajj": "woodland",
    "Maag Halan": "woodland", "Daag Chokah": "woodland",
    "Ketoh Wawai": "woodland", "Rona Kachta": "woodland",
    # Hebra Tower (hebra) — 13 base + 1 DLC
    "Sha Gehma": "hebra", "Gee Ha'rah": "hebra",
    "Hia Miu": "hebra", "Mozo Shenno": "hebra",
    "To Quomo": "hebra", "Shada Naw": "hebra",
    "Goma Asaagh": "hebra", "Rok Uwog": "hebra",
    "Rin Oyaa": "hebra", "Dunba Taag": "hebra",
    "Maka Rah": "hebra", "Lanno Kooh": "hebra",
    "Qaza Tokki": "hebra", "Kiah Toza": "hebra",
    # Tabantha Tower (tabantha) — 7
    "Akh Va'quot": "tabantha", "Bareeda Naag": "tabantha",
    "Voo Lota": "tabantha", "Sha Warvo": "tabantha",
    "Tena Ko'sah": "tabantha", "Kah Okeo": "tabantha",
    "Noe Rajee": "tabantha",
    # Ridgeland Tower (ridgeland) — 8
    "Zalta Wa": "ridgeland", "Sheem Dagoze": "ridgeland",
    "Toh Yahsa": "ridgeland", "Shae Loya": "ridgeland",
    "Mogg Latan": "ridgeland", "Mijah Rokee": "ridgeland",
    "Maag No'rah": "ridgeland", "Shira Gomar": "ridgeland",
    # Gerudo Tower (gerudo) — 12 + 1 DLC
    "Daqo Chisay": "gerudo", "Kema Zoos": "gerudo",
    "Sasa Kai": "gerudo", "Kema Kosassa": "gerudo",
    "Keeha Yoog": "gerudo", "Kihiro Moh": "gerudo",
    "Dako Tah": "gerudo", "Hawa Koth": "gerudo",
    "Sho Dantu": "gerudo", "Kuh Takkar": "gerudo",
    "Raqa Zunzo": "gerudo", "Tho Kayu": "gerudo",
    "Keive Tala": "gerudo",
    # Wasteland Tower (wasteland) — 7 + 1 DLC
    "Jee Noh": "wasteland", "Kay Noh": "wasteland",
    "Joloo Nah": "wasteland", "Dila Maag": "wasteland",
    "Misae Suma": "wasteland", "Korsh O'hu": "wasteland",
    "Suma Sahma": "wasteland", "Takama Shiri": "wasteland",
    # Lake Tower (lake) — 6
    "Ya Naga": "lake", "Ka'o Makagh": "lake",
    "Ishto Soh": "lake", "Pumaag Nitae": "lake",
    "Shoqa Tatone": "lake", "Shae Katha": "lake",
    # Faron Tower (faron) — 8
    "Yah Rin": "faron", "Kah Yah": "faron",
    "Shai Utoh": "faron", "Shoda Sah": "faron",
    "Muwo Jeem": "faron", "Qukah Nata": "faron",
    "Korgu Chideh": "faron", "Tawa Jinn": "faron",
}


def resolve_shrine_region(short_name: str) -> str:
    """Look up official tower region for a shrine by its short name."""
    return SHRINE_REGION.get(short_name, "central")


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
    unmapped: list[str] = []
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

        region = resolve_shrine_region(short_name)
        if region == "central" and short_name not in SHRINE_REGION:
            unmapped.append(short_name)
        region_zh = REGION_ZH.get(region, region)

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
            "regionZh": region_zh,
        })

    if unmapped:
        print(f"warn: {len(unmapped)} shrines not in SHRINE_REGION table (defaulted to central): {unmapped}", file=sys.stderr)
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

        warp = m.get("WarpDestMapName", "")
        map_name = re.sub(r"^MainField/", "", warp) if warp else ""

        region = TOWER_NAME_REGION.get(name_en, "central")
        region_zh = REGION_ZH.get(region, region)

        towers.append({
            "id": mid,
            "name": name_en,
            "nameZh": name_zh,
            "x": x,
            "y": y,
            "z": z,
            "mapUnit": map_name,
            "region": region,
            "regionZh": region_zh,
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
