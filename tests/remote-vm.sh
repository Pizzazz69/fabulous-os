#!/bin/bash
# Development aid: keeps a test machine running on the build server and obeys
# commands pushed to the "vm-control" branch (file cmd.txt, one vmctl command per
# line, plus: snap, restart-from-disk). Screens are pushed to the "vm-screen" branch.
# Used to work out the installer's click-path; the real test is tests/install-test.sh.
set -u
ISO=$1; MINUTES=${2:-45}
. "$(dirname "$0")/vm-lib.sh"
vm_prepare
vm_start stick full
out=$(mktemp -d); cd "$out"; git init -q -b vm-screen
git config user.name "fabulous-os build"; git config user.email "noreply@github.com"
remote="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}"
last=""; n=0; end=$(( $(date +%s) + MINUTES*60 ))
publish() {
    vm shot "$VMDIR/s.png" >> log.txt 2>&1 && sudo cat "$VMDIR/s.png" > shot.png
    sudo sh -c "cat $VMDIR/serial-*.log" | tr -d '\000' | grep -av "Loading:" | tail -c 20000 > serial.txt
    echo "$1" > done.txt
    git add -A; git commit -q -m "screen $1" --allow-empty; git push -q -f "$remote" vm-screen
}
sleep 20; publish started
while [ "$(date +%s)" -lt "$end" ]; do
    sha=$(git ls-remote "$remote" refs/heads/vm-control | cut -f1)
    if [ -n "$sha" ] && [ "$sha" != "$last" ]; then
        last=$sha
        git fetch -q "$remote" vm-control
        rm -f snap-*.png
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            echo "cmd: $line"
            case "$line" in
                snap) n=$((n+1)); vm shot "$VMDIR/s.png"; sudo cat "$VMDIR/s.png" > "snap-$n.png" ;;
                restart-from-disk) vm_stop; vm_internal_unchanged >> log.txt 2>&1; vm_start external full ;;
                stop) publish "$sha"; vm_stop; exit 0 ;;
                *) vm $line >> log.txt 2>&1 ;;
            esac
        done < <(git show FETCH_HEAD:cmd.txt)
        publish "$sha"
    fi
    sleep 4
done
vm_stop
