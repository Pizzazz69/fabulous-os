#!/bin/bash
# Automated install test. Starts the image in a test machine with Secure Boot
# enforcing and a blank 119 GB disk, clicks through the installer ("erase disk"),
# then restarts from the disk alone, logs in, and reads the system's self-check.
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
vm key alt-n; sleep 10; shot 06-partitions
vm click 335 185; sleep 5; shot 07-erase-disk-chosen
vm key alt-n; sleep 6
vm click 428 165 -- type Test User -- click 428 347 -- type "$PASSWORD" -- click 634 347 -- type "$PASSWORD"; sleep 2
shot 08-users
vm key alt-n; sleep 6; shot 09-summary
vm key alt-i; sleep 4; shot 10-after-install-pressed
vm key alt-i; sleep 4
for i in 1 2 3 4 5 6 7 8; do sleep 60; vm move $((600+i)) 300; done   # keep the screen awake
shot 11-install-finished
vm_stop

vm_start disk full
sleep 90; shot 12-login-screen
vm key shift -- sleep 3 -- type "$PASSWORD" -- key ret
sleep 60; shot 13-installed-desktop
log="$VMDIR/serial-disk.log"
for i in $(seq 1 90); do sudo grep -aq "SELFTEST FULL DONE" "$log" && break; sleep 10; done
vm_stop
sudo cat "$log" | tr -d '\000\r' | sed -n '/SELFTEST BEGIN/,$p' > "$OUT/install-selfcheck.txt"
echo "=== self-check of the installed system ==="; cat "$OUT/install-selfcheck.txt"

need() { grep -aq -- "$1" "$OUT/install-selfcheck.txt" || problem "$2"; }
need "started from: installed-disk" "The installed system did not start from the disk (or its self-check did not run)."
need "^system: Fabulous OS" "The installed system does not call itself Fabulous OS."
need "SecureBoot enabled" "Secure Boot is not enforcing in the installed system."
need "^Status: active" "The firewall is not active in the installed system."
need "deny (incoming)" "The firewall does not refuse incoming connections."
need "FOUND" "The virus scanner did not detect the standard test file."
echo "problems: $problems" | tee -a "$OUT/install-result.txt"
[ "$problems" -eq 0 ]
