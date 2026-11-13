import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(HERE))
import fabulous_probe as fp  # noqa: E402


def fixture(name):
    with open(os.path.join(HERE, "fixtures", name)) as f:
        return f.read()


def test_j4125_has_no_avx():
    cpu = fp.parse_cpuinfo(fixture("j4125_cpuinfo.txt"))
    assert cpu["model"] == "Intel(R) Celeron(R) J4125 CPU @ 2.00GHz"
    assert cpu["cores"] == 4 and cpu["threads"] == 4
    assert cpu["avx"] is False and cpu["avx2"] is False and cpu["avx512"] is False


def test_avx2_detected():
    text = "processor : 0\nmodel name : Test CPU\ncore id : 0\nflags : fpu sse avx avx2\n"
    cpu = fp.parse_cpuinfo(text)
    assert cpu["avx"] and cpu["avx2"] and not cpu["avx512"]


def test_meminfo_8gb():
    mem = fp.parse_meminfo("MemTotal:        8010000 kB\nMemAvailable:    6900000 kB\n")
    assert mem["total_gb"] == 7.6
    assert mem["available_gb"] == 6.6


def test_awow_sata_disks():
    disks = fp.parse_lsblk(fixture("awow_sata_lsblk.json"), live_medium="sdb")
    assert [d["name"] for d in disks] == ["sda", "sdb"]  # loop device ignored
    internal, stick = disks
    assert stick["removable"] and stick["is_live_medium"]
    assert not internal["removable"] and not internal["is_live_medium"]
    assert internal["size_gb"] == 119.2  # what Windows shows as "119 GB"
    roles = [p["role"] for p in internal["partitions"]]
    assert roles == ["efi", "windows-reserved", "windows-encrypted", "windows-recovery"]


def test_awow_emmc_disks():
    disks = fp.parse_lsblk(fixture("awow_emmc_lsblk.json"), live_medium="sda",
                           mmc_types={"mmcblk0": "MMC", "mmcblk1": "SD"})
    by = {d["name"]: d for d in disks}
    # the eMMC's boot areas are not offered as disks
    assert sorted(by) == ["mmcblk0", "mmcblk1", "sda"]
    assert not by["mmcblk0"]["removable"]
    assert by["mmcblk1"]["removable"]  # SD card in the card slot: never a target
    assert by["sda"]["is_live_medium"]


def test_sd_card_without_type_information_is_not_assumed_removable():
    disks = fp.parse_lsblk(fixture("awow_emmc_lsblk.json"), live_medium="sda")
    by = {d["name"]: d for d in disks}
    assert not by["mmcblk1"]["removable"]  # documents the limit: the type must be supplied


def test_bitlocker_summary():
    disks = fp.parse_lsblk(fixture("awow_sata_lsblk.json"), live_medium="sdb")
    assert fp.summarise_windows(disks) == {"present": True, "bitlocker": True}


def test_explain_is_plain_and_mentions_slow():
    profile = {
        "arch": "x86_64",
        "cpu": fp.parse_cpuinfo(fixture("j4125_cpuinfo.txt")),
        "memory": {"total_gb": 7.6, "available_gb": 6.6},
        "firmware": {"mode": "uefi", "secure_boot": True},
        "disks": fp.parse_lsblk(fixture("awow_sata_lsblk.json"), live_medium="sdb"),
        "windows": {"present": True, "bitlocker": True},
        "power": {"has_battery": False, "on_battery": False, "percent": None},
    }
    text = fp.explain(profile)
    assert "Celeron(R) J4125" in text
    assert "answer slowly" in text
    assert "the USB stick you started from" in text
    assert "BitLocker" in text


def test_collect_runs_on_this_machine_without_error():
    profile = fp.collect()
    assert profile["memory"]["total_gb"] > 0
    assert profile["cpu"]["threads"] >= 1
