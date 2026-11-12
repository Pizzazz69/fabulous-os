import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(HERE))
import fabulous_probe as fp  # noqa: E402


def fixture(name):
    with open(os.path.join(HERE, "fixtures", name)) as f:
        return f.read()


def test_n5105_has_no_avx():
    cpu = fp.parse_cpuinfo(fixture("n5105_cpuinfo.txt"))
    assert cpu["model"] == "Intel(R) Celeron(R) N5105 @ 2.00GHz"
    assert cpu["cores"] == 4 and cpu["threads"] == 4
    assert cpu["avx"] is False and cpu["avx2"] is False and cpu["avx512"] is False


def test_avx2_detected():
    text = "processor : 0\nmodel name : Test CPU\ncore id : 0\nflags : fpu sse avx avx2\n"
    cpu = fp.parse_cpuinfo(text)
    assert cpu["avx"] and cpu["avx2"] and not cpu["avx512"]


def test_meminfo_16gb():
    mem = fp.parse_meminfo("MemTotal:       16150000 kB\nMemAvailable:   14800000 kB\n")
    assert mem["total_gb"] == 15.4
    assert mem["available_gb"] == 14.1


def test_minipc_disks():
    disks = fp.parse_lsblk(fixture("minipc_lsblk.json"), live_medium="sda")
    assert [d["name"] for d in disks] == ["sda", "nvme0n1"]  # loop device ignored
    stick, internal = disks
    assert stick["removable"] and stick["is_live_medium"]
    assert not internal["removable"] and not internal["is_live_medium"]
    roles = [p["role"] for p in internal["partitions"]]
    assert roles == ["efi", "windows-reserved", "windows-encrypted", "windows-recovery"]


def test_bitlocker_summary():
    disks = fp.parse_lsblk(fixture("minipc_lsblk.json"), live_medium="sda")
    assert fp.summarise_windows(disks) == {"present": True, "bitlocker": True}


def test_explain_is_plain_and_mentions_slow():
    profile = {
        "arch": "x86_64",
        "cpu": fp.parse_cpuinfo(fixture("n5105_cpuinfo.txt")),
        "memory": {"total_gb": 15.4, "available_gb": 14.1},
        "firmware": {"mode": "uefi", "secure_boot": True},
        "disks": fp.parse_lsblk(fixture("minipc_lsblk.json"), live_medium="sda"),
        "windows": {"present": True, "bitlocker": True},
        "power": {"has_battery": False, "on_battery": False, "percent": None},
    }
    text = fp.explain(profile)
    assert "Celeron(R) N5105" in text
    assert "answer slowly" in text
    assert "the USB stick you started from" in text
    assert "BitLocker" in text


def test_collect_runs_on_this_machine_without_error():
    profile = fp.collect()
    assert profile["memory"]["total_gb"] > 0
    assert profile["cpu"]["threads"] >= 1
