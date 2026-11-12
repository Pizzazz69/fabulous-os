# Fabulous OS: Brief, version 2

**A Linux system with an offline AI assistant (Gemma 4), to replace Windows on a PC**

Prepared for David, 12 November 2026. This replaces the brief of 11 November 2026. Where the two disagree, this one wins.

---

## 1. How to use this brief

**For David.** This is the record of where the project stands. Section 2 is the short version. Section 9 lists what you will be asked to do.

**For Claude, in any later session.** The project lives on GitHub at `Pizzazz69/fabulous-os`. A new session does not remember this one, so start by reading this brief, then `DECISIONS.md` and `TESTING.md` in the repository. Work through section 7 in order. After each step, tell David plainly what was tested and what was not.

---

## 2. Where things stand

| | |
| --- | --- |
| Project home | GitHub repository `Pizzazz69/fabulous-os` (public) |
| Latest image | Build 4, 2.5 GB, built on GitHub's servers |
| What it does | Starts from a USB stick to a Fabulous OS desktop |
| Tested how | In two test machines on GitHub's servers (Secure Boot firmware, and legacy BIOS), by screenshot |
| Tested on the Beelink | Not yet |
| Installer run | Not yet |
| Gemma 4 | Not yet included |

---

## 3. The goal

Build **Fabulous OS**: a Linux system based on **Debian 13**, delivered as an image file that is written to a USB stick. A PC that currently runs Windows starts from the stick, and Fabulous OS is installed as the **only** system on that PC, replacing Windows. It brings a Windows 11-style desktop, private browsers, an app store, free office and creative apps, and **Gemma 4**, an AI assistant that runs entirely on the computer.

**What it is not.** It is not a new operating system written from scratch. Debian supplies the kernel, the drivers for the hardware, Secure Boot support and security updates. Fabulous OS is the layer on top.

**Focus for now.** Only PCs that currently run Windows, and first of all David's Beelink mini-PC (Intel Celeron N5105 at 2.00 GHz, 16 GB of memory, Windows Pro). Dropped for now: the old Zorin laptop, the Raspberry Pi 5, keeping Windows beside Fabulous OS, and the helper that restarts into the installer from Windows.

---

## 4. Decisions made on 12 November 2026

| Topic | Decision | Reason |
| --- | --- | --- |
| Windows | Fabulous OS replaces Windows completely. | David needs no Windows-only programs. A Linux system cannot sit "on top of" Windows and police it; only one system runs a PC at a time. Replacing Windows is the strongest privacy option. |
| Hardware drivers | Debian's. | Windows no longer runs, so it cannot handle the hardware. Debian's drivers cover this class of mini-PC well; "Try it first" proves it on the real machine before anything is erased. |
| Target | The Beelink mini-PC only, for now. | David's choice. |
| Desktop | KDE Plasma, Windows 11 style, taskbar icons centred. | Closest to Windows 11; one desktop to test. |
| Wallpaper | Mandala by default; plain blue-grey alternative. | David's request. David approved the mandala draft. |
| Browsers | Brave and Tor Browser. No Firefox. | David's choice. |
| Email | None installed. | No email will be used on this PC. |
| App installer | KDE Discover (the shopping-bag icon), with Flathub added. | David asked for a click-to-install and click-to-remove app store. |
| Name | Fabulous OS. | "Fabulous" and "fable" share the Latin root *fabula*. Trademark check deferred until any public release. |
| Users | David only for now. Possibly a stick for Jemma later. | Nothing personal is built into the image. |
| Where it is built | GitHub's build servers, from the public repository. | Claude's own workspace cannot reach Debian's servers, cannot run test machines at speed, and cannot deliver a file of this size. |
| Base | Debian 13 "trixie". | Full support until 9 August 2028, then long-term support until 30 June 2030. |
| Gemma model for the Beelink | Gemma 4 E2B, with a "will answer slowly" note. | 16 GB would allow the larger E4B, but the N5105 lacks AVX2, so the rules step down one size. |
| System identity | The system is named Fabulous OS, but its internal ID and start-up folder stay "debian". | Debian's signed start-up program, needed for Secure Boot, expects that name. This departs from the first brief. |

---

## 5. What exists today

**In the repository:**

- `build/` — the recipe that turns Debian into the Fabulous OS image.
- `packages/fabulous-probe/` — reads a PC's processor, memory and disks, changing nothing.
- `rules/` — chooses the Gemma model and app set from what the probe finds.
- `.github/workflows/` — builds the image, starts it in two test machines, and saves screenshots.
- `DECISIONS.md`, `TESTING.md` — the records.
- `docs/` — this brief.

**In the image (build 4):**

- Fabulous OS name on the desktop and the install icon.
- Mandala wallpaper and centred taskbar: start button, files, Brave, app store, settings.
- Brave, with a settings file intended to switch off its rewards, wallet, VPN, AI chat and usage reports.
- Tor Browser, through Debian's launcher, which downloads the real Tor Browser on first use.
- Discover app store with Flathub.
- Debian's standard installer, renamed.
- The probe and rules programs (not yet used by the installer).

**Tests that pass:** 17 automated tests of the probe and rules; image build; start to the desktop in both test machines.

---

## 6. What is not done or not verified

- Nothing has run on the Beelink.
- The installer has never been run, even in a test machine.
- Brave, Tor Browser and Discover have not been opened.
- Brave's privacy setting names have not been checked against Brave's documentation.
- Secure Boot: the image started on Secure Boot firmware, but enforcement has not been confirmed from inside the running system.
- The stick's start-up menu still says "Debian GNU/Linux". An installed system's start-up menu will also say "Debian" (see section 4).
- No Gemma, no LibreOffice, no creative apps.
- The installer's plain-question screens from the first brief are not built.
- The probe's test data is the expected profile of the Beelink, not a recording from the real machine.
- The mandala is changeable through the desktop's wallpaper settings, but it is not yet in a folder David can open and edit. This is a small task for the next session.
- The ArtCraft "Craft" apps named in the first brief have not been looked at.

