# Fabulous OS: Brief, version 3

**A Linux system with an offline AI assistant (Gemma 4), to replace Windows on a PC**

Prepared for David, 13 November 2026. This replaces the brief of 12 November 2026. Where the two disagree, this one wins.

---

## 1. How to use this brief

**For David.** This is the record of where the project stands. Section 2 is the short version. Section 9 lists what you will be asked to do.

**For Claude, in any later session.** The project lives on GitHub at `Pizzazz69/fabulous-os`. A new session does not remember this one, so start by reading this brief, then `DECISIONS.md` and `TESTING.md` in the repository. Work through section 7 in order. After each step, tell David plainly what was tested and what was not.

---

## 2. Where things stand

| | |
| --- | --- |
| Project home | GitHub repository `Pizzazz69/fabulous-os` (public) |
| Latest image | Build 6, 2.5 GB, built on GitHub's servers |
| What it does | Starts from a USB stick to a Fabulous OS desktop, and installs itself onto a blank disk |
| Installer | Run automatically in a test machine: installs, restarts from the disk, logs in. Passed. |
| Firewall | On from the first start, stick and installed. Checked from inside the system. |
| Virus scanner | ClamAV, scan when asked. Detected the standard test file. |
| Secure Boot | Confirmed enforcing from inside the system, stick and installed |
| Tested on the Beelink | Not yet. Nothing has run on any real PC. |
| Gemma 4 | Not yet included |

---

## 3. The goal

Build **Fabulous OS**: a Linux system based on **Debian 13**, delivered as an image file that is written to a USB stick. A PC that currently runs Windows starts from the stick, and Fabulous OS is installed as the **only** system on that PC, replacing Windows. It brings a Windows 11-style desktop, private browsers, an app store, a firewall, free office and creative apps, and **Gemma 4**, an AI assistant that runs entirely on the computer.

**What it is not.** It is not a new operating system written from scratch. Debian supplies the kernel, the drivers for the hardware, Secure Boot support and security updates. Fabulous OS is the layer on top.

**Target.** David's Beelink mini-PC (Intel Celeron N5105 at 2.00 GHz, 16 GB of memory, Windows Pro). On 13 November an AWOW mini-PC with 8 GB was considered instead and rejected the same morning: by the project's rules it would get no Gemma. Still dropped: the old Zorin laptop, the Raspberry Pi 5, keeping Windows beside Fabulous OS, and the helper that restarts into the installer from Windows.

---

## 4. Decisions

Decisions of 12 November stand (see `DECISIONS.md`): replace Windows completely; Debian's drivers; KDE Plasma in Windows 11 style; mandala wallpaper; Brave and Tor Browser, no Firefox; no email; Discover app store with Flathub; built on GitHub's servers; Debian 13; Gemma 4 E2B for the Beelink with a "will answer slowly" note; internal ID stays "debian".

**Added 13 November 2026:**

| Topic | Decision | Reason |
| --- | --- | --- |
| Target | Stays the Beelink. | The 8 GB AWOW would get no Gemma. |
| Firewall | On from the first start: refuses everything incoming, allows outgoing. Settings page in System Settings. | David's request. Costs nothing. |
| Virus scanner | ClamAV with a window ("Virus Scanner"), scan when asked. No always-on scanning. | David's request. Always-on scanning holds over 1 GB of memory, and ClamAV mostly recognises Windows viruses. The real protections on Linux are security updates, the firewall, and installing only from the app store. |
| Erasing | The installer asks a yes/no question before erasing. | Debian's installer erased the moment Install was pressed. A typed confirmation is still to come (step 4). |
| Tor | The background Tor service is off. Tor Browser is unaffected. | It connected to the Tor network at every start, unasked. |
| Self-check | The image contains a small program that reports facts to a test machine. It does nothing on a real PC. | Screenshots cannot prove a firewall is on. |

**Waiting for David's answer:** may security updates and virus-signature updates use the internet by themselves? Non-negotiable 4 forbids telemetry and unasked network use by the installer and the assistant; Claude reads it as allowing security updates, but has not been told so.

---

## 5. What exists today

