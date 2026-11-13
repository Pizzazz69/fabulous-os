# Shared by the test scripts: start a test machine shaped like the target mini-PC's
# essentials (UEFI with Secure Boot enforcing, one blank 119 GB internal disk).
# Usage: vm_prepare; vm_start stick|disk [selftest-mode]; vm ...commands...; vm_stop
VMDIR=${VMDIR:-/mnt/fabulous-vm}
VMLIB_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOCK=$VMDIR/qmp.sock

vm_prepare() {
    sudo apt-get update -qq
    sudo apt-get install -y -qq --no-install-recommends qemu-system-x86 qemu-utils ovmf >/dev/null
    sudo mkdir -p "$VMDIR" && sudo chmod 777 "$VMDIR"
    cp /usr/share/OVMF/OVMF_VARS_4M.ms.fd "$VMDIR/vars.fd"
    qemu-img create -q -f qcow2 "$VMDIR/disk.qcow2" 119G
}

vm_start() {  # $1 = stick (image attached, started from it) or disk (internal disk only)
    local from=$1 mode=${2:-basic} cd=""
    if [ "$from" = stick ]; then
        cd="-drive if=none,id=cd0,media=cdrom,readonly=on,file=$ISO -device ide-cd,drive=cd0,bus=ide.1,bootindex=0"
    fi
    sudo rm -f "$SOCK"
    sudo qemu-system-x86_64 -enable-kvm -cpu host -m 4096 -smp 3 -display none -vga std \
        -machine q35,smm=on -global driver=cfi.pflash01,property=secure,value=on \
        -drive if=pflash,format=raw,unit=0,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.secboot.fd \
        -drive if=pflash,format=raw,unit=1,file="$VMDIR/vars.fd" \
        -drive if=none,id=d0,format=qcow2,file="$VMDIR/disk.qcow2" -device ide-hd,drive=d0,bus=ide.0,bootindex=1 \
        $cd \
        -device qemu-xhci -device usb-tablet \
        -smbios type=11,value=io.systemd.credential:fabulous.selftest=$mode \
        -serial file:"$VMDIR/serial-$from.log" \
        -qmp unix:"$SOCK",server,nowait -daemonize
    sleep 2
}

vm() { sudo python3 "$VMLIB_DIR/vmctl.py" "$SOCK" "$@"; }

vm_stop() { vm quit || true; sleep 3; }
