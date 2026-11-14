# Shared by the test scripts. The test machine is shaped like David's plan (option B):
#   - UEFI firmware with Secure Boot enforcing
#   - an internal 477 GB disk laid out like a Windows PC's (must never be changed)
#   - a 500 GB external USB drive (where Fabulous OS is installed)
#   - 4 processor cores and 8 GB of memory unless told otherwise (Gemma needs about 3.5 GB)
# Usage: vm_prepare; vm_start stick|external [selftest-mode] [processor] [memory MB]; vm ...; vm_stop; vm_internal_unchanged
VMDIR=${VMDIR:-/mnt/fabulous-vm}
VMLIB_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOCK=$VMDIR/qmp.sock

vm_prepare() {
    sudo apt-get update -qq
    sudo apt-get install -y -qq --no-install-recommends qemu-system-x86 qemu-utils ovmf gdisk dosfstools ntfs-3g imagemagick >/dev/null
    sudo mkdir -p "$VMDIR" && sudo chmod 777 "$VMDIR"
    # Pretend Windows disk: EFI, Microsoft reserved, Windows (NTFS), recovery (NTFS).
    local raw="$VMDIR/internal.raw" loop
    truncate -s 477G "$raw"
    sgdisk -n1:0:+100M -t1:ef00 -c1:"EFI system partition" \
           -n2:0:+16M  -t2:0c01 -c2:"Microsoft reserved partition" \
           -n3:0:-1G   -t3:0700 -c3:"Basic data partition" \
           -n4:0:0     -t4:2700 "$raw" >/dev/null
    loop=$(sudo losetup -fP --show "$raw")
    sudo mkfs.vfat -n SYSTEM "${loop}p1" >/dev/null
    sudo mkfs.ntfs -Q -f -L Windows "${loop}p3" >/dev/null
    sudo mkfs.ntfs -Q -f -L Recovery "${loop}p4" >/dev/null
    sudo mkdir -p /mnt/fabulous-tmp
    if sudo mount "${loop}p1" /mnt/fabulous-tmp; then
        sudo mkdir -p /mnt/fabulous-tmp/EFI/Microsoft/Boot
        echo "pretend Windows start-up file" | sudo tee /mnt/fabulous-tmp/EFI/Microsoft/Boot/bootmgfw.efi >/dev/null
        sudo umount /mnt/fabulous-tmp
    fi
    if sudo mount -t ntfs-3g "${loop}p3" /mnt/fabulous-tmp; then
        sudo mkdir -p /mnt/fabulous-tmp/Users/David/Documents /mnt/fabulous-tmp/Windows/System32
        echo "This file must survive." | sudo tee /mnt/fabulous-tmp/Users/David/Documents/keep-me.txt >/dev/null
        sudo umount /mnt/fabulous-tmp
    fi
    sudo losetup -d "$loop"
    qemu-img convert -f raw -O qcow2 "$raw" "$VMDIR/internal.qcow2" && rm -f "$raw"
    cp "$VMDIR/internal.qcow2" "$VMDIR/internal-pristine.qcow2"
    qemu-img create -q -f qcow2 "$VMDIR/external.qcow2" 500G
    cp /usr/share/OVMF/OVMF_VARS_4M.ms.fd "$VMDIR/vars.fd"
}

vm_start() {  # $1 = stick (started from the image) or external (started from the USB drive, firmware memory wiped)
    local from=$1 mode=${2:-basic} cd="" extboot=3 cpu=${3:-host} mem=${4:-8192}
    if [ "$from" = stick ]; then
        cd="-drive if=none,id=cd0,media=cdrom,readonly=on,file=$ISO -device ide-cd,drive=cd0,bus=ide.1,bootindex=0"
    else
        # Fresh firmware memory: proves the drive starts on its own, as it must after
        # being unplugged, or on a PC that has never seen it.
        cp /usr/share/OVMF/OVMF_VARS_4M.ms.fd "$VMDIR/vars.fd"
        extboot=0
    fi
    sudo rm -f "$SOCK"
    sudo qemu-system-x86_64 -enable-kvm -cpu "$cpu" -m "$mem" -smp 4 -display none -vga std \
        -machine q35,smm=on -global driver=cfi.pflash01,property=secure,value=on \
        -drive if=pflash,format=raw,unit=0,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.secboot.fd \
        -drive if=pflash,format=raw,unit=1,file="$VMDIR/vars.fd" \
        -drive if=none,id=d0,format=qcow2,file="$VMDIR/internal.qcow2" -device ide-hd,drive=d0,bus=ide.0,bootindex=5 \
        $cd \
        -device qemu-xhci,id=xhci -device usb-tablet,bus=xhci.0 \
        -drive if=none,id=u0,format=qcow2,file="$VMDIR/external.qcow2" \
        -device usb-storage,drive=u0,bus=xhci.0,bootindex=$extboot \
        -smbios type=11,value=io.systemd.credential:fabulous.selftest=$mode \
        -serial file:"$VMDIR/serial-$from.log" \
        -qmp unix:"$SOCK",server,nowait -daemonize
    sleep 2
}

vm() { sudo python3 "$VMLIB_DIR/vmctl.py" "$SOCK" "$@"; }

vm_stop() { vm quit || true; sleep 3; }

# With the test machine stopped: is the internal "Windows" disk byte-for-byte as it was?
vm_internal_unchanged() { qemu-img compare "$VMDIR/internal-pristine.qcow2" "$VMDIR/internal.qcow2"; }
