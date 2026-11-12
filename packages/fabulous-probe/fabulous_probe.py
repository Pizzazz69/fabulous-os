#!/usr/bin/env python3
"""fabulous-probe: read this computer's hardware once, change nothing.

Writes one JSON profile (default /run/fabulous/profile.json).
Never mounts anything read-write, never writes to a disk, never uses the network.

The parse_* functions take text and return data, so they can be tested with
recorded output from real machines (tests/fixtures).
"""
import argparse
import json
import os
import platform
import re
import subprocess
import sys

GIB = 1024 ** 3


# ---------- parsers (pure functions) ----------

def parse_cpuinfo(text):
    """Parse /proc/cpuinfo text."""
    model = None
    flags = set()
    threads = 0
    core_ids = set()
    physical = "0"
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key == "processor":
            threads += 1
        elif key == "model name" and model is None:
            model = value
        elif key == "physical id":
            physical = value
        elif key == "core id":
            core_ids.add((physical, value))
        elif key == "flags" and not flags:
            flags = set(value.split())
    cores = len(core_ids) or threads
    return {
        "model": model or "Unknown processor",
        "cores": cores,
        "threads": threads,
        "avx": "avx" in flags,
        "avx2": "avx2" in flags,
        "avx512": "avx512f" in flags,
    }


def parse_meminfo(text):
    """Parse /proc/meminfo text. Values there are in kB."""
    values = {}
    for line in text.splitlines():
        m = re.match(r"(\w+):\s+(\d+)\s*kB", line)
        if m:
            values[m.group(1)] = int(m.group(2))
    to_gb = lambda kb: round(kb * 1024 / GIB, 1)
    return {
        "total_gb": to_gb(values.get("MemTotal", 0)),
        "available_gb": to_gb(values.get("MemAvailable", 0)),
    }


def _role(part):
    fstype = (part.get("fstype") or "").lower()
    parttype = (part.get("parttypename") or "").lower()
    if "efi system" in parttype:
        return "efi"
    if fstype == "bitlocker":
        return "windows-encrypted"
    if fstype == "ntfs":
        if "recovery" in parttype:
            return "windows-recovery"
        return "windows"
    if fstype in ("ext4", "btrfs", "xfs"):
        return "linux"
    if fstype == "swap":
        return "swap"
    if "microsoft reserved" in parttype:
        return "windows-reserved"
    return "other"


def parse_lsblk(text, live_medium=None):
    """Parse `lsblk -J -b -o NAME,SIZE,TYPE,TRAN,RM,MODEL,PTTYPE,FSTYPE,PARTTYPENAME,MOUNTPOINT`.

    live_medium: name of the disk the live system started from (never a target).
    """
    data = json.loads(text)
    disks = []
    for dev in data.get("blockdevices", []):
        if dev.get("type") != "disk":
            continue
        name = dev["name"]
        if name.startswith(("loop", "ram", "zram", "sr")):
            continue
        parts = []
        for child in dev.get("children") or []:
            if child.get("type") != "part":
                continue
            parts.append({
                "name": child["name"],
                "fs": child.get("fstype"),
                "role": _role(child),
                "size_gb": round(int(child.get("size") or 0) / GIB, 1),
            })
        removable = bool(dev.get("rm")) or dev.get("tran") == "usb"
        disks.append({
            "name": name,
            "model": (dev.get("model") or "").strip(),
            "size_gb": round(int(dev.get("size") or 0) / GIB, 1),
            "pttype": dev.get("pttype"),
            "transport": dev.get("tran"),
            "removable": removable,
            "is_live_medium": name == live_medium,
            "partitions": parts,
        })
    return disks


def summarise_windows(disks):
    roles = [p["role"] for d in disks for p in d["partitions"]]
    return {
        "present": any(r.startswith("windows") for r in roles),
        "bitlocker": "windows-encrypted" in roles,
    }


# ---------- collectors (read the real machine) ----------