**In the repository:** `build/` (the recipe), `packages/fabulous-probe/` (reads a PC's hardware), `rules/` (chooses the Gemma model and app set), `tests/` (drives the test machines; the install test), `.github/workflows/` (build, test, publish screenshots), `DECISIONS.md`, `TESTING.md`, `docs/` (this brief).

**In the image (build 6):**

- Everything in build 4: name, mandala, centred taskbar, Brave, Tor Browser launcher, Discover with Flathub, Debian's installer renamed, the probe and rules programs.
- Firewall (ufw), on.
- ClamAV and its window.
- The self-check.
- The installer's "Continue with Installation?" question.

**Tests that pass:** 19 automated tests of the probe and rules; image build; start to the desktop in both test machines; the automated install test; the self-checks listed in `TESTING.md`.

---

## 6. What is not done or not verified

- **Nothing has run on the Beelink or any real PC.**
- The installer was tested on a **blank** disk. Installing over Windows, and over a BitLocker-encrypted disk, is untested.
- **The installer starts in New York**, not London. Not fixed.
- **No typed confirmation** before erasing; only a yes/no question.
- Debian's wording and pictures remain in the installer and on the log-in screen. The stick's start-up menu still says "Debian GNU/Linux", and an installed system's will say "Debian".
- Brave opens, but shows a "KDE Wallet" question first. Its privacy setting names are unchecked.
- Tor Browser and the app store have not been opened.
- ClamAV's automatic signature updates are unconfirmed.
- The app store checks for updates by itself in the stick session.
- No Gemma, no LibreOffice, no creative apps.
- The plain-question installer screens are not built; the installer does not use the probe and rules.
- The probe's test data is the expected profile of the Beelink, not a recording.
- The mandala is not yet in a folder David can open and edit.
- The ArtCraft "Craft" apps have not been looked at.

---

## 7. Next steps, in order

1. ~~Automated install test.~~ Done 13 November.
2. **Gemma 4.** The assistant program, the model and the chat window. Include a test on a machine without AVX2.
3. **Office and creative apps.**
4. **The plain-question installer screens**, including the typed confirmation.

Small items to fold in along the way:

- Make the installer start in London.
- Stop Brave's "KDE Wallet" question; check Brave's settings; open Tor Browser and the app store once in a test machine.
- Install-test over a disk that holds Windows partitions.
- Put the mandala and the plain background in a folder the user can open.
- Rename the stick's start-up menu; replace the remaining Debian wording and pictures.
- Settle automatic updates (see section 4).

Each build takes about 20 minutes, plus about 30 minutes of testing.

**After step 4:** David tries the stick on the Beelink in "Try it first" mode, which changes nothing. Only after that, and after a backup, comes a real install. David may try "Try it first" earlier if he wishes; see section 9.

---

## 8. How a build works

1. Claude changes files in the repository and uploads them to GitHub.
2. GitHub's servers build the image inside Debian 13 (about 15 minutes).
3. The servers start the image in two test machines, photograph the screens, and record the self-check.
4. The servers install the image onto a blank test disk, restart from it, log in, and check it.
5. Claude views the screenshots, self-checks and build log, and records the result in `TESTING.md`.
6. When a build is ready for David, he downloads the image from the repository's **Actions** page on github.com.

Claude can see the screenshots and logs, but cannot download the image itself. Claude can also operate a test machine step by step ("Remote-controlled test machine").

---

## 9. What David will be asked to do

1. **When an image is ready to try:** download it from GitHub, write it to the stick with balenaEtcher (choose file, choose stick, press Flash), and start the Beelink from the stick by tapping the boot key at power-on (usually F7 on a Beelink). Claude will supply a step-by-step guide.
2. **"Try it first":** look around the desktop, check Wi-Fi and sound, and report what you see. **Do not double-click "Install Fabulous OS"** until Claude says the installer is ready: it can erase the disk after one yes/no question.
3. **Before any real install:** copy everything you want to keep off the Beelink. Installing erases Windows and everything on the disk.
4. **The stick:** the new 128 GB SD card is large enough for everything planned. It must go in a **USB card reader**; most PCs cannot start from a built-in SD card slot. Writing the image erases the card.

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

Not yet met: 3 (yes/no only), and 6 for Tor Browser and the app store (included but never opened).

---

## 11. Review of the session of 13 November 2026

**Change of PC, and back.** David proposed an AWOW mini-PC with 8 GB. Claude read its processor as a Celeron J4125, which Intel lists without AVX or AVX2, and reported that the rules would give it no Gemma. David reverted to the Beelink. The extra disk-safety checks written for the AWOW (eMMC storage, SD cards) were kept.

**Security.** A friend advised a firewall and antivirus from the start "or it will quickly be a target of hackers". Claude's answer: the firewall is worth having and is now on; the hacker claim is overstated for a Linux desktop; the antivirus is included in its light form with its limits stated.

**Builds.**

| Build | Result |
| --- | --- |
| 5 | Firewall, ClamAV, self-check. Self-check showed two faults: the system still called itself Debian inside, and a background Tor service was running. |
| 6 | Both fixed. Installer asks before erasing. Automated install test added and passed. One warning: the London fix did not take. |

**Mistakes by Claude this session.** A test helper had a wrong file path, costing two short test runs. The fix for the installer's starting place did not work.

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
| Test machine | A pretend PC on GitHub's servers, used to try the image. |
| Self-check | A small program in the image that reports facts (firewall on? Secure Boot on?) to a test machine. |
| Firewall | Software that refuses connections coming in from the network. |
| ClamAV | The virus scanner. It checks files when asked. |
| KDE Plasma | The desktop: taskbar, start menu, windows, settings. |
| Discover | The app store. Search, press Install or Remove. |
| Flathub | A large online collection of Linux apps that Discover can install from. |
| AVX2 | Processor instructions that make AI models faster. The N5105 lacks them. |
| Gemma 4 E2B | The smaller of the two Gemma 4 models considered; about 3 GB. |

---

## 13. Sources checked on 13 November 2026

- Celeron J4125 instruction set (SSE4.2 highest): https://www.intel.com/content/www/us/en/products/sku/197305/intel-celeron-processor-j4125-4m-cache-up-to-2-70-ghz/specifications.html
- AWOW 8 GB / 128 GB J4125 model: https://www.galaxus.ch/en/s1/product/awow-mini-pc-win11-pro-celeron-j4125-8gb-ram-128gb-m2-pc-21876616

Not re-checked today: Debian 13 support dates, Gemma 4 files, the N5105's lack of AVX2, the ArtCraft apps. The statements about ClamAV's memory use and what it detects are from Claude's general knowledge, not checked against a source today.
