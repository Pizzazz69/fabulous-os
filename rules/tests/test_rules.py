import copy
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(HERE))
import fabulous_rules as fr  # noqa: E402

RULES = fr.load_rules()

# The AWOW mini-PC as David described it on 13 November 2026 (expected profile, not a recording).
MINIPC = {
    "arch": "x86_64",
    "cpu": {"model": "Intel(R) Celeron(R) J4125 CPU @ 2.00GHz", "cores": 4, "threads": 4,
            "avx": False, "avx2": False, "avx512": False},
    "memory": {"total_gb": 7.6, "available_gb": 6.6},
    "firmware": {"mode": "uefi", "secure_boot": True},
    "disks": [
        {"name": "sdb", "model": "Card Reader", "size_gb": 119.1, "removable": True,
         "is_live_medium": True, "partitions": []},
        {"name": "sda", "model": "128GB SSD", "size_gb": 119.2, "removable": False,
         "is_live_medium": False, "partitions": []},
    ],
    "windows": {"present": True, "bitlocker": True},
    "power": {"has_battery": False, "on_battery": False, "percent": None},
}


def variant(**changes):
    p = copy.deepcopy(MINIPC)
    for path, value in changes.items():
        a, b = path.split("__")
        p[a][b] = value
    return p


def test_awow_gets_no_gemma_under_the_current_rules():
    """8 GB and no AVX2: the rules as written give no assistant. To be revisited
    with real measurements in the Gemma step (DECISIONS.md, 13 November 2026)."""
    d = fr.decide(MINIPC, RULES)
    assert d["model"] == "none" and d["model_label"] is None
    assert d["app_set"] == "office"  # below 8 GB usable
    assert d["target_disk"] == "sda"
    assert d["refusals"] == []  # 119 GB disk is above the 64 GB minimum
    assert d["will_erase_windows"] is True
    assert "8 GB" in d["welcome_text"] and "Gemma" not in d["welcome_text"]


def test_16gb_without_avx2_gets_e2b_with_slow_note():
    d = fr.decide(variant(memory__total_gb=15.4), RULES)
    assert d["model"] == "e2b"
    assert any("answer slowly" in n for n in d["model_notes"])
    assert d["app_set"] == "full"
    assert "16 GB" in d["welcome_text"] and "Gemma 4 E2B" in d["welcome_text"]


def test_16gb_with_avx2_gets_e4b():
    d = fr.decide(variant(cpu__avx2=True, memory__total_gb=15.4), RULES)
    assert d["model"] == "e4b" and d["model_notes"] == []


def test_8gb_with_avx2_gets_e2b():
    d = fr.decide(variant(cpu__avx2=True), RULES)
    assert d["model"] == "e2b"
    assert d["app_set"] == "office"  # below 8 GB


def test_4gb_gets_no_model_and_office():
    d = fr.decide(variant(cpu__avx2=True, memory__total_gb=3.8), RULES)
    assert d["model"] == "none" and d["app_set"] == "office"


def test_usb_stick_is_never_a_target():
    p = copy.deepcopy(MINIPC)
    p["disks"] = [p["disks"][0]]
    d = fr.decide(p, RULES)
    assert d["target_disk"] is None and d["target_disk_choices"] == []
    assert any("No internal disk" in r for r in d["refusals"])


def test_small_disk_refused():
    p = copy.deepcopy(MINIPC)
    p["disks"][1]["size_gb"] = 29.8
    assert any("too small" in r for r in fr.decide(p, RULES)["refusals"])


def test_wrong_arch_refused():
    p = copy.deepcopy(MINIPC)
    p["arch"] = "aarch64"
    assert any("for PCs" in r for r in fr.decide(p, RULES)["refusals"])


def test_low_battery_refused():
    p = copy.deepcopy(MINIPC)
    p["power"] = {"has_battery": True, "on_battery": True, "percent": 20}
    assert any("battery" in r for r in fr.decide(p, RULES)["refusals"])


def test_largest_internal_disk_preferred():
    p = copy.deepcopy(MINIPC)
    p["disks"].append({"name": "sdc", "model": "Big", "size_gb": 931.5, "removable": False,
                       "is_live_medium": False, "partitions": []})
    d = fr.decide(p, RULES)
    assert d["target_disk"] == "sdc"
    assert d["target_disk_choices"] == ["sda", "sdc"]
