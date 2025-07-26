from utils.constraints import TYPE_EFFECTIVENESS, TYPE_EMOJIS
from typing import List

def format_abilities(raw: List[str]) -> str:
    return ", ".join(
        f"h:{a[2:].title().replace(' ', '-')}"
        if a.startswith("h:") else a.title().replace(' ', '-')
        for a in raw
    ) or "N/A"

def group_spawns(spawns: list[dict]) -> list[dict]:
    def simplified_key(spawn: dict) -> tuple:
        cond = spawn.get("condition", {})
        anticond = spawn.get("anticondition", {})
        return (
            spawn.get("context"),
            spawn.get("level"),
            spawn.get("bucket"),
            tuple(sorted(cond.get("biomes", []))),
            tuple(sorted(anticond.get("biomes", []))),
        )

    grouped = {}
    for spawn in spawns:
        key = simplified_key(spawn)
        if key not in grouped:
            grouped[key] = {
                "base": spawn,
                "variants": [],
                "extra_conditions": []
            }
        grouped[key]["extra_conditions"].append(spawn.get("condition", {}))
        grouped[key]["variants"].append({
            "weight": spawn.get("weight", 0),
            "preset": spawn.get("presets", []),
            "id": spawn.get("id")
        })
    return list(grouped.values())


def get_type_effectiveness(primary: str, secondary: str = "") -> dict:
    effectiveness = {}
    all_types = TYPE_EFFECTIVENESS.keys()
    for attacking in all_types:
        multiplier = 1.0
        if primary in TYPE_EFFECTIVENESS and attacking in TYPE_EFFECTIVENESS[primary]:
            multiplier *= TYPE_EFFECTIVENESS[primary][attacking]
        if secondary and secondary in TYPE_EFFECTIVENESS and attacking in TYPE_EFFECTIVENESS[secondary]:
            multiplier *= TYPE_EFFECTIVENESS[secondary][attacking]
        if multiplier == 2.0 or multiplier == 4.0:
            effectiveness.setdefault("weak", []).append(attacking)
        elif multiplier == 0.5 or multiplier == 0.25:
            effectiveness.setdefault("resist", []).append(attacking)
        elif multiplier == 0:
            effectiveness.setdefault("immune", []).append(attacking)
    return effectiveness


def emoji_list(types: list[str]) -> str:
    return " ".join(TYPE_EMOJIS.get(t, t.title()) for t in types)


def format_effectiveness(primary: str, secondary: str = "") -> str:
    eff = get_type_effectiveness(primary, secondary)
    lines = []
    if "weak" in eff:
        lines.append(f"**Weak:** {emoji_list(eff['weak'])}")
    if "resist" in eff:
        lines.append(f"**Resist:** {emoji_list(eff['resist'])}")
    if "immune" in eff:
        lines.append(f"**Immune:** {emoji_list(eff['immune'])}")
    return "\n".join(lines)


def format_evolutions(evolutions: list[dict]) -> str:
    lines = []
    for evo in evolutions:
        result = evo.get("result", "Unknown").capitalize()
        reqs = evo.get("requirements", [])
        level = evo.get("level")
        if level:
            lines.append(f"• {result} (Lv. {level})")
            continue
        level_req = next((r for r in reqs if r.get("variant") == "level" and "minLevel" in r), None)
        if level_req:
            lines.append(f"• {result} (Lv. {level_req['minLevel']})")
            continue
        ctx = evo.get("requiredContext")
        if ctx:
            ctx_str = ctx.split(":")[-1].replace("_", " ").title()
            lines.append(f"• {result} ({ctx_str})")
            continue
        parts = []
        for r in reqs:
            match r.get("variant"):
                case "friendship":
                    parts.append("Friendship")
                case "time_range":
                    parts.append(r.get("range", "").capitalize())
                case "has_move_type":
                    parts.append(f"{r.get('type', '').capitalize()} move")
                case "held_item":
                    item = r.get("item", "").split(":")[-1].replace("_", " ").title()
                    parts.append(f"Held {item}")
                case "item":
                    item = r.get("item", "").split(":")[-1].replace("_", " ").title()
                    parts.append(f"Use {item}")
        lines.append(f"• {result} ({', '.join(parts)})" if parts else f"• {result}")
    return "**Evolution:**\n" + "\n".join(lines) if lines else ""

def format_drops(drops: dict) -> str:
    entries = drops.get("entries", [])
    if not entries:
        return "None"
    lines = []
    for d in entries:
        item = d.get("item")
        if not item:
            continue
        suffix = ""
        if "percentage" in d:
            suffix = f" ({d['percentage']}%)"
        elif "quantityRange" in d:
            suffix = f" ({d['quantityRange']}x)"
        lines.append(f"• `{item}`{suffix}")
    return "\n".join(lines)


def format_biomes(biomes: list[str]) -> str:
    return "\n".join(f"• `{b}`" for b in biomes) if biomes else "• N/A"


def format_conditions(cond: dict, anticond: dict) -> list[str]:
    lines = []

    if "minSkyLight" in cond or "maxSkyLight" in cond or "canSeeSky" in cond:
        min_sl = cond.get("minSkyLight", 0)
        max_sl = cond.get("maxSkyLight", 15)
        see_sky = cond.get("canSeeSky", False)
        lines.append(f"Sky Light: `{min_sl}–{max_sl}` / `{'Yes' if see_sky else 'No'}`")

    if "minLureLevel" in cond:
        lines.append(f"Min Lure Level: `{cond['minLureLevel']}`")

    y_parts = []
    if "minY" in cond:
        y_parts.append(f"Min Y: `{cond['minY']}`")
    if "maxY" in cond:
        y_parts.append(f"Max Y: `{cond['maxY']}`")
    if y_parts:
        lines.append(", ".join(y_parts))

    if "timeRange" in cond:
        lines.append(f"Time: `{cond['timeRange']}`")

    if "neededNearbyBlocks" in cond:
        blocks = "\n".join(f"• `{b}`" for b in cond["neededNearbyBlocks"])
        lines.append(f"Nearby Blocks:\n{blocks}")

    if "structures" in cond:
        structures = "\n".join(f"• `{s}`" for s in cond["structures"])
        lines.append(f"Structures:\n{structures}")

    if "structures" in anticond:
        blocked = "\n".join(f"• `{s}`" for s in anticond["structures"])
        lines.append(f"Excluded Structures:\n{blocked}")

    return lines

def format_multipliers(base: dict) -> list[str]:
    lines = []
    wm_all = []

    if base.get("weightMultiplier"):
        wm_all.append(base["weightMultiplier"])
    if base.get("weightMultipliers"):
        wm_all.extend(base["weightMultipliers"])

    for wm in wm_all:
        cond = wm.get("condition", {})
        cond_parts = []
        for k, v in cond.items():
            label = k.replace("_", " ").title()
            if isinstance(v, list):
                cond_parts.append(f"{label}: {', '.join(f'`{i}`' for i in v)}")
            else:
                cond_parts.append(f"{label}: `{v}`")
        lines.append(f"• ×{wm['multiplier']} if " + ", ".join(cond_parts))

    return lines