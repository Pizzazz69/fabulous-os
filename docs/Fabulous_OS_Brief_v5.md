# Fabulous OS: Brief, version 5

**A Linux system with an offline AI assistant (Gemma 4), run from an external drive beside an untouched Windows PC**

Prepared for David, 14 November 2026 (updated in the afternoon for build 11). This replaces brief version 4 of 13 November. Where the two disagree, this one wins.

---

## 1. How to use this brief

**For David.** This is the record of where the project stands. Section 2 is the short version. Section 9 lists what you will be asked to do.

**For Claude, in any later session.** The project lives on GitHub at `Pizzazz69/fabulous-os`. A new session does not remember this one, so start by reading this brief, then `DECISIONS.md` and `TESTING.md` in the repository. Work through section 7 in order. After each step, tell David plainly what was tested and what was not.

---

## 2. Where things stand

| | |
| --- | --- |
| Project home | GitHub repository `Pizzazz69/fabulous-os` (public) |
| Latest image | Build 11, 5.7 GB (was 2.5 GB before Gemma), built on GitHub's servers |
| Plan ("option B") | Fabulous OS lives on an **external USB SSD**. The Beelink's internal disk and Windows are never changed. To go back: unplug the drive. |
| Installer | Tested automatically: installs onto an external drive, which then starts by itself under Secure Boot. The internal disk was byte-for-byte unchanged. |
| Protection | When started from the stick, every internal disk is read-only; the installer offers only external drives. |
| Firewall, virus scanner, Secure Boot | Checked from inside the installed system. |
| Tested on the Beelink | Not yet. Nothing has run on any real PC. |
| External SSD | David is buying one (a known brand, 250 GB or more). |
| Gemma 4 | **Included from build 10; can look at pictures and listen to recordings from build 11.** Answers in test machines, including one shaped like the Beelink (no AVX, 16 GB). Speed on the real Beelink is unmeasured. |
| Office and creative apps | Not yet included (next step) |

---

## 3. The goal

Build **Fabulous OS**: a Linux system based on **Debian 13**, delivered as an image file that is written to a USB stick. The PC starts from the stick, and Fabulous OS is installed onto an **external USB SSD**. Windows stays on the PC's internal disk, untouched; whichever drive the PC starts from decides which system runs. Fabulous OS brings a Windows 11-style desktop, private browsers, an app store, a firewall, free office and creative apps, and **Gemma 4**, an AI assistant that runs entirely on the computer.

**What it is not.** It is not a new operating system written from scratch. Debian supplies the kernel, the drivers, Secure Boot support and security updates. Fabulous OS is the layer on top.

**Target.** David's Beelink mini-PC (Intel Celeron N5105 at 2.00 GHz, 16 GB of memory, 477 GB internal disk, Windows Pro). An 8 GB AWOW mini-PC was considered on 13 November and rejected: by the project's rules it would get no Gemma.

**History of the plan.** 12 November: replace Windows completely. 13 November: David asked for a way back like Windows' own "rename the old Windows folder". That cannot work for Linux, so he chose the external drive instead.

---

## 4. Decisions

Decisions of 12 November stand (see `DECISIONS.md`), except "replace Windows completely", which is withdrawn: Debian's drivers; KDE Plasma in Windows 11 style; mandala wallpaper; Brave and Tor Browser, no Firefox; no email; Discover app store with Flathub; built on GitHub's servers; Debian 13; Gemma 4 E2B for the Beelink with a "will answer slowly" note; internal ID stays "debian".

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

**Added 14 November 2026 (Gemma):**