---

## 7. Next steps, in order

1. **Automated install test.** Have the build servers run the installer onto a blank test disk and restart from it, so we know installation works before it goes near the Beelink.
2. **Gemma 4.** The assistant program, the model and the chat window.
3. **Office and creative apps.**
4. **The plain-question installer screens.**

Small items to fold in along the way:

- Put the mandala and the plain background in a folder the user can open, and list both in the wallpaper settings.
- Rename the stick's start-up menu.
- Check Brave's settings and open each browser once in a test machine.

Each build takes about 25 minutes, and each step needs several builds.

**After step 4:** David tries the stick on the Beelink in "Try it first" mode, which changes nothing. Only after that, and after a backup, comes a real install.

---

## 8. How a build works

1. Claude changes files in the repository and uploads them to GitHub.
2. GitHub's servers build the image inside Debian 13 (about 15 minutes).
3. The servers start the image in two test machines and photograph the screens.
4. Claude views the screenshots and the build log, and records the result in `TESTING.md`.
5. When a build is ready for David, he downloads the image from the repository's **Actions** page on github.com.

Claude can see the screenshots and logs, but cannot download the image itself.

---

## 9. What David will be asked to do

1. **When an image is ready to try:** download it from GitHub, write it to a USB stick with balenaEtcher (choose file, choose stick, press Flash), and start the Beelink from the stick by tapping the boot key at power-on (usually F7 on a Beelink). Claude will supply a step-by-step guide.
2. **"Try it first":** look around the desktop, check Wi-Fi and sound, and report what you see. Nothing on the PC is changed.
3. **Before any real install:** copy everything you want to keep off the Beelink. Installing erases Windows and everything on the disk.
4. **USB sticks:** the 8 GB stick is enough until Gemma is added. After that, a 32 GB stick is needed.

Never paste a password into the chat. Claude's access to GitHub works through the link David approved, not a password.

---

## 10. Non-negotiables

1. Do not write a kernel or an operating system from scratch. Build on Debian.
2. Never ask the person to switch Secure Boot off.
3. Never erase a disk without an explicit, typed confirmation.
4. Nothing leaves the computer: no telemetry, and no network use by the installer or the assistant unless the person turns it on.
5. Gemma files only from Google's official releases, verified by checksum, shipped with their licence.
6. Every app listed has been tested. A broken app is worse than a missing one.
7. Respect every licence and Debian's trademark rules: say "based on Debian".
8. When unsure about anything that could lose data, stop and ask David.
9. Report truthfully: say what was tested, how, and what was not.

---

## 11. Review of the session of 12 November 2026

**Morning: questions on the first brief.** David answered the brief's six questions. His plan for the mini-PC was Fabulous OS "on top of" Windows, guarding it. Claude explained that this is not possible and set out three options: replace Windows, run Windows inside Fabulous OS, or have both side by side.

**A misunderstanding cleared up.** David had been put off replacing Windows by an earlier warning against writing an operating system from scratch. That warning was about writing a new kernel. Fabulous OS built on Debian as the only system is the simplest option, and David chose it once it was clear he needs no Windows-only programs.

**How to build it.** Claude checked its own workspace and found it could not build or deliver the image. After considering a build on David's own machine, we chose GitHub's build servers, which need no commands from David.

**GitHub set-up.** David shared a password in the chat; Claude did not use it and asked him to change it, which he did. Finding the right place to link GitHub took several attempts, because Claude's first directions did not match David's screen. The link was finally made at `claude.ai/code`, and David created the `fabulous-os` repository.

**Afternoon: four builds.**

| Build | Result |
| --- | --- |
| 1 | Image built first time; test stopped at the start-up menu. |
| 2 | Menu now continues by itself; plain Debian desktop reached in both test machines. |
| 3 | Centred taskbar, Brave, no Firefox, app store. A Debian welcome window and "Install Debian" icon remained. |
| 4 | Welcome window removed, icon renamed, mandala visible. No build warnings. |

**Also decided:** David asked for an easy app installer (Discover, already included, with Flathub added), approved the mandala, and asked for it to be user-changeable. A separate quick installer for Gemma 4 on a Raspberry Pi 5 was noted as a possible future project.

---

## 12. Short glossary

| Word | Plain meaning |
| --- | --- |
| Image / ISO | The single file that is written onto the USB stick. |
| Boot key | A key tapped at power-on (usually F7 on a Beelink) that lets the PC start from the stick once. |
| Secure Boot | A safety feature that only starts software signed by trusted keys. Debian is signed, so it stays on. |
| "Try it first" | Running Fabulous OS from the stick without installing anything. |
| Repository | The project's folder on GitHub. |
| Build | GitHub's servers turning the recipe into an image and testing it. |
| KDE Plasma | The desktop: taskbar, start menu, windows, settings. |
| Discover | The app store. Search, press Install or Remove. |
| Flathub | A large online collection of Linux apps that Discover can install from. |
| AVX2 | Processor instructions that make AI models faster. The N5105 lacks them. |
| Gemma 4 E2B | The smaller of the two Gemma 4 models considered; about 3 GB. |

---

## 13. Sources checked on 12 November 2026

- Debian 13 support dates: https://www.debian.org/releases/stable
- Gemma 4 official files and formats: https://ai.google.dev/gemma/docs/core
- GitHub build server sizes: https://docs.github.com/en/actions/reference/runners/github-hosted-runners

The first brief's other sources (on the N5105's lack of AVX2, and the ArtCraft apps) were not re-checked today.
