#!/usr/bin/env python3
"""fabulous-rules: turn a hardware profile into the installer's choices.

Input: profile JSON from fabulous-probe. Output: decision JSON.
All thresholds and wording live in rules.yaml.

Version 1 scope (DECISIONS.md): Fabulous OS replaces whatever is on the chosen
disk. Keeping another system beside it is not offered.
"""
import json
import os
import sys

import yaml

DEFAULT_RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.yaml")


def load_rules(path=DEFAULT_RULES):
    with open(path) as f:
        return yaml.safe_load(f)


def choose_model(profile, rules):
    notes = []
    mem = profile["memory"]["total_gb"]
    model = "none"
    for band in rules["memory_bands"]:
        if band["below_gb"] is None or mem < band["below_gb"]:
            model = band["model"]
            if band["note"]:
                notes.append(band["note"])
            break
    if model != "none" and not profile["cpu"]["avx2"]:
        ladder = rules["model_ladder"]
        i = min(ladder.index(model) + rules["no_avx2"]["step_down"], len(ladder) - 1)
        model = ladder[i]
        if model != "none":
            notes.append(rules["no_avx2"]["note"])
        else:
            notes.append(rules["memory_bands"][0]["note"])
    return model, notes


def target_disks(profile):
    """Disks Fabulous OS may be installed on: never the stick, never removable."""
    return [d for d in profile["disks"] if not d["is_live_medium"] and not d["removable"]]


def choose_app_set(profile, disk, rules):
    a = rules["app_sets"]
    small = (profile["memory"]["total_gb"] < a["office_if_memory_below_gb"]
             or (disk is not None and disk["size_gb"] < a["office_if_disk_below_gb"]))
    return ("office", a["office_note"]) if small else ("full", None)


def refusals(profile, disk, rules):
    s = rules["safety"]
    out = []
    if profile["arch"] not in rules["supported_arch"]:
        out.append("This USB stick is for PCs. It cannot install on this kind of computer.")
    if disk is None:
        out.append("No internal disk was found to install Fabulous OS on.")
    elif disk["size_gb"] < s["min_disk_gb"]:
        out.append(f"The disk is too small. Fabulous OS needs at least {s['min_disk_gb']} GB.")
    p = profile.get("power", {})
    if p.get("on_battery") and (p.get("percent") or 0) < s["min_battery_percent"]:
        out.append("The battery is low. Plug the computer in before installing.")
    return out


NOMINAL_GB = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]


def nominal_memory_gb(total_gb):
    """Memory as sold ("16 GB"), since the system always reports a little less."""
    for size in NOMINAL_GB:
        if total_gb <= size:
            return size
    return round(total_gb)


def decide(profile, rules=None):
    rules = rules or load_rules()
    disks = target_disks(profile)
    disk = max(disks, key=lambda d: d["size_gb"]) if disks else None
    model, notes = choose_model(profile, rules)
    app_set, app_note = choose_app_set(profile, disk, rules)
    cpu = profile["cpu"]
    welcome = (f"This computer has {nominal_memory_gb(profile['memory']['total_gb'])} GB of memory and a "
               f"{cpu['cores']}-core processor. ")
    label = rules["models"][model]["label"]
    welcome += (f"Do you want to install Fabulous OS with {label}?" if label
                else "Do you want to install Fabulous OS?")
    return {
        "model": model,
        "model_label": label,
        "model_notes": notes,
        "app_set": app_set,
        "app_set_note": app_note,
        "target_disk": disk["name"] if disk else None,
        "target_disk_choices": [d["name"] for d in disks],
        # Replacing erases the disk, so BitLocker and Fast Startup do not block it;
        # the installer still requires the typed DELETE confirmation.
        "will_erase_windows": bool(profile.get("windows", {}).get("present")),
        "refusals": refusals(profile, disk, rules),
        "welcome_text": welcome,
    }


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    path = argv[0] if argv else "/run/fabulous/profile.json"
    with open(path) as f:
        profile = json.load(f)
    print(json.dumps(decide(profile), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