def _read(path, default=""):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return default


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def collect_firmware():
    uefi = os.path.isdir("/sys/firmware/efi")
    secure = None
    if uefi:
        out = _run(["mokutil", "--sb-state"]).lower()
        if "enabled" in out:
            secure = True
        elif "disabled" in out:
            secure = False
    return {"mode": "uefi" if uefi else "bios", "secure_boot": secure}


def collect_power():
    base = "/sys/class/power_supply"
    has_battery, on_mains, percent = False, False, None
    try:
        names = os.listdir(base)
    except OSError:
        names = []
    for name in names:
        kind = _read(f"{base}/{name}/type").strip()
        if kind == "Battery":
            has_battery = True
            cap = _read(f"{base}/{name}/capacity").strip()
            if cap.isdigit():
                percent = int(cap)
        elif kind in ("Mains", "USB") and _read(f"{base}/{name}/online").strip() == "1":
            on_mains = True
    return {
        "has_battery": has_battery,
        "on_battery": has_battery and not on_mains,
        "percent": percent,
    }


def find_live_medium():
    """The disk holding the running live system, if any."""
    src = _run(["findmnt", "-n", "-o", "SOURCE", "/run/live/medium"]).strip()
    if not src:
        return None
    parent = _run(["lsblk", "-n", "-o", "PKNAME", src]).strip()
    return parent or os.path.basename(src)


def collect():
    disks = parse_lsblk(
        _run(["lsblk", "-J", "-b", "-o",
              "NAME,SIZE,TYPE,TRAN,RM,MODEL,PTTYPE,FSTYPE,PARTTYPENAME,MOUNTPOINT"]) or '{"blockdevices": []}',
        live_medium=find_live_medium(),
    )
    return {
        "arch": platform.machine(),
        "cpu": parse_cpuinfo(_read("/proc/cpuinfo")),
        "memory": parse_meminfo(_read("/proc/meminfo")),
        "firmware": collect_firmware(),
        "disks": disks,
        "windows": summarise_windows(disks),
        "power": collect_power(),
    }


# ---------- plain-English explanation ----------

def explain(profile):
    cpu, mem, fw = profile["cpu"], profile["memory"], profile["firmware"]
    lines = [
        f"Processor: {cpu['model']} ({cpu['cores']} cores).",
        f"Memory: {mem['total_gb']} GB.",
    ]
    if cpu["avx2"]:
        lines.append("This processor has the features that make the AI assistant fast (AVX2).")
    else:
        lines.append("This processor lacks the features that make the AI assistant fast (no AVX2), "
                     "so Gemma will answer slowly.")
    start = "modern start-up (UEFI)" if fw["mode"] == "uefi" else "older start-up (legacy BIOS)"
    sb = {True: "Secure Boot is on.", False: "Secure Boot is off.", None: ""}[fw["secure_boot"]]
    lines.append(f"The computer uses {start}. {sb}".strip())
    for d in profile["disks"]:
        kind = "the USB stick you started from" if d["is_live_medium"] else (
            "a removable drive" if d["removable"] else "an internal disk")
        lines.append(f"Disk {d['name']} ({d['model'] or 'no name'}): {d['size_gb']} GB, {kind}.")
    win = profile["windows"]
    if win["present"]:
        lines.append("Windows was found on this computer.")
    if win["bitlocker"]:
        lines.append("Windows disk encryption (BitLocker) is on.")
    p = profile["power"]
    if p["has_battery"]:
        lines.append(f"Battery: {p['percent']}%, {'not ' if p['on_battery'] else ''}plugged in.")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read this computer's hardware. Changes nothing.")
    ap.add_argument("--explain", action="store_true", help="print the result in plain English")
    ap.add_argument("--output", default="/run/fabulous/profile.json")
    ap.add_argument("--stdout", action="store_true", help="print JSON instead of writing the file")
    args = ap.parse_args(argv)
    profile = collect()
    if args.explain:
        print(explain(profile))
        return 0
    text = json.dumps(profile, indent=2)
    if args.stdout:
        print(text)
        return 0
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        f.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
