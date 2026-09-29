#!/usr/bin/env python3
"""Generate data/armors.json — BotW 成套防具图鉴数据."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "armors.json"

SETS: list[dict] = []

# 防御阶梯（含未强化基准）
DEF2 = [2, 4, 6, 9, 16]
DEF3 = [3, 5, 8, 12, 20]
DEF4 = [4, 7, 12, 18, 28]


def m(mid: str, name: str, count: int) -> dict:
    # UI 使用 item 字段；保留 id 便于去重
    return {"id": mid, "item": name, "count": count}


def loc(x: float, z: float, label: str, y: float = 0) -> dict:
    return {"x": x, "y": y, "z": z, "label": label}


def ups(
    star1: list[dict],
    star2: list[dict],
    star3: list[dict],
    star4: list[dict],
) -> dict:
    return {"star1": star1, "star2": star2, "star3": star3, "star4": star4}


def piece(
    slot: str,
    name: str,
    defense: list[int],
    how_to_get: str,
    effect: str,
    location: dict | None = None,
    *,
    pid: str | None = None,
) -> dict:
    p: dict = {
        "id": pid or "",
        "slot": slot,
        "name": name,
        "defense": defense,
        "howToGet": how_to_get,
        "effect": effect,
    }
    if location is not None:
        p["location"] = location
    return p


def add(
    *,
    id: str,
    name: str,
    category: str,
    description: str,
    pieces: list[dict],
    set_bonus: dict,
    amiibo: bool = False,
    dlc: bool = False,
    upgradable: bool = True,
    upgrades: dict | None = None,
) -> None:
    for p in pieces:
        if not p.get("id"):
            p["id"] = f"{id}_{p['slot']}"
    entry: dict = {
        "id": id,
        "name": name,
        "category": category,
        "amiibo": amiibo,
        "dlc": dlc,
        "upgradable": upgradable,
        "description": description,
        "setBonus": set_bonus,
        "pieces": pieces,
    }
    if upgradable and upgrades is not None:
        entry["upgrades"] = upgrades
    SETS.append(entry)


# Amiibo 勇者系：各件强化材料相同（宝石 + 星之碎片）
def amiibo_hero_up(gem: str, gem_zh: str) -> dict:
    return ups(
        [m(gem, gem_zh, 1), m("star_fragment", "星之碎片", 1)],
        [m(gem, gem_zh, 3), m("star_fragment", "星之碎片", 1)],
        [m(gem, gem_zh, 5), m("star_fragment", "星之碎片", 1)],
        [m(gem, gem_zh, 10), m("star_fragment", "星之碎片", 1)],
    )


FIERCE_UP = ups(
    [m("hinox_tooth", "西诺克斯的牙齿", 5), m("dinraal_scale", "奥尔龙的鳞片", 1)],
    [m("hinox_guts", "西诺克斯的肝脏", 5), m("dinraal_claw", "奥尔龙的爪子", 1)],
    [m("lynel_guts", "莱尼尔的肝脏", 2), m("shard_dinraal_fang", "奥尔龙的牙齿碎片", 1)],
    [m("lynel_guts", "莱尼尔的肝脏", 2), m("shard_dinraal_horn", "奥尔龙的犄角碎片", 1)],
)


# —— 常用升级材料模板 ——
HYLIAN_UP = ups(
    [m("bokoblin_horn", "波克布林的犄角", 5)],
    [m("blue_bokoblin_horn", "蓝色波克布林的犄角", 5), m("bokoblin_fang", "波克布林的牙齿", 3)],
    [
        m("black_bokoblin_horn", "黑色波克布林的犄角", 5),
        m("bokoblin_guts", "波克布林的肝脏", 3),
        m("amber", "琥珀", 20),
    ],
    [
        m("silver_bokoblin_horn", "银色波克布林的犄角", 5),
        m("bokoblin_guts", "波克布林的肝脏", 5),
        m("amber", "琥珀", 30),
    ],
)

SOLDIER_UP = ups(
    [m("chuchu_jelly", "丘丘胶", 5), m("bokoblin_guts", "波克布林的肝脏", 3)],
    [m("keese_eyeball", "蝙蝠的眼珠", 5), m("moblin_guts", "莫力布林的肝脏", 3)],
    [
        m("lizalfos_tail", "蜥蜴战士的尾巴", 3),
        m("hinox_guts", "西诺克斯的肝脏", 3),
        m("flint", "打火石", 30),
    ],
    [
        m("lynel_hoof", "莱尼尔的蹄子", 5),
        m("lynel_guts", "莱尼尔的肝脏", 5),
        m("amber", "琥珀", 30),
    ],
)

SNOWQUILL_UP = ups(
    [m("red_chuchu_jelly", "红色丘丘胶", 3)],
    [m("red_chuchu_jelly", "红色丘丘胶", 5), m("warm_safflina", "暖暖草果", 3)],
    [
        m("fire_keese_wing", "火蝙蝠的翅膀", 5),
        m("fire_breath_lizalfos_tail", "喷火蜥蜴战士的尾巴", 3),
        m("sunshroom", "阳光蘑菇", 5),
    ],
    [
        m("fire_breath_lizalfos_horn", "喷火蜥蜴战士的犄角", 5),
        m("fire_breath_lizalfos_tail", "喷火蜥蜴战士的尾巴", 10),
        m("ruby", "红宝石", 5),
    ],
)

DESERT_VOE_UP = ups(
    [m("white_chuchu_jelly", "白色丘丘胶", 3)],
    [m("white_chuchu_jelly", "白色丘丘胶", 5), m("cool_safflina", "清凉草果", 3)],
    [
        m("ice_keese_wing", "冰蝙蝠的翅膀", 5),
        m("ice_breath_lizalfos_tail", "喷冰蜥蜴战士的尾巴", 3),
        m("chillshroom", "冰冷蘑菇", 5),
    ],
    [
        m("ice_breath_lizalfos_horn", "喷冰蜥蜴战士的犄角", 5),
        m("ice_breath_lizalfos_tail", "喷冰蜥蜴战士的尾巴", 10),
        m("sapphire", "蓝宝石", 5),
    ],
)

RUBBER_UP = ups(
    [m("electric_lizalfos_horn", "电蜥蜴战士的犄角", 1), m("yellow_chuchu_jelly", "黄色丘丘胶", 3)],
    [m("yellow_chuchu_jelly", "黄色丘丘胶", 8), m("voltfruit", "伏特水果", 5)],
    [
        m("zapshroom", "雷电蘑菇", 5),
        m("electric_lizalfos_tail", "电蜥蜴战士的尾巴", 5),
        m("electric_safflina", "电草", 8),
    ],
    [
        m("electric_lizalfos_horn", "电蜥蜴战士的犄角", 5),
        m("topaz", "黄宝石", 5),
        m("electric_lizalfos_tail", "电蜥蜴战士的尾巴", 8),
    ],
)

FLAMEBREAKER_UP = ups(
    [m("moblin_horn", "莫力布林的犄角", 3)],
    [m("moblin_fang", "莫力布林的牙齿", 5), m("fireproof_lizard", "防火蜥蜴", 5)],
    [
        m("blue_moblin_horn", "蓝色莫力布林的犄角", 5),
        m("smotherwing_butterfly", "耐火凤蝶", 3),
        m("flint", "打火石", 15),
    ],
    [
        m("black_moblin_horn", "黑色莫力布林的犄角", 5),
        m("smotherwing_butterfly", "耐火凤蝶", 5),
        m("flint", "打火石", 30),
    ],
)

ZORA_UP = ups(
    [m("lizalfos_horn", "蜥蜴战士的犄角", 3)],
    [m("lizalfos_talon", "蜥蜴战士的爪子", 5), m("hyrule_bass", "海拉鲁鲈鱼", 5)],
    [
        m("blue_lizalfos_horn", "蓝色蜥蜴战士的犄角", 5),
        m("lizalfos_tail", "蜥蜴战士的尾巴", 3),
        m("hearty_bass", "大鲈鱼", 3),
    ],
    [
        m("black_lizalfos_horn", "黑色蜥蜴战士的犄角", 5),
        m("blue_lizalfos_tail", "蓝色蜥蜴战士的尾巴", 5),
        m("opal", "蛋白石", 20),
    ],
)

STEALTH_UP = ups(
    [m("blue_nightshade", "蓝夜影", 3)],
    [m("blue_nightshade", "蓝夜影", 5), m("sunset_firefly", "落日萤火虫", 5)],
    [
        m("silent_shroom", "潜行蘑菇", 8),
        m("sneaky_river_snail", "潜行蜗牛", 5),
        m("sticky_frog", "贴贴蛙", 5),
    ],
    [
        m("sneaky_river_snail", "潜行蜗牛", 10),
        m("silent_princess", "静谧公主", 5),
        m("octorok_eyeball", "八爪怪的眼珠", 10),
    ],
)

CLIMBING_UP = ups(
    [m("keese_wing", "蝙蝠的翅膀", 3), m("rushroom", "速速蘑菇", 3)],
    [m("electric_keese_wing", "电蝙蝠的翅膀", 5), m("hightail_lizard", "速速蜥蜴", 5)],
    [m("ice_keese_wing", "冰蝙蝠的翅膀", 8), m("hot_footed_frog", "热火蛙", 10)],
    [m("fire_keese_wing", "火蝙蝠的翅膀", 10), m("swift_violet", "速速紫罗兰", 20)],
)

BARBARIAN_UP = ups(
    [m("lynel_horn", "莱尼尔的犄角", 10)],
    [m("lynel_horn", "莱尼尔的犄角", 15), m("lynel_hoof", "莱尼尔的蹄子", 10)],
    [m("lynel_horn", "莱尼尔的犄角", 20), m("lynel_guts", "莱尼尔的肝脏", 3)],
    [m("lynel_guts", "莱尼尔的肝脏", 5), m("lynel_hoof", "莱尼尔的蹄子", 20)],
)

RADIANT_UP = ups(
    [m("luminous_stone", "夜光石", 10), m("bokoblin_guts", "波克布林的肝脏", 1)],
    [m("luminous_stone", "夜光石", 15), m("moblin_guts", "莫力布林的肝脏", 2)],
    [
        m("luminous_stone", "夜光石", 20),
        m("molduga_guts", "莫尔德拉吉克的肝脏", 2),
        m("molduga_fin", "莫尔德拉吉克的鳍", 2),
        m("bokoblin_guts", "波克布林的肝脏", 5),
    ],
    [m("luminous_stone", "夜光石", 30), m("star_fragment", "星星碎片", 3)],
)

ANCIENT_UP = ups(
    [m("ancient_screw", "古代螺丝", 5), m("ancient_spring", "古代弹簧", 5)],
    [m("ancient_gear", "古代齿轮", 5), m("ancient_shaft", "古代轴", 5)],
    [m("ancient_core", "古代核心", 5), m("ancient_screw", "古代螺丝", 5)],
    [m("giant_ancient_core", "巨大古代核心", 1), m("star_fragment", "星星碎片", 3)],
)

WILD_UP = ups(
    [m("acorn", "橡果", 50)],
    [m("courser_bee_honey", "精力蜜蜂蜂蜜", 5)],
    [m("keese_eyeball", "蝙蝠的眼珠", 10), m("sunshroom", "阳光蘑菇", 10)],
    [m("star_fragment", "星星碎片", 3), m("diamond", "钻石", 1)],
)


def build_sets() -> None:
    # —— 海利亚 ——
    add(
        id="hylian",
        name="海利亚套装",
        category="商店",
        description="海拉鲁各地防具店出售的基础旅行装，均衡而实用。",
        amiibo=False,
        dlc=False,
        upgradable=True,
        upgrades=HYLIAN_UP,
        set_bonus={
            "level2": None,
            "note": "无套装加成；单件无特殊效果，适合早期替换初始装。",
        },
        pieces=[
            piece(
                "head",
                "海利亚兜帽",
                DEF3,
                "在卡卡利科村或哈特诺村防具店购买。",
                "无特殊效果。",
                loc(1846, 1007, "卡卡利科村 防具店"),
            ),
            piece(
                "body",
                "海利亚服",
                DEF3,
                "在卡卡利科村或哈特诺村防具店购买。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺村 防具店"),
            ),
            piece(
                "legs",
                "海利亚裤子",
                DEF3,
                "在卡卡利科村或哈特诺村防具店购买。",
                "无特殊效果。",
                loc(1846, 1007, "卡卡利科村 防具店"),
            ),
        ],
    )

    add(
        id="soldier",
        name="士兵套装",
        category="战斗",
        description="高防御重型护甲，无套装特技，适合纯减伤构筑。",
        upgradable=True,
        upgrades=SOLDIER_UP,
        set_bonus={"level2": None, "note": "无套装加成。"},
        pieces=[
            piece(
                "head",
                "士兵头盔",
                DEF4,
                "哈特诺村防具店购买（需完成一定主线进度后上架）。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺村 防具店"),
            ),
            piece(
                "body",
                "士兵铠甲",
                DEF4,
                "哈特诺村防具店购买。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺村 防具店"),
            ),
            piece(
                "legs",
                "士兵护胫",
                DEF4,
                "哈特诺村防具店购买。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺村 防具店"),
            ),
        ],
    )

    add(
        id="snowquill",
        name="利特防寒服套装",
        category="环境",
        description="利特族传统防寒装，抵御寒冷与冰冻。",
        upgradable=True,
        upgrades=SNOWQUILL_UP,
        set_bonus={
            "level2": "抗冻",
            "note": "两件起：免疫冰冻状态（仍受极端寒冷伤害，需配合料理）。",
        },
        pieces=[
            piece(
                "head",
                "雪鸟头饰",
                DEF3,
                "利特村防具店购买。",
                "抗寒。",
                loc(-3615, -1815, "利特村 防具店"),
            ),
            piece(
                "body",
                "雪鸟羽饰",
                DEF3,
                "利特村防具店购买。",
                "抗寒。",
                loc(-3615, -1815, "利特村 防具店"),
            ),
            piece(
                "legs",
                "雪鸟长裤",
                DEF3,
                "利特村防具店购买。",
                "抗寒。",
                loc(-3615, -1815, "利特村 防具店"),
            ),
        ],
    )

    add(
        id="desert_voe",
        name="沙漠服套装",
        category="环境",
        description="格鲁德族耐热装，并可在升级后进一步抗雷。",
        upgradable=True,
        upgrades=DESERT_VOE_UP,
        set_bonus={
            "level2": "防雷",
            "note": "单件耐热；两件起（需★2）：免疫触电与雷电伤害。",
        },
        pieces=[
            piece(
                "head",
                "沙漠伏特头巾",
                DEF3,
                "格鲁德小镇防具店购买（需先取得「瓦伊」伪装进入）。",
                "耐热。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
            piece(
                "body",
                "沙漠伏特护肩",
                DEF3,
                "格鲁德小镇防具店购买。",
                "耐热。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
            piece(
                "legs",
                "沙漠伏特长裤",
                DEF3,
                "格鲁德小镇防具店购买。",
                "耐热。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
        ],
    )

    add(
        id="gerudo",
        name="格鲁德套装",
        category="特殊",
        description="格鲁德族「瓦伊」伪装，用于进入格鲁德小镇；不可在大精灵处升级。",
        upgradable=False,
        set_bonus={
            "level2": "耐热",
            "note": "两件起：额外耐热；三件齐全时可伪装成瓦伊进入格鲁德小镇。",
        },
        pieces=[
            piece(
                "head",
                "格鲁德兜帽",
                [3],
                "格鲁德小镇防具店购买。",
                "伪装成瓦伊。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
            piece(
                "body",
                "格鲁德上衣",
                [3],
                "格鲁德小镇防具店购买。",
                "伪装成瓦伊。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
            piece(
                "legs",
                "格鲁德裤",
                [3],
                "格鲁德小镇防具店购买。",
                "伪装成瓦伊。",
                loc(-3827, 2917, "格鲁德小镇 防具店"),
            ),
        ],
    )

    add(
        id="rubber",
        name="橡胶套装",
        category="环境",
        description="绝缘橡胶装，防雷击，升级后可完全免疫电流。",
        upgradable=True,
        upgrades=RUBBER_UP,
        set_bonus={
            "level2": "绝缘",
            "note": "两件起：免疫触电与雷电伤害。",
        },
        pieces=[
            piece(
                "head",
                "橡胶头盔",
                DEF3,
                "完成「橡胶制」支线：在费罗尼地区找到三处橡胶制部件并交给商人。",
                "抗雷。",
                loc(2745, -1200, "费罗尼 橡胶制商人"),
            ),
            piece(
                "body",
                "橡胶铠甲",
                DEF3,
                "橡胶制支线奖励。",
                "抗雷。",
            ),
            piece(
                "legs",
                "橡胶紧身裤",
                DEF3,
                "橡胶制支线奖励。",
                "抗雷。",
            ),
        ],
    )

    add(
        id="flamebreaker",
        name="防火套装",
        category="环境",
        description="鼓隆族防火装，在奥尔汀火山区域必备。",
        upgradable=True,
        upgrades=FLAMEBREAKER_UP,
        set_bonus={
            "level2": "防火",
            "note": "两件起：免疫火焰与燃烧（仍无法裸身进入超高温岩浆）。",
        },
        pieces=[
            piece(
                "head",
                "防火头盔",
                DEF3,
                "鼓隆城防具店购买。",
                "防火。",
                loc(1674, 2424, "鼓隆城 防具店"),
            ),
            piece(
                "body",
                "防火铠甲",
                DEF3,
                "鼓隆城防具店购买。",
                "防火。",
                loc(1674, 2424, "鼓隆城 防具店"),
            ),
            piece(
                "legs",
                "防火靴",
                DEF3,
                "鼓隆城防具店购买。",
                "防火。",
                loc(1674, 2424, "鼓隆城 防具店"),
            ),
        ],
    )

    add(
        id="zora",
        name="卓拉套装",
        category="探索",
        description="卓拉族护甲，提升游泳能力。",
        upgradable=True,
        upgrades=ZORA_UP,
        set_bonus={
            "level2": "游泳冲刺",
            "note": "两件起：可在水面发动冲刺攻击（消耗精力）。",
        },
        pieces=[
            piece(
                "head",
                "卓拉头盔",
                DEF3,
                "完成卓拉主线「水之神兽瓦·露塔」相关流程后，在卓拉域购买。",
                "游泳速度提升。",
                loc(3279, -430, "卓拉域 防具店"),
            ),
            piece(
                "body",
                "卓拉铠甲",
                DEF3,
                "卓拉域防具店购买。",
                "游泳速度提升；可攀瀑（需精力）。",
                loc(3279, -430, "卓拉域 防具店"),
            ),
            piece(
                "legs",
                "卓拉护胫",
                DEF3,
                "卓拉域防具店购买。",
                "游泳速度提升。",
                loc(3279, -430, "卓拉域 防具店"),
            ),
        ],
    )

    add(
        id="stealth",
        name="潜行套装",
        category="探索",
        description="依盖队风格潜行装，提升隐蔽性。",
        upgradable=True,
        upgrades=STEALTH_UP,
        set_bonus={
            "level2": "潜行强化",
            "note": "两件起：潜行效果进一步提升。",
        },
        pieces=[
            piece(
                "head",
                "潜行面罩",
                DEF2,
                "完成卡卡利科村「潜行套」支线（多座神庙挑战）后购买。",
                "潜行提升。",
                loc(1846, 1007, "卡卡利科村 潜行套商人"),
            ),
            piece(
                "body",
                "潜行胸甲",
                DEF2,
                "潜行套支线奖励后购买。",
                "潜行提升。",
                loc(1846, 1007, "卡卡利科村 潜行套商人"),
            ),
            piece(
                "legs",
                "潜行紧身裤",
                DEF2,
                "潜行套支线奖励后购买。",
                "潜行提升。",
                loc(1846, 1007, "卡卡利科村 潜行套商人"),
            ),
        ],
    )

    add(
        id="climbing",
        name="攀登套装",
        category="探索",
        description="提升攀爬速度与跳跃精力效率。",
        upgradable=True,
        upgrades=CLIMBING_UP,
        set_bonus={
            "level2": "攀爬跳跃",
            "note": "两件起：攀爬跳跃消耗精力减少。",
        },
        pieces=[
            piece(
                "head",
                "攀爬头巾",
                DEF3,
                "完成「攀爬套」相关神庙：Ree Dahee、Tahno O'ah 等，在商店购买部件。",
                "攀爬速度提升。",
                loc(4550, -1680, "双子山 Ree Dahee 神庙附近"),
            ),
            piece(
                "body",
                "攀爬护手",
                DEF3,
                "攀爬套神庙挑战后购买。",
                "攀爬速度提升。",
                loc(3378, 2133, "哈特诺村 攀爬套商人"),
            ),
            piece(
                "legs",
                "攀爬靴",
                DEF3,
                "攀爬套神庙挑战后购买。",
                "攀爬速度提升。",
                loc(3378, 2133, "哈特诺村 攀爬套商人"),
            ),
        ],
    )

    add(
        id="barbarian",
        name="蛮族套装",
        category="战斗",
        description="高攻击向护甲，升级材料需求苛刻。",
        upgradable=True,
        upgrades=BARBARIAN_UP,
        set_bonus={
            "level2": "攻击提升",
            "note": "两件起：攻击力提升（与料理/武器加成叠加）。",
        },
        pieces=[
            piece(
                "head",
                "蛮族头盔",
                DEF3,
                "完成三处与蛮族套相关的试炼神庙后，在相应地点领取。",
                "无单件特技。",
                loc(-2400, 3200, "格鲁德高地 卡·奥耀神庙"),
            ),
            piece(
                "body",
                "蛮族铠甲",
                DEF3,
                "完成「达·卡索」等试炼神庙后领取。",
                "无单件特技。",
                loc(-150, 1900, "初始台地 达·卡索神庙"),
            ),
            piece(
                "legs",
                "蛮族护腿",
                DEF3,
                "完成「卡·姆·耀」试炼神庙后领取。",
                "无单件特技。",
                loc(400, 1200, "海拉鲁城堡 卡·姆·耀神庙"),
            ),
        ],
    )

    add(
        id="radiant",
        name="夜光套装",
        category="战斗",
        description="由夜光石与怪物素材制成，对骷髅系敌人特化。",
        upgradable=True,
        upgrades=RADIANT_UP,
        set_bonus={
            "level2": "骨骼武器强化",
            "note": "两件起：骨骼类武器攻击力提升；单件可让骷髅敌人发光暴露。",
        },
        pieces=[
            piece(
                "head",
                "夜光面罩",
                DEF3,
                "在格鲁德小镇附近的「骷髅」支线完成后，向商人购买。",
                "骷髅敌人持续发光。",
                loc(-3827, 2917, "格鲁德小镇 夜光套商人"),
            ),
            piece(
                "body",
                "夜光服",
                DEF3,
                "夜光套商人处购买。",
                "骷髅敌人持续发光。",
                loc(-3827, 2917, "格鲁德小镇 夜光套商人"),
            ),
            piece(
                "legs",
                "夜光紧身裤",
                DEF3,
                "夜光套商人处购买。",
                "骷髅敌人持续发光。",
                loc(-3827, 2917, "格鲁德小镇 夜光套商人"),
            ),
        ],
    )

    add(
        id="ancient",
        name="古代套装",
        category="战斗",
        description="阿卡莱古代研究所研制，抗守护者并强化古代/守护者武器。",
        upgradable=True,
        upgrades=ANCIENT_UP,
        set_bonus={
            "level2": "古代精通",
            "note": "两件起：古代与守护者系列武器攻击力大幅提升。",
        },
        pieces=[
            piece(
                "head",
                "古代头盔",
                DEF4,
                "在阿卡莱古代研究所用古代材料与卢比兑换（需完成「古代兵装」研究）。",
                "守护者抗性提升。",
                loc(4508, -3160, "阿卡莱古代研究所"),
            ),
            piece(
                "body",
                "古代铠甲",
                DEF4,
                "阿卡莱古代研究所兑换。",
                "守护者抗性提升。",
                loc(4508, -3160, "阿卡莱古代研究所"),
            ),
            piece(
                "legs",
                "古代护胫",
                DEF4,
                "阿卡莱古代研究所兑换。",
                "守护者抗性提升。",
                loc(4508, -3160, "阿卡莱古代研究所"),
            ),
        ],
    )

    add(
        id="wild",
        name="旷野之勇者套装",
        category="奖励",
        description="集齐全部 120 座神庙后，在林克小屋旁宝箱领取；非 amiibo 获取。",
        amiibo=False,
        upgradable=True,
        upgrades=WILD_UP,
        set_bonus={
            "level2": "大师之剑光束强化",
            "note": "两件起：大师之剑剑气伤害提升（需满精力挥剑触发）。",
        },
        pieces=[
            piece(
                "head",
                "旷野之息帽",
                DEF3,
                "完成 120 座神庙后，在哈特诺林克小屋旁宝箱开启。",
                "无单件特技。",
                loc(3378, 2133, "哈特诺 林克小屋"),
            ),
            piece(
                "body",
                "旷野之息服",
                DEF3,
                "120 神庙奖励宝箱。",
                "无单件特技。",
                loc(3378, 2133, "哈特诺 林克小屋"),
            ),
            piece(
                "legs",
                "旷野之息裤",
                DEF3,
                "120 神庙奖励宝箱。",
                "无单件特技。",
                loc(3378, 2133, "哈特诺 林克小屋"),
            ),
        ],
    )

    add(
        id="dark",
        name="暗黑套装",
        category="特殊",
        description="基顿商店兑换，夜间移动更快；不可升级。",
        upgradable=False,
        set_bonus={
            "level2": "夜间移速",
            "note": "两件起：夜间移动速度提升（每件单穿也有夜间加速）。",
        },
        pieces=[
            piece(
                "head",
                "暗黑兜帽",
                [3],
                "在「怪物商店」用怪物素材兑换（需先完成相关支线解锁商店）。",
                "夜间移动速度提升。",
                loc(3500, 2100, "哈特诺附近 怪物商店"),
            ),
            piece(
                "body",
                "暗黑服",
                [3],
                "怪物商店兑换。",
                "夜间移动速度提升。",
                loc(3500, 2100, "怪物商店"),
            ),
            piece(
                "legs",
                "暗黑裤",
                [3],
                "怪物商店兑换。",
                "夜间移动速度提升。",
                loc(3500, 2100, "怪物商店"),
            ),
        ],
    )

    add(
        id="worn",
        name="破旧套装",
        category="剧情",
        description="林克苏醒时的旧衣（仅上衣与裤子两件），无加成也不可升级。",
        upgradable=False,
        set_bonus={"level2": None, "note": "无套装加成；游戏中无对应头饰。"},
        pieces=[
            piece(
                "body",
                "破旧的外衣",
                [1],
                "复苏神庙苏醒时自带；丢失后可在哈特诺林克小屋衣柜找回。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺 林克小屋"),
            ),
            piece(
                "legs",
                "破旧的裤子",
                [1],
                "苏醒时自带；可在林克小屋找回。",
                "无特殊效果。",
                loc(3378, 2133, "哈特诺 林克小屋"),
            ),
        ],
    )

    # —— DLC ——
    add(
        id="royal_guard",
        name="近卫兵套装",
        category="DLC",
        description="扩充票「试炼之剑」DLC 宝箱；高攻低防，不可升级。",
        dlc=True,
        upgradable=False,
        set_bonus={
            "level2": "攻击提升",
            "note": "两件起：攻击力提升（防御低于一般护甲）。",
        },
        pieces=[
            piece(
                "head",
                "近卫帽",
                [4],
                "DLC 宝箱：海拉鲁城堡内近卫室等地。",
                "无单件特技。",
                loc(400, 1200, "海拉鲁城堡 近卫室"),
            ),
            piece(
                "body",
                "近卫服",
                [4],
                "DLC 宝箱：海拉鲁城堡。",
                "无单件特技。",
                loc(400, 1200, "海拉鲁城堡"),
            ),
            piece(
                "legs",
                "近卫靴",
                [4],
                "DLC 宝箱：海拉鲁城堡。",
                "无单件特技。",
                loc(400, 1200, "海拉鲁城堡"),
            ),
        ],
    )

    add(
        id="phantom",
        name="幻影套装",
        category="DLC",
        description="扩充票 DLC 宝箱；不可升级。",
        dlc=True,
        upgradable=False,
        set_bonus={
            "level2": "攻击提升",
            "note": "两件起：攻击力提升。",
        },
        pieces=[
            piece(
                "head",
                "幻影盖侬头盔",
                [4],
                "DLC 宝箱：费罗尼「里·梅·乔」神庙附近等标记点。",
                "无单件特技。",
                loc(2200, -900, "费罗尼 DLC 宝箱"),
            ),
            piece(
                "body",
                "幻影盖侬铠甲",
                [4],
                "DLC 宝箱散布各地。",
                "无单件特技。",
            ),
            piece(
                "legs",
                "幻影盖侬护胫",
                [4],
                "DLC 宝箱散布各地。",
                "无单件特技。",
            ),
        ],
    )

    add(
        id="tingle",
        name="汀空套装",
        category="DLC",
        description="扩充票 DLC 宝箱；汀格尔主题，不可升级。",
        dlc=True,
        upgradable=False,
        set_bonus={
            "level2": None,
            "note": "无战斗套装加成；整套装扮为彩蛋向外观。",
        },
        pieces=[
            piece(
                "head",
                "汀格尔头饰",
                [3],
                "DLC 宝箱：海拉鲁各地地图标记处。",
                "无特殊效果。",
                loc(1800, 1000, "卡卡利科附近 DLC 宝箱"),
            ),
            piece(
                "body",
                "汀格尔上衣",
                [3],
                "DLC 宝箱。",
                "无特殊效果。",
            ),
            piece(
                "legs",
                "汀格尔紧身裤",
                [3],
                "DLC 宝箱。",
                "无特殊效果。",
            ),
        ],
    )

    add(
        id="salvager",
        name="打捞员套装",
        category="联动",
        description="免费更新「异度神剑2」联动任务奖励；提升游泳速度，不可升级。",
        dlc=False,
        upgradable=False,
        set_bonus={
            "level2": "游泳速度",
            "note": "两件起：游泳速度提升。",
        },
        pieces=[
            piece(
                "head",
                "打捞员头盔",
                [3],
                "DLC 宝箱：拉聂尔相关标记点。",
                "游泳速度提升。",
                loc(3200, -500, "拉聂尔 DLC 宝箱"),
            ),
            piece(
                "body",
                "打捞员背心",
                [3],
                "DLC 宝箱。",
                "游泳速度提升。",
            ),
            piece(
                "legs",
                "打捞员长裤",
                [3],
                "DLC 宝箱。",
                "游泳速度提升。",
            ),
        ],
    )

    # —— Amiibo（可在大精灵处强化）——
    # 套装效果需三件均强化至 ★★ 以上并同时穿戴。
    amiibo_defs = [
        (
            "hero",
            "初始之勇者套装",
            "8-Bit Link / 经典林克 amiibo 随机掉落部件。",
            {"level2": "大师之剑光束强化", "note": "三件均★2+且穿戴：大师之剑剑气强化。"},
            ("初始之勇者的帽子", "初始之勇者的服装", "初始之勇者的裤子"),
            amiibo_hero_up("ruby", "红宝石"),
        ),
        (
            "time",
            "时之勇者套装",
            "《时之笛》林克 amiibo 随机掉落部件。",
            {"level2": "大师之剑光束强化", "note": "三件均★2+且穿戴：大师之剑剑气强化。"},
            ("时之勇者的帽子", "时之勇者的服装", "时之勇者的裤子"),
            amiibo_hero_up("amber", "琥珀"),
        ),
        (
            "wind",
            "风之勇者套装",
            "《风之律动》林克 / Toon Link amiibo 随机掉落部件。",
            {"level2": "大师之剑光束强化", "note": "三件均★2+且穿戴：大师之剑剑气强化。"},
            ("风之勇者的帽子", "风之勇者的服装", "风之勇者的裤子"),
            amiibo_hero_up("opal", "蛋白石"),
        ),
        (
            "twilight",
            "黄昏之勇者套装",
            "《黄昏公主》林克 / 狼林克 amiibo 随机掉落部件。",
            {"level2": "大师之剑光束强化", "note": "三件均★2+且穿戴：大师之剑剑气强化。"},
            ("黄昏之勇者的帽子", "黄昏之勇者的服装", "黄昏之勇者的裤子"),
            amiibo_hero_up("topaz", "黄玉"),
        ),
        (
            "sky",
            "天空之勇者套装",
            "《天空之剑》林克 amiibo 随机掉落部件。",
            {"level2": "大师之剑光束强化", "note": "三件均★2+且穿戴：大师之剑剑气强化。"},
            ("天空之勇者的帽子", "天空之勇者的服装", "天空之勇者的裤子"),
            amiibo_hero_up("sapphire", "蓝宝石"),
        ),
        (
            "fierce_deity",
            "鬼神套装",
            "《穆修拉的假面》林克 amiibo 随机掉落部件。",
            {
                "level2": "蓄力攻击精力减少",
                "note": "三件均★2+且穿戴：蓄力攻击精力消耗减少；各件自带攻击力提升。",
            },
            ("鬼神的面具", "鬼神的服装", "鬼神的靴子"),
            FIERCE_UP,
        ),
    ]
    for aid, aname, how, bonus, names, upgrades in amiibo_defs:
        h, b, l = names
        fx = "攻击力提升。" if aid == "fierce_deity" else "无单件特技。"
        add(
            id=aid,
            name=aname,
            category="Amiibo",
            description=how + " 可在大精灵之泉强化（需星之碎片等材料）。",
            amiibo=True,
            upgradable=True,
            upgrades=upgrades,
            set_bonus=bonus,
            pieces=[
                piece("head", h, DEF3, how, fx),
                piece("body", b, DEF3, how, fx),
                piece("legs", l, DEF3, how, fx),
            ],
        )

    apply_acquire_fixes()


# 获取方式与坐标校正（覆盖上文占位文案）
# how: str；loc: dict|None；可选 name/effect/description 仅在需要时覆盖
def apply_acquire_fixes() -> None:
    # (howToGet, location_or_None, optional_name, optional_effect)
    fixes: dict[str, tuple] = {
        # 海利亚：卡卡利科「魔女」/哈特诺「文特斯」；裤子亦可在初始台地神庙旁宝箱
        "hylian_head": (
            "卡卡利科村防具店「魔女」或哈特诺村「文特斯服装店」购买（60 卢比）。之后也可在塔利镇向格兰特回购。",
            loc(1846, 1007, "卡卡利科村 魔女防具店"),
            "海利亚兜帽",
            "无",
        ),
        "hylian_body": (
            "卡卡利科村「魔女」或哈特诺村「文特斯服装店」购买（120 卢比）。之后也可在塔利镇向格兰特回购。",
            loc(3378, 2133, "哈特诺村 文特斯服装店"),
            "海利亚服",
            "无",
        ),
        "hylian_legs": (
            "初始台地时之神殿附近宝箱可得一件；也可在卡卡利科/哈特诺防具店购买（90 卢比）。之后可在塔利镇回购。",
            loc(-700, 1600, "初始台地 时之神殿附近宝箱"),
            "海利亚裤子",
            "无",
        ),
        # 士兵：仅哈特诺文特斯
        "soldier_head": (
            "哈特诺村「文特斯服装店」购买（180 卢比）。之后可在塔利镇向格兰特回购。",
            loc(3378, 2133, "哈特诺村 文特斯服装店"),
            "士兵头盔",
            "无",
        ),
        "soldier_body": (
            "哈特诺村「文特斯服装店」购买（250 卢比）。之后可在塔利镇向格兰特回购。",
            loc(3378, 2133, "哈特诺村 文特斯服装店"),
            "士兵铠甲",
            "无",
        ),
        "soldier_legs": (
            "哈特诺村「文特斯服装店」购买（200 卢比）。之后可在塔利镇向格兰特回购。",
            loc(3378, 2133, "哈特诺村 文特斯服装店"),
            "士兵护胫",
            "无",
        ),
        # 利特防寒
        "snowquill_head": (
            "利特村防具店「厚脸皮」购买（1000 卢比）。之后可在塔利镇回购。",
            loc(-3615, -1815, "利特村 厚脸皮防具店"),
            "利特的头饰",
            "耐寒",
        ),
        "snowquill_body": (
            "利特村防具店「厚脸皮」购买（600 卢比）。之后可在塔利镇回购。",
            loc(-3615, -1815, "利特村 厚脸皮防具店"),
            "利特的羽绒服",
            "耐寒",
        ),
        "snowquill_legs": (
            "利特村防具店「厚脸皮」购买（900 卢比）。之后可在塔利镇回购。",
            loc(-3615, -1815, "利特村 厚脸皮防具店"),
            "利特的羽绒服裤子",
            "耐寒",
        ),
        # 沙漠服：格鲁德秘密俱乐部（非正面防具店）
        "desert_voe_head": (
            "格鲁德小镇「时尚热情」后门秘密俱乐部购买（需先敲后门并输入口令；450 卢比）。也可在塔利镇向格兰特购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "沙漠头巾",
            "耐热",
        ),
        "desert_voe_body": (
            "格鲁德小镇秘密俱乐部购买（1300 卢比），或塔利镇格兰特处购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "沙漠护肩",
            "耐热",
        ),
        "desert_voe_legs": (
            "格鲁德小镇秘密俱乐部购买（650 卢比），或塔利镇格兰特处购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "沙漠裤子",
            "耐热",
        ),
        # 格鲁德瓦伊装：时尚热情（进入格鲁德小镇主线）
        "gerudo_head": (
            "主线「禁入之城」：在格鲁德小镇入口外的「时尚热情」购买格鲁德面纱（180 卢比），凑齐三件瓦伊装方可进城。",
            loc(-3900, 2950, "格鲁德小镇入口 时尚热情"),
            "格鲁德面纱",
            "耐热；三件齐全可伪装成瓦伊进城",
        ),
        "gerudo_body": (
            "「时尚热情」购买格鲁德上衣（180 卢比）。须与面纱、灯笼裤同时穿戴才能进入格鲁德小镇。",
            loc(-3900, 2950, "格鲁德小镇入口 时尚热情"),
            "格鲁德上衣",
            "耐热；三件齐全可伪装成瓦伊进城",
        ),
        "gerudo_legs": (
            "「时尚热情」购买格鲁德灯笼裤（180 卢比）。须与面纱、上衣同时穿戴才能进城。",
            loc(-3900, 2950, "格鲁德小镇入口 时尚热情"),
            "格鲁德灯笼裤",
            "耐热；三件齐全可伪装成瓦伊进城",
        ),
        # 橡胶
        "rubber_head": (
            "支线「雷鸣吸引器」：在费罗尼湖畔驿站与吉斯托对话并完成任务后获得橡胶头盔。",
            loc(1560, 3230, "费罗尼 湖畔驿站"),
            "橡胶头盔",
            "抗电",
        ),
        "rubber_body": (
            "完成「雷鸣高原的试炼」神庙任务后，进入利奇兰地区「托·亚萨神庙」宝箱取得橡胶铠甲。",
            loc(-1200, 850, "利奇兰 托·亚萨神庙"),
            "橡胶铠甲",
            "抗电",
        ),
        "rubber_legs": (
            "完成「雷击试炼」神庙任务后，进入费罗尼「丘卡·纳塔神庙」宝箱取得橡胶紧身裤。",
            loc(2000, 3350, "费罗尼 丘卡·纳塔神庙"),
            "橡胶紧身裤",
            "抗电",
        ),
        # 防火
        "flamebreaker_head": (
            "鼓隆城防具店「破破烂烂」购买（2000 卢比）。之后可在塔利镇回购。",
            loc(1674, 2424, "鼓隆城 破破烂烂"),
            "防火石盔",
            "防火",
        ),
        "flamebreaker_body": (
            "鼓隆主线中可由布尔德赠送一件；也可在鼓隆城「破破烂烂」购买（600 卢比）。之后可在塔利镇回购。",
            loc(1674, 2424, "鼓隆城 破破烂烂"),
            "防火石铠",
            "防火",
        ),
        "flamebreaker_legs": (
            "鼓隆城「破破烂烂」购买（700 卢比）。之后可在塔利镇回购。",
            loc(1674, 2424, "鼓隆城 破破烂烂"),
            "防火石靴",
            "防火",
        ),
        # 卓拉
        "zora_head": (
            "卓拉领地北侧「托托湖」水下金属宝箱（需磁力抓取）。石碑有提示。",
            loc(3600, -900, "托托湖"),
            "卓拉头盔",
            "游泳速度提升；可在水中旋转攻击",
        ),
        "zora_body": (
            "抵达卓拉领地后与多莱凡王对话获得（主线「水之神兽瓦·露塔」相关）。",
            loc(3279, -430, "卓拉领地 王座"),
            "卓拉铠甲",
            "游泳速度提升；可攀瀑",
        ),
        "zora_legs": (
            "支线「莱尼尔观察日记」：卓拉领地二层东桥附近与拉弗拉特对话，拍摄普莱姆斯山莱尼尔照片后获得。需先解锁照相机。",
            loc(3300, -400, "卓拉领地 拉弗拉特"),
            "卓拉护胫",
            "游泳速度提升",
        ),
        # 潜行：直接购买，无支线门槛
        "stealth_head": (
            "卡卡利科村防具店「魔女」直接购买（500 卢比）。之后可在塔利镇回购。",
            loc(1846, 1007, "卡卡利科村 魔女防具店"),
            "潜行面罩",
            "潜行提升",
        ),
        "stealth_body": (
            "卡卡利科村「魔女」直接购买（700 卢比）。之后可在塔利镇回购。",
            loc(1846, 1007, "卡卡利科村 魔女防具店"),
            "潜行护胸",
            "潜行提升",
        ),
        "stealth_legs": (
            "卡卡利科村「魔女」直接购买（600 卢比）。之后可在塔利镇回购。",
            loc(1846, 1007, "卡卡利科村 魔女防具店"),
            "潜行紧身裤",
            "潜行提升",
        ),
        # 攀登：三座神庙宝箱
        "climbing_head": (
            "双子山之间「利·达希神庙」宝箱取得攀登头巾。",
            loc(1700, 1950, "利·达希神庙"),
            "攀登头巾",
            "攀爬速度提升",
        ),
        "climbing_body": (
            "哈特诺塔东南方海上浮岛「查斯·克塔神庙」宝箱取得攀登护手。",
            loc(4500, 2850, "查斯·克塔神庙"),
            "攀登护手",
            "攀爬速度提升",
        ),
        "climbing_legs": (
            "完成支线「雪松的秘密」后，在哈特诺研究所东北「塔诺·奥阿神庙」宝箱取得攀登靴。",
            loc(4000, 1500, "塔诺·奥阿神庙"),
            "攀登靴",
            "攀爬速度提升",
        ),
        # 蛮族：三处迷宫神庙
        "barbarian_head": (
            "阿卡拉「洛梅伊迷宫岛」尽头「图·卡洛神庙」宝箱取得蛮族头盔。",
            loc(4650, -3720, "洛梅伊迷宫岛 图·卡洛神庙"),
            "蛮族头盔",
            "攻击力提升",
        ),
        "barbarian_body": (
            "格鲁德沙漠「南洛梅伊迷宫」尽头「迪拉·马格神庙」宝箱取得蛮族铠甲。",
            loc(-1800, 3530, "南洛梅伊迷宫 迪拉·马格神庙"),
            "蛮族铠甲",
            "攻击力提升",
        ),
        "barbarian_legs": (
            "赫布拉「北洛梅伊迷宫」尽头「卡扎·托基神庙」宝箱取得蛮族绑腿。",
            loc(-820, -3420, "北洛梅伊迷宫 卡扎·托基神庙"),
            "蛮族绑腿",
            "攻击力提升",
        ),
        # 夜光：秘密俱乐部
        "radiant_head": (
            "格鲁德小镇秘密俱乐部购买（800 卢比）。口令后门进入；也可在塔利镇向格兰特购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "夜光面罩",
            "使骷髅敌人发光",
        ),
        "radiant_body": (
            "格鲁德小镇秘密俱乐部购买（800 卢比），或塔利镇格兰特处购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "夜光服",
            "使骷髅敌人发光",
        ),
        "radiant_legs": (
            "格鲁德小镇秘密俱乐部购买（800 卢比），或塔利镇格兰特处购买。",
            loc(-3827, 2917, "格鲁德小镇 秘密俱乐部"),
            "夜光紧身裤",
            "使骷髅敌人发光",
        ),
        # 古代
        "ancient_head": (
            "完成罗贝里相关流程后，在阿卡拉古代研究所向樱桃用古代材料+卢比兑换（2000 卢比等）。",
            loc(4508, -3160, "阿卡拉古代研究所"),
            "古代头盔",
            "守护者抗性",
        ),
        "ancient_body": (
            "阿卡拉古代研究所向樱桃兑换（5000 卢比等材料）。",
            loc(4508, -3160, "阿卡拉古代研究所"),
            "古代铠甲",
            "守护者抗性",
        ),
        "ancient_legs": (
            "阿卡拉古代研究所向樱桃兑换（3000 卢比等材料）。",
            loc(4508, -3160, "阿卡拉古代研究所"),
            "古代护胫",
            "守护者抗性",
        ),
        # 旷野：遗忘神殿，非林克小屋
        "wild_head": (
            "完成全部 120 座古代神庙后触发「僧侣的赠礼」：在塔邦达「遗忘神殿」三座宝箱之一取得。",
            loc(-1100, -1500, "遗忘神殿"),
            "旷野之勇者的帽子",
            "无",
        ),
        "wild_body": (
            "完成 120 座神庙后，于遗忘神殿宝箱取得旷野之勇者的服装。",
            loc(-1100, -1500, "遗忘神殿"),
            "旷野之勇者的服装",
            "无",
        ),
        "wild_legs": (
            "完成 120 座神庙后，于遗忘神殿宝箱取得旷野之勇者的裤子。",
            loc(-1100, -1500, "遗忘神殿"),
            "旷野之勇者的裤子",
            "无",
        ),
        # 暗黑：基尔顿
        "dark_head": (
            "夜间在各地出没的怪物商人基尔顿「牙与骨」处以魔物点数兑换（999 魔物币）。据点在阿卡拉骷髅湖。",
            loc(3900, -2800, "阿卡拉 骷髅湖（基尔顿）"),
            "暗黑兜帽",
            "无",
        ),
        "dark_body": (
            "基尔顿「牙与骨」以魔物点数兑换（999 魔物币）。",
            loc(3900, -2800, "阿卡拉 骷髅湖（基尔顿）"),
            "暗黑服",
            "无",
        ),
        "dark_legs": (
            "基尔顿「牙与骨」以魔物点数兑换（999 魔物币）。",
            loc(3900, -2800, "阿卡拉 骷髅湖（基尔顿）"),
            "暗黑裤",
            "无",
        ),
        # 破旧
        "worn_body": (
            "复苏神庙苏醒时自带「旧衬衫」。卖掉后可在塔利镇格兰特处回购；购入哈特诺林克之屋后也可在屋内相关位置保管。",
            loc(-1000, 1900, "复苏神庙"),
            "旧衬衫",
            "无",
        ),
        "worn_legs": (
            "复苏神庙苏醒时自带「破旧的裤子」。卖掉后可在塔利镇格兰特处回购。",
            loc(-1000, 1900, "复苏神庙"),
            "破旧的裤子",
            "无",
        ),
        # 近卫兵 DLC
        "royal_guard_head": (
            "扩充票 DLC：海拉鲁城堡「圣殿」上方房间宝箱。之后可在塔利镇格兰特处回购。",
            loc(-250, -550, "海拉鲁城堡 圣殿上方"),
            "近卫兵的帽子",
            "无",
        ),
        "royal_guard_body": (
            "扩充票 DLC：海拉鲁城堡餐厅附近小房间宝箱。之后可在塔利镇回购。",
            loc(-220, -350, "海拉鲁城堡 餐厅附近"),
            "近卫兵的服装",
            "无",
        ),
        "royal_guard_legs": (
            "扩充票 DLC：海拉鲁城堡「近卫室」宝箱。之后可在塔利镇回购。",
            loc(-150, -250, "海拉鲁城堡 近卫室"),
            "近卫兵的靴子",
            "无",
        ),
        # 幻影（非幻影盖侬）
        "phantom_head": (
            "扩充票「英杰们的诗篇」相关地图：竞技场遗迹一楼宝箱。之后可在塔利镇回购。",
            loc(-1150, 1250, "竞技场遗迹"),
            "幻影头盔",
            "无",
        ),
        "phantom_body": (
            "扩充票：海拉鲁城堡南侧「圣域遗迹」宝箱。之后可在塔利镇回购。",
            loc(-50, 450, "圣域遗迹"),
            "幻影铠甲",
            "无",
        ),
        "phantom_legs": (
            "扩充票：海拉鲁驻屯地遗迹宝箱。之后可在塔利镇回购。",
            loc(-450, 750, "海拉鲁驻屯地遗迹"),
            "幻影护胫",
            "无",
        ),
        # 汀空
        "tingle_head": (
            "扩充票：科洛莫湖西北「交易所遗迹」宝箱取得汀空风帽。之后可在塔利镇回购。",
            loc(-650, 1550, "交易所遗迹"),
            "汀空的风帽",
            "无",
        ),
        "tingle_body": (
            "扩充票：海拉鲁城堡西北岛「城下镇监狱」宝箱取得汀空衬衫。之后可在塔利镇回购。",
            loc(-400, -200, "城下镇监狱"),
            "汀空的衬衫",
            "无",
        ),
        "tingle_legs": (
            "扩充票：中央塔与卡亚·万神庙之间「马贝村遗迹」宝箱取得汀空紧身裤。之后可在塔利镇回购。",
            loc(150, 900, "马贝村遗迹"),
            "汀空的紧身裤",
            "无",
        ),
        # 打捞员：异度神剑 2 联动任务
        "salvager_head": (
            "免费更新联动任务「异度神剑2」：按驿站旅客提示，在赫布拉相关发光处取得打捞员头饰。之后可在塔利镇回购。",
            loc(-3200, -2500, "赫布拉（联动发光点）"),
            "打捞员头饰",
            "游泳速度提升",
        ),
        "salvager_body": (
            "联动任务「异度神剑2」：在费罗尼相关发光处取得打捞员背心。之后可在塔利镇回购。",
            loc(1800, 3000, "费罗尼（联动发光点）"),
            "打捞员背心",
            "游泳速度提升",
        ),
        "salvager_legs": (
            "联动任务「异度神剑2」：在格鲁德峡谷相关发光处取得打捞员裤子。之后可在塔利镇回购。",
            loc(-2800, 2000, "格鲁德峡谷（联动发光点）"),
            "打捞员裤子",
            "游泳速度提升",
        ),
        # Amiibo（精确对应）
        "hero_head": (
            "使用「8-Bit 林克 / 经典林克」amiibo 扫描，有概率掉落；已拥有后也可在塔利镇格兰特处购买。",
            None,
            "初始之勇者的帽子",
            "无",
        ),
        "hero_body": (
            "「8-Bit 林克 / 经典林克」amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "初始之勇者的服装",
            "无",
        ),
        "hero_legs": (
            "「8-Bit 林克 / 经典林克」amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "初始之勇者的裤子",
            "无",
        ),
        "time_head": (
            "使用《时之笛》林克 amiibo 扫描掉落；之后可在塔利镇购买。",
            None,
            "时之勇者的帽子",
            "无",
        ),
        "time_body": (
            "《时之笛》林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "时之勇者的服装",
            "无",
        ),
        "time_legs": (
            "《时之笛》林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "时之勇者的裤子",
            "无",
        ),
        "wind_head": (
            "使用《风之律动》林克或「卡通林克」amiibo 扫描掉落；之后可在塔利镇购买。",
            None,
            "风之勇者的帽子",
            "无",
        ),
        "wind_body": (
            "《风之律动》林克 / 卡通林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "风之勇者的服装",
            "无",
        ),
        "wind_legs": (
            "《风之律动》林克 / 卡通林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "风之勇者的裤子",
            "无",
        ),
        "twilight_head": (
            "使用《黄昏公主》林克或狼林克 amiibo 扫描掉落；之后可在塔利镇购买。",
            None,
            "黄昏之勇者的帽子",
            "无",
        ),
        "twilight_body": (
            "《黄昏公主》林克 / 狼林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "黄昏之勇者的服装",
            "无",
        ),
        "twilight_legs": (
            "《黄昏公主》林克 / 狼林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "黄昏之勇者的裤子",
            "无",
        ),
        "sky_head": (
            "使用《天空之剑》林克 amiibo 扫描掉落；之后可在塔利镇购买。",
            None,
            "天空之勇者的帽子",
            "无",
        ),
        "sky_body": (
            "《天空之剑》林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "天空之勇者的服装",
            "无",
        ),
        "sky_legs": (
            "《天空之剑》林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "天空之勇者的裤子",
            "无",
        ),
        "fierce_deity_head": (
            "使用《穆修拉的假面》林克 / 鬼神林克 amiibo 扫描掉落；之后可在塔利镇购买。",
            None,
            "鬼神的面具",
            "攻击力提升",
        ),
        "fierce_deity_body": (
            "《穆修拉的假面》林克 / 鬼神林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "鬼神的服装",
            "攻击力提升",
        ),
        "fierce_deity_legs": (
            "《穆修拉的假面》林克 / 鬼神林克 amiibo 随机掉落；之后可在塔利镇购买。",
            None,
            "鬼神的靴子",
            "攻击力提升",
        ),
    }

    set_desc = {
        "wild": "完成全部 120 座古代神庙后，在遗忘神殿开启「僧侣的赠礼」宝箱获得；非 amiibo。",
        "desert_voe": "格鲁德小镇秘密俱乐部（时尚热情后门）出售的耐热男性装；口令进入。",
        "radiant": "格鲁德小镇秘密俱乐部出售；对骷髅敌人与骨制武器有特化效果。",
        "stealth": "卡卡利科村「魔女」防具店直接出售，无需完成支线。",
        "climbing": "分别藏于利·达希、查斯·克塔、塔诺·奥阿三座神庙宝箱。",
        "barbarian": "分别藏于洛梅伊三座迷宫尽头神庙宝箱。",
        "rubber": "头盔来自湖畔驿站支线；铠甲/紧身裤分别来自托·亚萨与丘卡·纳塔神庙。",
        "zora": "铠甲由多莱凡王赠送；头盔在托托湖；护胫为莱尼尔观察支线奖励。",
        "phantom": "扩充票 DLC：竞技场遗迹、圣域遗迹、海拉鲁驻屯地遗迹宝箱（幻影套，非幻影盖侬）。",
        "salvager": "免费更新「异度神剑2」联动任务奖励；按驿站提示寻找发光点。",
        "gerudo": "在格鲁德小镇入口「时尚热情」购买三件瓦伊装，用于主线进城；不可强化。",
    }

    by_id = {s["id"]: s for s in SETS}
    for sid, desc in set_desc.items():
        if sid in by_id:
            by_id[sid]["description"] = desc

    for s in SETS:
        for p in s["pieces"]:
            fix = fixes.get(p["id"])
            if not fix:
                continue
            how, location, name, effect = fix
            p["howToGet"] = how
            if name:
                p["name"] = name
            if effect:
                p["effect"] = effect
            if location is None:
                p.pop("location", None)
            else:
                p["location"] = location


def main() -> None:
    build_sets()
    piece_count = sum(len(s["pieces"]) for s in SETS)
    payload = {
        "meta": {
            "game": "botw",
            "setCount": len(SETS),
            "pieceCount": piece_count,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "sets": SETS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"写入 {OUT.relative_to(ROOT)}")
    print(f"套装数: {len(SETS)}，部件数: {piece_count}")


if __name__ == "__main__":
    main()
