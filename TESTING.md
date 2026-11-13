# Testing record

| Date | What | Where | Result |
| --- | --- | --- | --- |
| 2026-11-12 | Probe and rules unit tests (17) | Claude's workspace | Pass |
| 2026-11-12 | Image build (run 43246997013), 2.5 GB | GitHub build server | Pass, 22 minutes |
| 2026-11-12 | Start to KDE desktop with Secure Boot firmware (OVMF secboot, Microsoft keys) | GitHub build server (QEMU/KVM) | Pass by screenshot. Not yet confirmed from inside the system that Secure Boot was enforcing (`mokutil --sb-state`). |
| 2026-11-12 | Start to KDE desktop under legacy BIOS | GitHub build server (QEMU/KVM) | Pass by screenshot |

Probe fixtures so far are written from the brief's expected mini-PC profile, not recorded
from the real machine. Replace them with real recordings after the first start on the Beelink.

Known gaps in the first image: still shows Debian's name (start-up menu, "Install Debian" icon, welcome window), default KDE wallpaper and left-aligned taskbar, a Firefox icon present, no Gemma, no Tor Browser or Brave.

| Date | What | Where | Result |
| --- | --- | --- | --- |
| 2026-11-12 | Branded image (run 43263602914), 2.5 GB: mandala wallpaper, centred taskbar, "Install Fabulous OS" icon, Brave on the taskbar, no Firefox, no Debian welcome window | GitHub build server, UEFI Secure Boot firmware and legacy BIOS | Pass by screenshot; no build warnings |

Still untested after the branding pass: running the installer; opening Brave, Tor Browser or the app store; anything on real hardware. The start-up menu on the stick still says "Debian GNU/Linux". No Gemma yet.

## 13 November 2026

Test machines are virtual PCs on GitHub's build servers (QEMU/KVM, 4 GB memory). "Self-check" means the
`fabulous-selftest` program inside the image reporting facts over the test machine's serial port;
the reports are saved beside the screenshots on the `test-results` branch.

| What | Image | How | Result |
| --- | --- | --- | --- |
| Probe and rules unit tests (19) | — | Claude's workspace and build server | Pass |
| Build 5 (run 43408506398), 2.5 GB: firewall, ClamAV, self-check added | build 5 | Build server | Pass, 20 minutes, no build warnings |
| Secure Boot really enforcing in the stick session | builds 5, 6 | Self-check (`mokutil --sb-state`: "SecureBoot enabled") | Pass. Closes the gap noted on 12 November. |
| Firewall on in the stick session: active, incoming refused, outgoing allowed | builds 5, 6 | Self-check (`ufw status verbose`), Secure Boot and legacy BIOS machines | Pass |
| Installer run by hand through to "All done", then restart from the disk | build 4 | Remote-controlled test machine, Secure Boot firmware, blank 119 GB disk | Pass. Install took under 5 minutes. |
| Brave opens | build 5 | Remote-controlled test machine, screenshot | Opens to its welcome page, but a "KDE Wallet" question pops up first. Not fixed. Privacy settings still unchecked. |
| Virus Scanner window (ClamTk) opens | build 5 | Same | Pass (window seen; no scan run through the window) |
| Firewall page in System Settings | build 5 | Same | Pass: shows "Enabled", incoming "Ignore", outgoing "Allow" |
| Build 6 (run 43412304396), 2.5 GB | build 6 | Build server | Pass, with one warning: installer still starts in New York (see below) |
| **Automated install test** (`tests/install-test.sh`): open installer from the desktop icon, choose "Erase disk" on a blank 119 GB disk, create a user, confirm, install, restart from the disk alone, log in | build 6 | Build server, Secure Boot firmware, 13 screenshots | **Pass**, 0 problems |
| Installed system calls itself Fabulous OS | build 6 | Self-check on the installed system | Pass ("Fabulous OS 0.1") |
| Installed system: Secure Boot enforcing | build 6 | Self-check | Pass. Confirms the decision to keep the start-up folder named "debian". |
| Installed system: firewall active, incoming refused | build 6 | Self-check | Pass |
| Installed system: no network services listening | build 6 | Self-check (`ss -tuln`: empty) | Pass. Build 5 had a background Tor service on 127.0.0.1:9050; switched off in build 6. |
| Installed system: no services failed to start | build 6 | Self-check | Pass |
| Virus scanner detects the standard EICAR test file and passes a clean file | build 6 | Self-check on the installed system, after downloading signatures | Pass ("Eicar-Test-Signature FOUND", 1 of 2 files) |
| Installer asks "Continue with Installation?" before erasing | build 6 | Screenshot `install-10` | Pass. Build 4 erased at once on pressing Install. |

### Found and not fixed

