# Fabulous OS: Brief, version 4

**A Linux system with an offline AI assistant (Gemma 4), run from an external drive beside an untouched Windows PC**

Prepared for David, 13 November 2026 (evening). This replaces brief version 3 of the same morning. Where the two disagree, this one wins.

---

## 1. How to use this brief

**For David.** This is the record of where the project stands. Section 2 is the short version. Section 9 lists what you will be asked to do.

**For Claude, in any later session.** The project lives on GitHub at `Pizzazz69/fabulous-os`. A new session does not remember this one, so start by reading this brief, then `DECISIONS.md` and `TESTING.md` in the repository. Work through section 7 in order. After each step, tell David plainly what was tested and what was not.

---

## 2. Where things stand

| | |
| --- | --- |
| Project home | GitHub repository `Pizzazz69/fabulous-os` (public) |
| Latest image | Build 8, 2.5 GB, built on GitHub's servers |
| Plan ("option B") | Fabulous OS lives on an **external USB SSD**. The Beelink's internal disk and Windows are never changed. To go back: unplug the drive. |
| Installer | Tested automatically: installs onto an external drive, which then starts by itself under Secure Boot. The internal disk was byte-for-byte unchanged. |
| Protection | When started from the stick, every internal disk is read-only; the installer offers only external drives. |
| Firewall, virus scanner, Secure Boot | Checked from inside the installed system. |
| Tested on the Beelink | Not yet. Nothing has run on any real PC. |
| External SSD | David is buying one (a known brand, 250 GB or more). |
| Gemma 4 | Not yet included |

---

## 3. The goal

Build **Fabulous OS**: a Linux system based on **Debian 13**, delivered as an image file that is written to a USB stick. The PC starts from the stick, and Fabulous OS is installed onto an **external USB SSD**. Windows stays on the PC's internal disk, untouched; whichever drive the PC starts from decides which system runs. Fabulous OS brings a Windows 11-style desktop, private browsers, an app store, a firewall, free office and creative apps, and **Gemma 4**, an AI assistant that runs entirely on the computer.

**What it is not.** It is not a new operating system written from scratch. Debian supplies the kernel, the drivers, Secure Boot support and security updates. Fabulous OS is the layer on top.

**Target.** David's Beelink mini-PC (Intel Celeron N5105 at 2.00 GHz, 16 GB of memory, 477 GB internal disk, Windows Pro). An 8 GB AWOW mini-PC was considered on 13 November and rejected: by the project's rules it would get no Gemma.

**History of the plan.** 12 November: replace Windows completely. 13 November: David asked for a way back like Windows' own "rename the old Windows folder". That cannot work for Linux, so he chose the external drive instead.

---

## 4. Decisions

Decisions of 12 November stand (see `DECISIONS.md`): replace Windows completely; Debian's drivers; KDE Plasma in Windows 11 style; mandala wallpaper; Brave and Tor Browser, no Firefox; no email; Discover app store with Flathub; built on GitHub's servers; Debian 13; Gemma 4 E2B for the Beelink with a "will answer slowly" note; internal ID stays "debian".

**Added 13 November 2026:**

| Topic | Decision | Reason |
| --- | --- | --- |
| Where it is installed | On an external USB SSD. Internal disks are never install targets. This replaces "replace Windows completely". | David wants a sure way back. |
| Protection | In the stick session every internal disk is made read-only. | Debian's installer preselected the internal Windows disk. |
| Starting | The drive carries its start-up files in the standard removable-drive place, and the installer is told to write nothing into the PC's firmware. | The drive must start from the boot-key menu on its own. |
| Firewall | On from the first start: refuses everything incoming, allows outgoing. | David's request. |
| Virus scanner | ClamAV with a window ("Virus Scanner"). Signatures are fetched when it is opened. No always-on scanning, no background downloading. | David's request and choice. Limits: mostly recognises Windows viruses. |
| Updates | The system checks daily and shows a pop-up; David clicks to install. | David's choice. |
| Installer's starting place | London. | A New York clock adds no anonymity. |
| Erasing | The installer asks yes/no before erasing the external drive. A typed confirmation is still to come. | Non-negotiable 3. |
| Tor | The background Tor service is off. Tor Browser is unaffected. | It connected at every start, unasked. |
| Branding | Mandala in the installer and on the log-in screen; "based on Debian" on the installer's picture; app store labelled "App Store". | David's request. |
| Brave | Kept. | The "KDE Wallet" question does not appear on an installed system. |

---

## 5. What exists today

