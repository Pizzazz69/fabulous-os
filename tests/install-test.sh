#!/bin/bash
# Automated install test (option B: install on an external drive).
# The test machine has Secure Boot enforcing, an internal 477 GB disk laid out like
# Windows, and a blank 500 GB external USB drive. The test clicks through the
# installer, then wipes the firmware's memory and restarts from the external drive,
# logs in, reads the system's self-check, asks Gemma a question, and finally compares the internal disk
# with a copy taken beforehand: it must be byte-for-byte unchanged.
# Usage: ISO=/path/to/image.iso OUT=dir tests/install-test.sh
set -u
: "${ISO:?}"; OUT=${OUT:-shots}; mkdir -p "$OUT"
. "$(dirname "$0")/vm-lib.sh"
PASSWORD='Qz7-mandala-Plum4'   # throwaway, exists only inside the test machine
shot() { vm shot "$VMDIR/s.png" && sudo cat "$VMDIR/s.png" > "$OUT/install-$1.png"; }
region_changed() {  # did the middle of the screen change between two screenshots?
    local n
    n=$(compare -metric AE -fuzz 8% -extract 700x300+300+200 "$1" "$2" null: 2>&1 | cut -d' ' -f1 | cut -d. -f1)
    [ "${n:-0}" -gt 20000 ]
}
problems=0
problem() { echo "PROBLEM: $*" | tee -a "$OUT/install-result.txt"; problems=$((problems+1)); }
: > "$OUT/install-result.txt"

vm_prepare
vm_start stick basic
sleep 170
shot 01-stick-desktop

# Open the installer the way a person would: double-click the desktop icon.
# (The very first click after start-up only wakes the desktop, so click an empty spot first.)
vm click 900 250; sleep 2
vm dclick 58 45; sleep 25
shot 02-after-double-click
if region_changed "$OUT/install-01-stick-desktop.png" "$OUT/install-02-after-double-click.png"; then
    echo "Installer opened from the desktop icon." | tee -a "$OUT/install-result.txt"
else
    problem "Double-clicking the desktop icon did not open the installer; opened it from the start menu instead."
    vm key meta_l -- sleep 3 -- type install -- sleep 3 -- key ret; sleep 30
fi
shot 03-welcome
vm key alt-n; sleep 6; shot 04-location
vm key alt-n; sleep 6; shot 05-keyboard
vm key alt-n; sleep 12; shot 06-partitions
vm click 335 185; sleep 5; shot 07-erase-disk-chosen
sudo cat "$VMDIR/serial-stick.log" | tr -d '\000\r' | sed -n '/SELFTEST BEGIN/,$p' > "$OUT/install-stick-selfcheck.txt"
vm key alt-n; sleep 6
vm click 428 165 -- type Test User -- click 428 347 -- type "$PASSWORD" -- click 634 347 -- type "$PASSWORD"; sleep 2
shot 08-users
vm key alt-n; sleep 6; shot 09-summary
vm key alt-i; sleep 4; shot 10-after-install-pressed
vm key alt-i; sleep 4
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 60; vm move $((600+i)) 300; done   # keep the screen awake (the 3.35 GB Gemma file is copied too)
shot 11-install-finished
vm_stop

if vm_internal_unchanged; then
    echo "Internal (Windows) disk is byte-for-byte unchanged after the install." | tee -a "$OUT/install-result.txt"
else
    problem "THE INTERNAL DISK WAS CHANGED BY THE INSTALL."
fi
# The installed system runs on a machine shaped like the Beelink: a processor without
# AVX or AVX2 ("Westmere") and 16 GB of memory, so that Gemma is tried the way it
# will have to run there.
vm_start external full Westmere 16384
sleep 100; shot 12-login-screen
vm key shift -- sleep 3 -- type "$PASSWORD" -- key ret
sleep 60; shot 13-installed-desktop
vm click 900 250 -- click 632 768; sleep 30; shot 14-brave-on-installed-system
log="$VMDIR/serial-external.log"
# Gemma: first wait for the self-check's question (asked without a window), then
# open the window from the start menu the way a person would and ask one there.
for i in $(seq 1 240); do sudo grep -aq "SELFTEST GEMMA DONE" "$log" && break; sleep 10; vm move $((600+i%5)) 300; done
vm key meta_l -- sleep 4 -- type gemma -- sleep 4 -- key ret
sleep 60; shot 15-gemma-window
vm type "name three fruits" -- key ret
for i in 1 2 3 4 5 6 7 8 9; do sleep 10; vm move $((600+i)) 300; done
shot 16-gemma-answer
for i in $(seq 1 90); do sudo grep -aq "SELFTEST FULL DONE" "$log" && break; sleep 10; done
vm_stop
vm_internal_unchanged >/dev/null || problem "THE INTERNAL DISK WAS CHANGED BY RUNNING THE INSTALLED SYSTEM."
sudo cat "$log" | tr -d '\000\r' | sed -n '/SELFTEST BEGIN/,$p' > "$OUT/install-selfcheck.txt"
echo "=== self-check of the installed system ==="; cat "$OUT/install-selfcheck.txt"

need() { grep -aq -- "$1" "$OUT/install-selfcheck.txt" || problem "$2"; }
need "started from: installed-disk" "The installed system did not start from the disk (or its self-check did not run)."
need "^system: Fabulous OS" "The installed system does not call itself Fabulous OS."
need "SecureBoot enabled" "Secure Boot is not enforcing in the installed system."
need "^Status: active" "The firewall is not active in the installed system."
need "deny (incoming)" "The firewall does not refuse incoming connections."
need "FOUND" "The virus scanner did not detect the standard test file."
need "timezone: Europe/London" "The installed system is not set to London."
need "tokens per second" "Gemma did not answer on the installed system."
need "gemma exit code: 0" "Gemma's program reported an error on the installed system."
grep -a "^picture answer:" "$OUT/install-selfcheck.txt" | grep -aqi "fabulous" || problem "Gemma did not read the words in the test picture on the installed system."
grep -a "^recording answer:" "$OUT/install-selfcheck.txt" | grep -aqi "london" || problem "Gemma did not hear the test recording on the installed system."
need "AVX2 no, AVX no" "The installed system's test processor had AVX, so the no-AVX test proves nothing."
grep -aqF "network devices visible to the assistant: ['lo']" "$OUT/install-selfcheck.txt" || problem "The assistant was not cut off from the network."
need "^sdb .* usb .*disk" "The installed system does not see itself on a USB drive."
grep -aqE "^sda +1 " "$OUT/install-stick-selfcheck.txt" || problem "The internal disk was not read-only in the stick session."
echo "problems: $problems" | tee -a "$OUT/install-result.txt"
[ "$problems" -eq 0 ]