- **The installer starts in New York** (place, clock, American date style). The build-6 fix did not take: the settings file was not where expected (build warning). Until fixed, choose London on the installer's Location screen.
- **No typed confirmation before erasing.** There is now a click-through question, which is weaker than non-negotiable 3 requires. The typed confirmation belongs to the plain-question screens (step 4).
- Debian's wording and pictures remain in the installer ("Welcome to the Calamares installer", "Welcome to Debian GNU/Linux", the main partition labelled "Debian") and on the log-in screen.
- Brave shows a "KDE Wallet" question at first start.
- ClamAV's automatic signature updater reported "inactive" on the installed system. Signatures download when asked for (the self-check did it by hand); whether they update by themselves is unconfirmed.
- In the stick session the app store (Discover) checked for updates by itself. That is network use nobody asked for.
- Once, in a remote-controlled test machine, the first double-click on the install icon after start-up did nothing; a later double-click worked, and the automated test's double-click worked. Cause unknown.

### Still untested

- Anything on real hardware (the Beelink): start from the stick, screen, Wi-Fi, sound, Bluetooth.
- Installing over a disk that already holds Windows (the test disk was blank), including a BitLocker-encrypted one.
- Installing on a legacy-BIOS machine (only the stick session was started there).
- Opening Tor Browser and the app store; installing or removing an app.
- A scan started from the Virus Scanner window.
- Brave's privacy setting names against Brave's documentation.
- No Gemma, LibreOffice or creative apps yet.

## 13 November 2026, afternoon: option B (install on an external drive)

The test machine now has Secure Boot enforcing, an internal 477 GB disk laid out like a Windows PC's
(EFI, Microsoft reserved, NTFS "Windows" with a marker file, NTFS recovery), and a blank 500 GB external USB drive.
"Unchanged" means `qemu-img compare` against a copy of the internal disk taken beforehand reports "Images are identical".

| What | Image | How | Result |
| --- | --- | --- | --- |
| Probe and rules unit tests (19), rules now offer only external drives | — | Workspace and build server | Pass |
| Installer's first choice of disk, as Debian ships it | build 6 | By hand, remote-controlled test machine | **Dangerous: the internal Windows disk was preselected**, with "Erase disk" one click away. |
| With the internal disk made read-only, installer offers only the external drive | build 6 by hand; builds 7, 8 built in | Screenshot; stick self-check shows `sda` read-only | Pass |
| Install onto the external drive; internal disk unchanged afterwards | builds 6, 7 by hand; 7, 8 automated | `qemu-img compare` | Pass every time (5 installs) |
| External drive starts by itself after the firmware's memory is wiped | build 6, 7 | By hand and automated | **Fail.** Build 6: no start-up file in the removable-drive location. Build 7: file present but it was GRUB, not the signed shim; Secure Boot refused it ("Access Denied"). |
| Build 7 (run 43435924365) | build 7 | Build server | Built; install test failed as above. Also lost the installer's "Fabulous OS" wording through an editing mistake by Claude. |
| Build 8 (run 43444437036), 2.5 GB | build 8 | Build server | Pass, no build warnings |
| **Automated install test, option B**: install to external drive, wipe firmware memory, start from the external drive under Secure Boot, log in | build 8 | Build server, 14 screenshots | **Pass**, 0 problems |
| Installed system (on the external drive): calls itself Fabulous OS; Secure Boot enforcing; firewall active, incoming refused; nothing listening; set to London | build 8 | Self-check | Pass |
| Internal disk unchanged after the installed system had run | build 8 | `qemu-img compare` | Pass |
| Virus signatures fetched by the on-request service; scanner then detects the EICAR test file | build 8 | Self-check on the installed system (service started as administrator) | Pass |
| Installer starts in London | build 6 by hand; build 8 | Screenshot; self-check of installed system | Pass |
| Installer pictures: mandala logo, "Fabulous OS, based on Debian" | build 8 | Screenshot `install-03` | Pass. The heading still says "Welcome to the Calamares installer for Fabulous OS 13". |
| Log-in screen shows the mandala | build 8 | Screenshot `install-12` | Partly: mandala background, but a "debian" logo remains at the bottom. |
| Brave on the installed system opens with no "KDE Wallet" question | build 8 | Screenshot `install-14` | Pass |

### Not tested (new items)

- Whether anything is written to the PC's firmware memory during install. The installer is told not to (`--no-nvram`); the test shows the drive does not *need* such an entry, not that none was written.
- Opening the Virus Scanner from the menu as an ordinary user (the no-password permission to fetch signatures).
- The daily "updates available" pop-up, and its setting names.
- "App Store" label; Brave in the stick session (Wallet switched off there).
- A real external SSD, a real PC, a real Windows disk with BitLocker. The pretend Windows disk cannot start, so "unplug and Windows starts as before" is argued from the disk being unchanged, not observed.
- Gemma from an external drive.
