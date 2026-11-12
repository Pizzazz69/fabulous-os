# Testing record

| Date | What | Where | Result |
| --- | --- | --- | --- |
| 2026-11-12 | Probe and rules unit tests (17) | Claude's workspace | Pass |
| 2026-11-12 | Image build (run 43246997013), 2.5 GB | GitHub build server | Pass, 22 minutes |
| 2026-11-12 | Start to KDE desktop with Secure Boot firmware (OVMF secboot, Microsoft keys) | GitHub build server (QEMU/KVM) | Pass by screenshot. Not yet confirmed from inside the system that Secure Boot was enforcing (`mokutil --sb-state`). |
| 2026-11-12 | Start to KDE desktop under legacy BIOS | GitHub build server (QEMU/KVM) | Pass by screenshot |
| — | "Try it first" on the Beelink: desktop, Wi-Fi, sound | David | Not yet run |

Probe fixtures so far are written from the brief's expected mini-PC profile, not recorded
from the real machine. Replace them with real recordings after the first start on the Beelink.

Known gaps in the first image: still shows Debian's name (start-up menu, "Install Debian" icon, welcome window), default KDE wallpaper and left-aligned taskbar, a Firefox icon present, no Gemma, no Tor Browser or Brave.

| Date | What | Where | Result |
| --- | --- | --- | --- |
| 2026-11-12 | Branded image (run 43263602914), 2.5 GB: mandala wallpaper, centred taskbar, "Install Fabulous OS" icon, Brave on the taskbar, no Firefox, no Debian welcome window | GitHub build server, UEFI Secure Boot firmware and legacy BIOS | Pass by screenshot; no build warnings |

Still untested after the branding pass: running the installer; opening Brave, Tor Browser or the app store; anything on real hardware. The start-up menu on the stick still says "Debian GNU/Linux". No Gemma yet.