| Topic | Decision | Reason |
| --- | --- | --- |
| Model | Gemma 4 E2B, Google's own file (3.35 GB), fixed to one revision and its checksum in `models.lock`. The build refuses anything else. | Non-negotiable 5. Apache 2.0 licence, shipped. |
| Where the model lives | Inside the image. Nothing is downloaded on the PC. | Offline from the first start. |
| Pictures and audio | **Included from build 11** (Google's 1 GB add-on), at David's request. Files only, no microphone. | Measured: ordinary chat is not slowed. A picture takes minutes. |
| Program that runs Gemma | llama.cpp, built from source at one fixed version (`build/llama.lock`) on the build server. Not from Debian. | Debian 13 has nothing that runs Gemma 4. MIT licence, shipped. |
| Network | The assistant is started with no network at all, and refuses to start if that cannot be arranged. | Non-negotiable 4, enforced by the system. |
| Window | "Gemma", on the taskbar and in the start menu. | — |
| KDE Connect | Removed. | It listened on the network and announced the PC as soon as the desktop started, unasked. Can be reinstalled from the App Store. David may reverse this. |

---

## 5. What exists today

**In the repository:** `build/` (the recipe), `models.lock` (which Gemma file, and its checksum), `packages/fabulous-gemma/` (the assistant and its window), `packages/fabulous-probe/` (reads a PC's hardware), `rules/` (chooses the Gemma model and app set), `tests/` (drives the test machines; the install test), `.github/workflows/` (build, test, publish screenshots), `DECISIONS.md`, `TESTING.md`, `docs/` (this brief).

**In the image (build 11):**

- Desktop: name, mandala, centred taskbar, Brave, Tor Browser launcher, app store with Flathub.
- Debian's installer, renamed, with mandala pictures, starting in London, asking before it erases, putting start-up files where an external drive needs them.
- Stick-session protection: internal disks read-only.
- Firewall (ufw), on. ClamAV, its window, and the fetch-signatures-when-opened service.
- Gemma 4 E2B with its add-on for pictures and recordings, the program that runs it, the chat window, and their licences.
- The probe and rules programs (not yet used by the installer; the Gemma window does use the rules), and the self-check.

**Tests that pass (build 11):** 41 automated tests of the probe, rules and assistant; image build with no warnings; start to the desktop in both test machines; Gemma answering, describing a test picture and writing down a test recording in three test machines; the automated install test for option B, now ending with a question typed into the Gemma window; the self-checks listed in `TESTING.md`.

---

## 6. What is not done or not verified

- **Nothing has run on the Beelink, a real external SSD, or a real Windows disk.** The test's "Windows" disk is a pretend one that cannot start; that Windows starts as before is argued from the disk being unchanged.
- Not checked: that nothing is written to the PC's firmware memory during install.
- **No typed confirmation** before the external drive is erased; only a yes/no question.
- The log-in screen still shows a small "debian" logo. The installer's heading still says "Calamares installer". The stick's start-up menu says "Debian GNU/Linux", and the installed system's will say "Debian".
- Not tested: opening the Virus Scanner from the menu; the daily update pop-up; the "App Store" label; Brave in the stick session; Tor Browser; the app store itself.
- Brave's privacy setting names are unchecked.
- No LibreOffice, no creative apps.
- **Gemma's speed on the Beelink is unmeasured.** The test machines hide AVX from a server processor whose cores are faster than the N5105's; they gave about 5 tokens (roughly 4 words) a second. Expect the Beelink to be slower than that; how much slower is not known.
- Gemma took about 4½ minutes to load when started from the image in a test machine, and 20 seconds from the installed external test drive. Times from a real stick and a real SSD are unmeasured.
- **Pictures are slow and not fully reliable.** On the no-AVX test machine the answer about a picture began after about 3 minutes; the Beelink will be slower. In every test Gemma described the test picture correctly but added a "22" that is not in it. Recordings took about 20 seconds and were written down correctly, but only one 4-second computer-voice sentence was tried on the build servers.
- The "Add a picture…" and "Add a recording…" buttons were not clicked in any automated test. No real photograph and no human voice has been tried. There is no microphone button.
- Gemma's window on a test machine: only opening it and one typed question were tested. Not tested: Stop, New chat, a long conversation, closing mid-answer, opening it twice, the window in "Try it first".
- The assistant's lack of network was checked by listing what it can see (only a switched-off loopback device), not by trying to connect out from inside it.
- The quality of Gemma's answers was not assessed, beyond three short answers being sensible.
- That nothing listens on the network once the desktop is up was seen in the two machines started from the image. On the installed system the check still runs before log-in.
- The plain-question installer screens are not built; the installer does not use the probe and rules.
- The probe's test data is the expected profile of the Beelink, not a recording.
- The mandala is not yet in a folder David can open and edit.
- The ArtCraft "Craft" apps have not been looked at.
- If Windows on the Beelink uses BitLocker, David should have his recovery key to hand before first starting from another drive. Claude does not expect it to be asked for, but has not tested it.

---

## 7. Next steps, in order

1. ~~Automated install test.~~ Done 13 November, then redone for option B.
2. ~~Gemma 4.~~ Done 14 November (builds 9 and 10), tested on a machine without AVX.
3. **Office and creative apps.** Next.
4. **The plain-question installer screens**, including the typed confirmation.

Small items to fold in along the way:

- Remove the "debian" logo from the log-in screen; reword the installer's heading; rename the stick's start-up menu.
- Test the Virus Scanner from the menu, the update pop-up, Tor Browser and the app store in a test machine.
- Check Brave's settings.
- Put the mandala and the plain background in a folder the user can open.

Each build now takes about 65 minutes in all (Gemma made the image and the tests bigger).

**When David has the SSD:** he may try "Try it first" on the Beelink at any time; it cannot change the internal disk. Installing onto the SSD is reasonably safe from build 8 on (build 11 is the current one with Gemma), with the SSD being the only thing that can be erased, but Claude would prefer the typed confirmation (step 4) first.

---

## 8. How a build works

1. Claude changes files in the repository and uploads them to GitHub.
2. GitHub's servers build the image inside Debian 13 (about 15 minutes).
3. The servers start the image in two test machines, photograph the screens, and record the self-check.
4. The servers install the image onto an external test drive beside a pretend Windows disk, wipe the firmware's memory, start from the external drive on a machine shaped like the Beelink (no AVX, 16 GB), log in, check it, ask Gemma a question, and confirm the Windows disk is unchanged.
5. Claude views the screenshots, self-checks and build log, and records the result in `TESTING.md`.
6. When a build is ready for David, he downloads the image from the repository's **Actions** page on github.com.

Claude can see the screenshots and logs (on the `test-results` branch), but cannot download the image itself. Claude's workspace can reach GitHub and Google's Gemma repository, so llama.cpp and Gemma can be tried there before a build. Claude can also operate a test machine step by step ("Remote-controlled test machine").

---

## 9. What David will be asked to do

1. **Buy an external SSD:** a known brand (Samsung, Crucial, SanDisk, Kingston) from a known UK retailer, 250 GB or more. Not the "128 TB for £30" kind; those are fakes.
2. **When an image is ready to try:** download it from GitHub (5.7 GB for build 11), write it to the stick with balenaEtcher, and start the Beelink from the stick by tapping the boot key at power-on (usually F7 on a Beelink). Claude will supply a step-by-step guide.
3. **"Try it first":** optional now that Windows is not at risk. The stick always starts a working desktop with the installer as an icon on it; a quick look at the screen, Wi-Fi and sound before the SSD is erased is all it is for. No need to try Gemma there: it loads slowly from the stick.
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

Met on 14 November: 5 (Gemma from Google's repository, checksum enforced, licence shipped). Non-negotiable 4 for the assistant is enforced by starting it without a network.

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

### Session of 14 November 2026 (Gemma)

**Facts corrected.** The N5105 has no AVX at all, not only no AVX2 (Intel lists SSE4.2 as its highest). The Gemma file is 3.35 GB, not "about 3 GB". Debian 13 carries no program that runs Gemma 4.

**Tried in Claude's workspace first.** llama.cpp built; Google's file downloaded and its checksum matched; Gemma answered. With only SSE4.2: 5 tokens a second; with everything: 14 (2 cores). Memory in use: 3.47 GB.

| Build | Result |
| --- | --- |
| 9 | Gemma in the image. Answered on the modern test machine (21.6 tokens a second). Install test and no-AVX test failed: Claude had given those machines 8 GB, where the rules correctly allow no Gemma on a no-AVX processor. |
| 10 | Test machines shaped like the Beelink (no AVX, 16 GB). All tests passed, 0 problems, no build warnings. No-AVX: 5.4 tokens a second from the image, 5.0 from the installed external drive. Gemma window opened from the start menu and answered a typed question. KDE Connect removed. |
| 11 | Gemma's add-on for pictures and recordings, and the two buttons. All tests passed, 0 problems, no build warnings. No-AVX: picture answer began after about 3 minutes, recording after 21 seconds, text 4.7 tokens a second. |

**Afternoon: eyes and ears.** David asked for the add-on if it would not slow Gemma. Measured first: ordinary chat is not slowed. Found on the way: Gemma denied it could hear when the recording was sent before the question; it sometimes misheard a time of day at the normal setting; and it reports a "22" that is not in the test picture.

**Found by testing.** KDE Connect listened on the network and announced the PC once the desktop was up; earlier self-checks ran before the desktop and missed it. After its removal nothing was listening in either machine started from the image.

**Mistakes by Claude this session.** The 8 GB test machines (cost one build, about an hour). Gemma's "cannot run" message at first used the installer's wording ("will install without it"). The first build's saved copies of llama.cpp and the model were thrown away because a later test failed, so build 10 fetched and built them again.

**Interrupted once.** David stopped the first llama.cpp build to say the project had gone back to the Beelink; the N5105 is the Beelink's processor, so nothing changed.

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
| AVX, AVX2 | Processor instructions that make AI models faster. The N5105 has neither. |
| Gemma 4 E2B | The smaller of the two Gemma 4 models considered; 3.35 GB, plus 1 GB for pictures and recordings. |
| llama.cpp | The open-source program that runs Gemma on the PC. |
| Token | A piece of a word. Gemma writes in tokens; 5 tokens a second is roughly 4 words a second. |

---

## 13. Sources checked

Checked on 13 November 2026:

- Celeron J4125 instruction set (SSE4.2 highest): https://www.intel.com/content/www/us/en/products/sku/197305/intel-celeron-processor-j4125-4m-cache-up-to-2-70-ghz/specifications.html
- AWOW 8 GB / 128 GB J4125 model: https://www.galaxus.ch/en/s1/product/awow-mini-pc-win11-pro-celeron-j4125-8gb-ram-128gb-m2-pc-21876616

Checked on 14 November 2026:

- Celeron N5105 instruction set (SSE4.2 highest): https://www.intel.com/content/www/us/en/products/sku/212328/intel-celeron-processor-n5105-4m-cache-up-to-2-90-ghz/specifications.html
- Google's Gemma 4 E2B file, licence and checksum: https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf/tree/main
- llama.cpp releases: https://github.com/ggml-org/llama.cpp/releases

Not re-checked on 14 November: Debian 13 support dates, the ArtCraft apps. The statements about ClamAV's memory use and what it detects are from Claude's general knowledge, not checked against a source today.