**In the repository:** `build/` (the recipe), `packages/fabulous-probe/` (reads a PC's hardware), `rules/` (chooses the Gemma model and app set), `tests/` (drives the test machines; the install test), `.github/workflows/` (build, test, publish screenshots), `DECISIONS.md`, `TESTING.md`, `docs/` (this brief).

**In the image (build 8):**

- Desktop: name, mandala, centred taskbar, Brave, Tor Browser launcher, app store with Flathub.
- Debian's installer, renamed, with mandala pictures, starting in London, asking before it erases, putting start-up files where an external drive needs them.
- Stick-session protection: internal disks read-only.
- Firewall (ufw), on. ClamAV, its window, and the fetch-signatures-when-opened service.
- The probe and rules programs (not yet used by the installer), and the self-check.

**Tests that pass:** 19 automated tests of the probe and rules; image build; start to the desktop in both test machines; the automated install test for option B; the self-checks listed in `TESTING.md`.

---

## 6. What is not done or not verified

- **Nothing has run on the Beelink, a real external SSD, or a real Windows disk.** The test's "Windows" disk is a pretend one that cannot start; that Windows starts as before is argued from the disk being unchanged.
- Not checked: that nothing is written to the PC's firmware memory during install.
- **No typed confirmation** before the external drive is erased; only a yes/no question.
- The log-in screen still shows a small "debian" logo. The installer's heading still says "Calamares installer". The stick's start-up menu says "Debian GNU/Linux", and the installed system's will say "Debian".
- Not tested: opening the Virus Scanner from the menu; the daily update pop-up; the "App Store" label; Brave in the stick session; Tor Browser; the app store itself.
- Brave's privacy setting names are unchecked.
- No Gemma, no LibreOffice, no creative apps. Gemma from an external drive is untested.
- The plain-question installer screens are not built; the installer does not use the probe and rules.
- The probe's test data is the expected profile of the Beelink, not a recording.
- The mandala is not yet in a folder David can open and edit.
- The ArtCraft "Craft" apps have not been looked at.
- If Windows on the Beelink uses BitLocker, David should have his recovery key to hand before first starting from another drive. Claude does not expect it to be asked for, but has not tested it.

---

## 7. Next steps, in order

1. ~~Automated install test.~~ Done 13 November, then redone for option B.
2. **Gemma 4.** The assistant program, the model and the chat window. Include a test on a machine without AVX2.
3. **Office and creative apps.**
4. **The plain-question installer screens**, including the typed confirmation.

Small items to fold in along the way:

- Remove the "debian" logo from the log-in screen; reword the installer's heading; rename the stick's start-up menu.
- Test the Virus Scanner from the menu, the update pop-up, Tor Browser and the app store in a test machine.
- Check Brave's settings.
- Put the mandala and the plain background in a folder the user can open.

Each build takes 40 to 50 minutes in all, of which about 25 is testing.

**When David has the SSD:** he may try "Try it first" on the Beelink at any time; it cannot change the internal disk. Installing onto the SSD is reasonably safe from build 8 on, with the SSD being the only thing that can be erased, but Claude would prefer the typed confirmation (step 4) first.

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

1. **Buy an external SSD:** a known brand (Samsung, Crucial, SanDisk, Kingston) from a known UK retailer, 250 GB or more. Not the "128 TB for £30" kind; those are fakes.
2. **When an image is ready to try:** download it from GitHub, write it to the stick with balenaEtcher, and start the Beelink from the stick by tapping the boot key at power-on (usually F7 on a Beelink). Claude will supply a step-by-step guide.
3. **"Try it first":** look around the desktop, check Wi-Fi and sound, and report what you see.
4. **Install:** plug in the SSD, run the installer, choose the SSD. Everything on the SSD is erased. The internal disk is read-only throughout.
5. **Afterwards:** tap F7 at power-on and choose the SSD to start Fabulous OS. Unplug it, or just don't press F7, and the PC starts Windows as before.
6. **The stick:** the 128 GB SD card in a **USB card reader**. Writing the image erases the card.

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

Non-negotiable 4, as David clarified on 13 November: a daily check for updates with a pop-up is acceptable; installing is by his click.

---

## 11. Review of the session of 13 November 2026

**Change of PC, and back.** David proposed an AWOW mini-PC with 8 GB. Claude read its processor as a Celeron J4125, which Intel lists without AVX or AVX2, and reported that the rules would give it no Gemma. David reverted to the Beelink. The extra disk-safety checks written for the AWOW (eMMC storage, SD cards) were kept.

**Security.** A friend advised a firewall and antivirus from the start "or it will quickly be a target of hackers". Claude's answer: the firewall is worth having and is now on; the hacker claim is overstated for a Linux desktop; the antivirus is included in its light form with its limits stated.

**Builds.**

| Build | Result |
| --- | --- |
| 5 | Firewall, ClamAV, self-check. Self-check showed two faults: the system still called itself Debian inside, and a background Tor service was running. |
| 6 | Both fixed. Installer asks before erasing. Automated install test added and passed. One warning: the London fix did not take. |

**Afternoon: option B.** David asked whether Fabulous OS could be installed the way a Windows upgrade keeps "Windows.old". It cannot; of three alternatives he chose the external drive. He also asked about two "128 TB" and "256 TB" SSD listings at about £30; Claude checked and reported them as fakes.

| Build | Result |
| --- | --- |
| 7 | Internal disks read-only in the stick session; London; branding; signatures on request. Install test failed: the external drive would not start by itself. |
| 8 | Fixed. Install test for option B passed with 0 problems. |

**Found by testing, which would have hurt on the real PC:** the installer preselected the internal Windows disk; an external drive installed by Debian's installer does not start by itself once the PC forgets it.

**Mistakes by Claude this session.** A test helper had a wrong file path. The first London fix did not work. An edit for build 7 deleted the lines that put "Fabulous OS" in the installer's wording. A hand test of the start-up fix was spoiled by a mistyped command, costing about 20 minutes. Two scratch branches (`vm-control`, `vm-screen`) remain in the repository.

---

## 12. Short glossary

| Word | Plain meaning |
| --- | --- |
| Image / ISO | The single file that is written onto the USB stick. |
| Boot key | A key tapped at power-on (usually F7 on a Beelink) that lets the PC start from the stick once. |
| Secure Boot | A safety feature that only starts software signed by trusted keys. Debian is signed, so it stays on. |
| "Try it first" | Running Fabulous OS from the stick without installing anything. |
| External SSD | A small, fast drive that plugs into a USB socket. Fabulous OS will live on it. |
| Read-only | Can be looked at but not changed. |
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
