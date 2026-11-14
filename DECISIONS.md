# Decisions

Each entry: what was decided, why, and whether it has been verified.

## Scope (agreed with David, 12 November 2026)

| Decision | Reason |
| --- | --- |
| Fabulous OS **replaces Windows** on the mini-PC (it is the only system). | David needs no Windows-only programs. Strongest privacy: no Microsoft software remains. A Linux system cannot sit "on top of" Windows and police it. |
| First and only target for now: the **Beelink mini-PC** (Celeron N5105, 16 GB). | David's choice. The Zorin laptop and Raspberry Pi 5 are dropped from version 1. |
| Version 1 installer offers **"replace everything on the chosen disk"** only. | Follows from the above. Keep/shrink scenarios (brief 8.4 B–D) and the Setup helper (8.7) are deferred. |
| Browsers: **Tor Browser and Brave** (Brave's rewards and usage reports off). No Firefox, no Thunderbird. | David's choice. Not yet implemented; Brave's default network behaviour still to be verified. |
| Name: **Fabulous OS**. Trademark check deferred until any public release. | David's choice. |
| Image is built and test-started on **GitHub's build servers**; the repository is public. | Claude's workspace cannot reach Debian's servers, has no VM acceleration and cannot deliver a multi-GB file. Public repositories get free build time. |

## Base system

| Decision | Reason | Verified? |
| --- | --- | --- |
| Base: **Debian 13 "trixie", amd64**. | Full Debian support until 9 August 2028, then LTS until 30 June 2030 (debian.org/releases/stable), i.e. more than three years of security support from today. Debian 14 is not released. | Dates verified 12 Nov 2026. |
| Desktop: **KDE Plasma** for all machines. | Windows 11 look (centred taskbar) is native to Plasma; one desktop halves testing. Fine on 16 GB. | Not yet tested on the Beelink. |
| Wallpaper: mandala by default, plain blue-grey (#4a637a) alternative. | David's request. | Draft drawn; not yet set as the Plasma default. |
| Installer: Calamares with Debian's default settings in phase 1. | Brief phase 1. Custom screens come in phase 3. | Untested until first build. |
| Secure Boot: Debian's signed shim, GRUB and kernel, unchanged. | Brief section 5. | Untested until first build (workflow starts the image under Secure Boot firmware). |

## Gemma

| Decision | Reason | Verified? |
| --- | --- | --- |
| Model source: Google's own Q4_0 GGUF files (e.g. `google/gemma-4-E2B-it-qat-q4_0-gguf` on Hugging Face). | Google's Gemma documentation lists official QAT Q4_0 collections. | Existence seen via Google's docs page and a third-party listing; exact file names, sizes and checksums still to be recorded in `models.lock`. |
| Mini-PC gets **Gemma 4 E2B** with a "will answer slowly" note. | 16 GB would give E4B, but no AVX2 steps down one size (rules.yaml). | Rule tested; real speed unmeasured. |
| 3–6 GB machines get no model for now. | No small build has been tested (brief 8.5.2). | — |

## Not yet verified (carried from the brief)

- That GitHub's build servers can build this image and start it in a test machine (first workflow run will show).
- live-build option names in `build/auto/config` against Debian 13's live-build version.
- ArtCraft "Craft" apps: state and packaging (phase 5).
- LiteRT-LM on x86-64 Linux (phase 4).

## Added 12 November 2026 (branding pass)

| Decision | Reason | Verified? |
| --- | --- | --- |
| `os-release` keeps `ID=debian` (the brief asked for `ID=fabulous`); only the names change. GRUB's distributor name stays "Debian". | Debian's signed GRUB, needed for Secure Boot, looks for its files under `EFI/debian`, and that folder name is derived from these values. A wrong name risks an installed system that will not start. Cosmetic cost: the start-up menu of an installed system says "Debian". | Reasoned, not yet tested by a real install. |
| App installer: KDE **Discover**, with Flathub added as a second source. | David asked for a click-to-install app store. Discover is KDE's own and handles install, remove and updates. Flathub widens the choice. It uses the network only when opened. | In the image; not yet tried. |
| Brave is installed from Brave's own signed repository, with a policy file switching off rewards, wallet, VPN, AI chat, usage reports and the daily stats ping. | Brave is not in Debian. | Policy names not yet verified against Brave's documentation; unknown names are ignored by the browser. |
| Tor Browser via Debian's `torbrowser-launcher`. | It downloads and verifies the real Tor Browser on first use, so it stays current. Needs the internet once, as any browser does. | Not yet tried. |
| The Debian welcome window is switched off; Firefox and Konqueror are removed if nothing else depends on them. | David's browser choice. | Checked per build in the log. |

## Added 13 November 2026 (security; target PC confirmed)

| Decision | Reason | Verified? |
| --- | --- | --- |
| Target PC **stays the Beelink** (N5105, 16 GB). | On the morning of 13 November David proposed an AWOW mini-PC instead (8 GB; processor read as a Celeron J4125, which has neither AVX nor AVX2 per Intel's specification page). Under the rules that PC gets no Gemma, so David reverted to the Beelink the same morning. | — |
| **Firewall on from the first start**: `ufw`, refusing all incoming connections and allowing outgoing ones, in the stick session and the installed system. Settings page: `plasma-firewall`. | David's request. Costs nothing; a desktop PC needs no incoming connections. | See TESTING.md. |
| **Virus scanner: ClamAV, scan-on-request only.** No always-on scanning service. Signature updates run only on an installed system, not from the stick. | David's request. Honest limits: ClamAV chiefly recognises Windows malware; its always-on service holds over 1 GB of memory; Linux desktop malware is rare. The main protections are security updates, the firewall, and installing only from the app store. | See TESTING.md. |
| The image carries a **self-check** (`fabulous-selftest`) that reports firewall, Secure Boot and other facts to a test machine's serial port. It runs only inside a virtual machine that hands it a specific credential. | Screenshots cannot show whether the firewall or Secure Boot is really on. | See TESTING.md. |
| Probe: eMMC boot areas are not treated as disks; an SD card in a built-in card slot is treated as removable (never an install target). | Some mini-PCs have eMMC storage, and David's stick is an SD card. | Unit-tested with expected data, not a recording. |
| Signature updates and (later) security updates use the network without being asked each time. Non-negotiable 4 covers telemetry, the installer and the assistant; it is read as not forbidding security updates. | An unpatched system or a scanner without signatures is worse than none. | David to confirm this reading. |
| The installer asks a yes/no question before erasing (`prompt-install: true`). | Debian's setting starts erasing the moment Install is pressed. A typed confirmation (non-negotiable 3) still has to be built in step 4. | Seen in build 6's install test. |
| The background Tor service that comes with Tor Browser's launcher is switched off. | It connected to the Tor network at every start without being asked. Tor Browser carries its own. | Build 6 self-check: nothing listening. Tor Browser itself not yet opened. |
| The system's name is written directly to `/etc/os-release` as well as `/usr/lib/os-release`. | Build 5's self-check showed the running system still calling itself Debian; why the first method failed is not known. `ID=debian` is unchanged. | Build 6 self-check: "Fabulous OS 0.1", stick and installed. |
| Test tooling in `tests/`: `install-test.sh` runs on every build; `remote-vm.sh` lets Claude operate a test machine step by step. | The installer could not otherwise be tested without David's PC. | Used 13 November. |

## Added 13 November 2026, afternoon (option B: external drive)

| Decision | Reason | Verified? |
| --- | --- | --- |
| **Fabulous OS is installed on an external USB SSD. The Beelink's internal disk (477 GB, Windows) is never changed.** This replaces "Fabulous OS replaces Windows completely" of 12 November. | David wants a sure way back. Renaming the Windows folder (as Windows upgrades do) is not possible for Linux. To go back: unplug the drive. | See TESTING.md. |
| In the stick session every internal disk is made **read-only** at start-up (`fabulous-stick-session`). | The installer's first choice was the internal Windows disk, with "Erase disk" one click away. With the disk read-only the installer offers only external drives, and the kernel refuses any write to it. | Tried by hand in a test machine on build 6; built in from build 7. |
| Rules: only external drives are install targets; internal disks never. | Follows from option B. | Unit-tested. |
| Start-up files go in the removable-drive location (`EFI/BOOT`) as well, and nothing is written to the PC's firmware memory (`fabulous-grub-install`). | A hand test showed that with wiped firmware memory the external drive did not start: Debian's installer relies on an entry in the PC's firmware. | See TESTING.md. |
| Installer starts in **London**. | David agreed after Claude explained that a New York clock adds no anonymity and makes Brave more distinctive. | Tried by hand on build 6; built in from build 7. |
| Updates: the system checks daily and shows a pop-up; David clicks to install. No silent installs. | David's choice. The check itself uses the network. | Setting names unverified. |
| Virus signatures are fetched when the Virus Scanner is opened; no background downloading. | David's choice. | See TESTING.md. |
| Stick session: password safe (KDE Wallet) off, update pop-ups off. | The stick has no log-in password to lock a safe with; updating a stick session is pointless. | See TESTING.md. |
| Installer pictures and log-in screen use the mandala; the installer picture says "based on Debian". The app store is labelled "App Store". | David's request; Debian's trademark rules. | See TESTING.md. |

## Added 14 November 2026 (Gemma 4)

| Decision | Reason | Verified? |
| --- | --- | --- |
| Model: **Gemma 4 E2B**, Google's own file `gemma-4-E2B_q4_0-it.gguf` (3.35 GB) from `google/gemma-4-E2B-it-qat-q4_0-gguf`, pinned to revision `675cff4` and to its SHA-256 in `models.lock`. The build refuses any file that is not from Google's repository or does not match. | Non-negotiable 5. Licence Apache 2.0; the repository is not gated (no sign-up). | Checksum compared with the value Google's repository publishes, 14 Nov 2026. Refusal of a wrong checksum and of a non-Google address tried by hand. |
| The model travels **inside the image** (which grows from 2.5 GB to about 6 GB). Nothing is downloaded on the PC. | "Offline assistant"; non-negotiable 4. | See TESTING.md. |
| **Text only.** Google's 1 GB add-on for pictures and audio (`mmproj`) is left out. | Smaller image; David can ask for it. | — |
| Program that runs the model: **llama.cpp**, built from source at one fixed commit (`build/llama.lock`: b12110, the build its release v0.9.0 points to), inside Debian 13 on the build server. MIT licence, shipped. This replaces the "LiteRT-LM" idea of 12 November. | Debian 13 has nothing that can run Gemma 4, and Google's page for this file names llama.cpp. Built without its web page, without HTTPS and without any downloading ability. | See TESTING.md. |
| One program for every processor: the calculating part is built in all variants and chosen at start. The Beelink's **N5105 has neither AVX2 nor AVX** (Intel lists SSE4.2 as its highest), so it uses the plain SSE4.2 variant. | Brief v4 said "lacks AVX2"; checked against Intel's page on 14 Nov 2026. | Speed on the Beelink itself unmeasured. In Claude's workspace (2 cores of a 2.3 GHz Xeon) the SSE4.2 variant gave 5 tokens a second against 14 with everything on. |
| **The assistant has no network at all.** It is started inside its own empty network namespace (`unshare --net`) and spoken to through a private socket file, not a network port. If that cannot be set up, Gemma refuses to start. | Non-negotiable 4, enforced by the system rather than by a setting. | See TESTING.md. |
| Chat window: `fabulous-gemma` (Python, Qt), on the taskbar and in the start menu as "Gemma". One window at a time. Reasoning mode off, 8,192-token working memory, Google's recommended sampling settings. | Short, quick answers matter on a slow processor. | See TESTING.md. |
| Rules: E2B's memory figure raised from 2.9 to 3.5 GB. | Measured: 3.47 GB in use while answering. | Measured in Claude's workspace. |
| Test machines have 8 GB of memory and 4 cores (were 4 GB, 3 cores). The installed-system test runs on a processor model without AVX ("Westmere"). | Gemma does not fit in 4 GB beside the desktop; the Beelink has no AVX. | — |

## Added 14 November 2026, afternoon (pictures and recordings)

| Decision | Reason | Verified? |
| --- | --- | --- |
| **Gemma gets Google's add-on for pictures and sound recordings** (`gemma-4-E2B-it-mmproj.gguf`, 0.99 GB, same repository, revision and licence; pinned in `models.lock`). This reverses "text only" of this morning. | David's request, on condition that ordinary chat is not slowed. Measured: it is not (4.8 against 5.0 tokens a second). | See TESTING.md. |
| The window has "Add a picture…" and "Add a recording…" (files only; no microphone). Large pictures are shrunk to 1,600 pixels. | Simplest thing that works. | Buttons themselves not clicked in a test. |
| The question is sent before the attachment, and sampling is less inventive (temperature 0.2) whenever a picture or recording is in the conversation. | The other order made Gemma deny it could hear; the normal setting misheard a time of day in 5 of 9 tries in one batch. | Workspace tests. |
| Pictures are looked at in the model's standard detail, not reduced. | Reduced detail was faster (80 s against 145 s) but reading writing in pictures matters. David may prefer speed. | — |
| Rules: E2B's memory figure is now 4.6 GB. | Measured with the add-on loaded. | Workspace. |
