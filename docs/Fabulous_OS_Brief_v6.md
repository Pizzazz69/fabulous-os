# Fabulous OS: Brief, version 6

**A Linux system with an offline AI assistant (Gemma 4), run from an external drive beside an untouched Windows PC**

Prepared for David, 14 November 2026 (night), after build 12. This replaces brief version 5 of the same day. Where the two disagree, this one wins. It is written so that a new Claude session can finish the project from it.

---

## 1. How to use this brief

**For David.** Section 2 is where things stand. Section 9 is your step-by-step guide for trying build 12 on the Beelink; you can follow it without Claude. Section 7 is what remains.

**For Claude, in any later session.** You do not remember the earlier sessions. Do this, in order:

1. Read this brief, then `DECISIONS.md` and `TESTING.md` in the repository `Pizzazz69/fabulous-os`.
2. Read section 8 ("How a build works" and "Working notes for Claude"). It tells you how to see test results and what has already gone wrong, so you do not repeat it.
3. Ask David what happened when he tried build 12 on the Beelink (section 9). **His report from the real PC outranks everything in this brief**, which rests on test machines only. Fix what he found before adding anything new.
4. Then work through section 7 in order.
5. After each step tell David plainly what was tested, how, and what was not (non-negotiable 9). Record it in `TESTING.md` and `DECISIONS.md`, and update this brief under a new version number at the end of the session.

David is not a programmer. Write to him in plain words, explain any term you must use, and never ask him to type commands unless there is no other way. He holds truth to be important: say what you do not know.

---

## 2. Where things stand

| | |
| --- | --- |
| Project home | GitHub repository `Pizzazz69/fabulous-os` (public) |
| Latest image | Build 12, 5.7 GB (was 2.5 GB before Gemma), built on GitHub's servers |
| Plan ("option B") | Fabulous OS lives on an **external USB SSD**. The Beelink's internal disk and Windows are never changed. To go back: unplug the drive. |
| Installer | Tested automatically: installs onto an external drive, which then starts by itself under Secure Boot. The internal disk was byte-for-byte unchanged. |
| Protection | Every internal disk is read-only, both when started from the stick and (from build 12) on the installed system; the installer offers only external drives. |
| Firewall, virus scanner, Secure Boot | Checked from inside the installed system. |
| Tested on the Beelink | Not yet. Nothing has run on any real PC. |
| External SSD | Netac Portable SSD, 500 GB, USB 3.2; expected 14 November evening. |
| Stick | New 128 GB SD card in an SD-to-USB reader, ready. |
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
| Internal disks on the installed system | Read-only at every start, as in the stick session. Windows' disk can be looked at, not changed. | David's decision, 14 November evening. |
| KDE Connect | Removed. | It listened on the network and announced the PC as soon as the desktop started, unasked. Can be reinstalled from the App Store. David may reverse this. |

---

## 5. What exists today

**In the repository:** `build/` (the recipe), `models.lock` (which Gemma file, and its checksum), `packages/fabulous-gemma/` (the assistant and its window), `packages/fabulous-probe/` (reads a PC's hardware), `rules/` (chooses the Gemma model and app set), `tests/` (drives the test machines; the install test), `.github/workflows/` (build, test, publish screenshots), `DECISIONS.md`, `TESTING.md`, `docs/` (this brief).

**In the image (build 12):**

- Desktop: name, mandala, centred taskbar, Brave, Tor Browser launcher, app store with Flathub.
- Debian's installer, renamed, with mandala pictures, starting in London, asking before it erases, putting start-up files where an external drive needs them.
- Internal disks read-only, in the stick session and on the installed system.
- Firewall (ufw), on. ClamAV, its window, and the fetch-signatures-when-opened service.
- Gemma 4 E2B with its add-on for pictures and recordings, the program that runs it, the chat window, and their licences.
- The probe and rules programs (not yet used by the installer; the Gemma window does use the rules), and the self-check.

**Tests that pass (build 12):** 41 automated tests of the probe, rules and assistant; image build with no warnings; start to the desktop in both test machines; Gemma answering, describing a test picture and writing down a test recording in three test machines; the automated install test for option B, now ending with a question typed into the Gemma window; the self-checks listed in `TESTING.md`.

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

Done: the automated install test (13 November); Gemma 4 with pictures and recordings (14 November, builds 9 to 11); internal disks read-only on the installed system (build 12).

**Step A. David tries build 12 on the Beelink** (section 9). This is the first run on real hardware. Claude: ask for his report and fix what it shows first. Things to ask him: did the stick start; screen, Wi-Fi, sound; did the installer offer only the SSD; did the SSD start from the F7 menu; how long Gemma takes to load and to answer on the real N5105; does Windows still start normally with the SSD unplugged.

**Step B. Typed confirmation before erasing** (non-negotiable 3, not yet met). The installer (Calamares) asks only yes/no today. Add a screen where the person must type a word (for example ERASE) before the external drive is erased. Extend `tests/install-test.sh` to type it, and add a check that a wrong word does not start the install.

**Step C. Office and creative apps.** LibreOffice (Writer, Calc, Impress) from Debian 13. David also listed creative apps on 12 November; see `DECISIONS.md`, and the ArtCraft "Craft" apps have still not been looked at. Non-negotiable 6: every app shipped must be opened in a test machine, with a screenshot. Add each to the install test the way Brave and Gemma were added.

**Step D. Gemma reads documents** (David's wish, 14 November; not started, not tested). David hoped Gemma could read and edit .docx files, spreadsheets and slides and work unaided on long tasks. Claude told him that unaided long work is not realistic for this small model on this PC, and that a realistic version is:

- an "Add a document…" button in the Gemma window that hands Gemma the text of a .docx, .odt, spreadsheet or slides file (LibreOffice can convert these to text without opening a window);
- for a long document, a small program (not Gemma) that cuts it into sections, gives Gemma one section at a time, and collects the results. This suits summarising, proofreading, plainer wording and translating; it does not suit tasks that need the whole document in mind;
- results saved as a **new** file; the original is never changed.

Try it in the workspace first on a real multi-page .docx and show David the results and timings before building it in. Expect roughly an hour per 10,000 words rewritten on the test machines, and more on the Beelink.

**Step E. The plain-question installer screens**, using the probe and rules (the installer does not use them yet).

**Small items**, to fold in along the way:

- Remove the "debian" logo from the log-in screen; reword the installer's heading ("Calamares installer"); rename the stick's start-up menu ("Debian GNU/Linux").
- Test in a test machine: the Virus Scanner from the menu, the update pop-up, Tor Browser, the app store.
- Test in a test machine: Gemma's Stop and New chat buttons; "Add a picture…" and "Add a recording…" with a real file chosen; opening the Windows disk in the file manager on the installed system (it should be readable and not writable).
- Check Brave's settings.
- Put the mandala and the plain background in a folder the user can open.
- Delete the scratch branches `vm-control` and `vm-screen`.
- Optional, if David wants faster picture answers: reduced picture detail (`--image-max-tokens 140`) cut the wait from about 145 to about 80 seconds in the workspace, at some cost to reading small writing.

Each build takes about 65 minutes. Finishing all of this is more than one day's work; steps A, B and C matter most.

---

## 8. How a build works

1. Claude changes files in the repository and uploads them to GitHub.
2. GitHub's servers build the image inside Debian 13 (about 15 minutes).
3. The servers start the image in two test machines, photograph the screens, and record the self-check.
4. The servers install the image onto an external test drive beside a pretend Windows disk, wipe the firmware's memory, start from the external drive on a machine shaped like the Beelink (no AVX, 16 GB), log in, check it, ask Gemma a question, and confirm the Windows disk is unchanged.
5. Claude views the screenshots, self-checks and build log, and records the result in `TESTING.md`.
6. When a build is ready for David, he downloads the image from the repository's **Actions** page on github.com.

Claude can see the screenshots and logs (on the `test-results` branch), but cannot download the image itself. Claude's workspace can reach GitHub and Google's Gemma repository, so llama.cpp and Gemma can be tried there before a build. Claude can also operate a test machine step by step ("Remote-controlled test machine").

### Working notes for Claude

- **Starting a build.** Any push to `main` starts a full build and test (about 65 minutes). Put `[skip ci]` in the commit message for changes to documents only. Earlier sessions pushed straight to `main`; David expects that.
- **Watching a build.** `gh run list -R Pizzazz69/fabulous-os`, then `gh run view <id> -R Pizzazz69/fabulous-os --json status,conclusion,jobs`. The full log, once the run has finished: `gh run view <id> --log`. Look in it for `FABULOUS-WARNING` (the build prints "=== warnings ===" and then "none" when there are none).
- **Seeing the results.** Artifact downloads are blocked from Claude's workspace. Instead, a second workflow publishes the screenshots and self-check texts to the `test-results` branch about a minute after each run: `git fetch --depth 1 origin test-results`, then check the files out into a separate folder. Read `shots/gemma-result.txt` and `shots/install-result.txt` (both must end "problems: 0") and the three `*-selfcheck.txt` files, and look at the `install-*.png` screenshots yourself.
- **Trying Gemma without a build.** The workspace can reach GitHub and huggingface.co. Build llama.cpp at the commit in `build/llama.lock` with the options in `build/build-llama.sh`, fetch the model files with `build/fetch-models.sh`, then run `packages/fabulous-gemma/fabulous_gemma.py` with `FABULOUS_GEMMA_PREFIX`, `FABULOUS_GEMMA_MODELS` and `FABULOUS_RULES_DIR` set. `--ask "question" [--picture FILE] [--recording FILE]` answers on the terminal. With `QT_QPA_PLATFORM=offscreen`, `--demo "question" --screenshot out.png` runs the real window and saves a picture of it. To imitate the Beelink's processor, keep only `libggml-cpu-sse42.so` of the `libggml-cpu-*.so` files.
- **Unit tests.** `python3 -m pytest -q packages rules` (41 tests).
- **The rules decide who gets Gemma** (`rules/rules.yaml`): a processor without AVX2 needs 12 GB or more. A no-AVX test machine with 8 GB is correctly refused, so give such machines 16 GB (build 9 was wasted on this).
- **Gemma and attachments.** The question must be sent before the picture or recording, or Gemma denies it can hear. Sampling is made less inventive when something is attached. Both are in `fabulous_gemma.py`; do not undo them without re-testing.
- **Disk safety.** `fabulous-protect-internal` makes internal disks read-only in the stick session and on the installed system. Never weaken it without David's say-so. The install test must keep proving the internal disk is byte-for-byte unchanged.
- **The image expires.** GitHub keeps each build's image for 14 days (build 12: until about 28 November 2026). If David needs it after that, start a new build.
- **David's time with Claude is limited.** Check on builds sparingly and keep messages short.

---

## 9. David's guide: trying build 12 on the Beelink

You have: the Beelink with Windows; the 128 GB SD card in its USB reader (the "stick"); the Netac 500 GB external SSD. Nothing below can change the Beelink's internal disk: Fabulous OS makes it read-only. None of this has been tried on a real PC yet, so if anything differs from what is written here, stop and tell Claude.

**1. Download the image (on Windows).**
Sign in to github.com, open `github.com/Pizzazz69/fabulous-os`, click **Actions**, then the run named "Installed system: internal disks read-only at every start" with a green tick. At the bottom of that page, under **Artifacts**, click **fabulous-os-image**. A zip file of about 5.7 GB downloads. Open it and copy out the file ending `.iso`. (Available until about 28 November; after that, ask Claude for a new build.)

**2. Write it to the stick.**
Install balenaEtcher (etcher.balena.io). Plug in the SD-card stick. In Etcher: "Flash from file" and pick the `.iso`; "Select target" and pick the SD card (check the size, about 128 GB, so that you do not pick the SSD); then "Flash". This erases the SD card. If Windows afterwards says the card "needs to be formatted", say **No**.

**3. Start the Beelink from the stick.**
If Windows uses BitLocker, have your recovery key to hand first (Claude does not expect it to be asked for, but has not tested it). Shut Windows down. Plug in the stick. Switch on and tap **F7** repeatedly until a menu of drives appears; choose the stick. A menu headed "Debian GNU/Linux" appears: press Enter. The Fabulous OS desktop should appear within a couple of minutes. Do not switch Secure Boot off; if the PC refuses to start the stick, stop and tell Claude.

**4. Look around (optional, two minutes).**
Does the screen look right? Does Wi-Fi connect? Is there sound? There is no need to try Gemma here: from the stick she takes about five minutes to load.

**5. Install onto the SSD.**
Plug in the Netac SSD. Double-click **Install Fabulous OS** on the desktop. When asked where to install, the SSD should be the only drive offered (about 500 GB). **If the internal disk (477 GB) is ever offered, stop and tell Claude.** The installer asks yes or no before erasing the SSD; there is no typed confirmation yet. Choose a user name and password and remember them. In the test machines the install took under 12 minutes.

**6. Start Fabulous OS from the SSD.**
When it finishes, shut down, remove the stick, leave the SSD plugged in, switch on and tap **F7**; choose the SSD. Log in.

**7. Try Gemma.**
Click the speech-bubble icon on the taskbar. Wait for "Ready." and ask a short question. Please note roughly how long she takes to load and to answer; these will be the first real measurements.

**8. Back to Windows.**
Shut down, unplug the SSD, switch on. Windows should start exactly as before. If Windows ever offers to format the SSD, say **No**.

**What to tell Claude afterwards:** anything that did not match the above; whether Wi-Fi and sound worked; Gemma's loading and answering times; whether Windows started normally.

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
| 12 | The installed system also makes internal disks read-only. All tests passed, 0 problems. |

**Afternoon: eyes and ears.** David asked for the add-on if it would not slow Gemma. Measured first: ordinary chat is not slowed. Found on the way: Gemma denied it could hear when the recording was sent before the question; it sometimes misheard a time of day at the normal setting; and it reports a "22" that is not in the test picture.

**Evening.** David asked where files are kept; Claude found that the installed system, unlike the stick session, did not protect the Windows disk, and David asked for it to be protected (build 12). Not tested there: opening the Windows disk in the file manager; a real USB stick (the test stick is a virtual CD drive).

**Found by testing.** KDE Connect listened on the network and announced the PC once the desktop was up; earlier self-checks ran before the desktop and missed it. After its removal nothing was listening in either machine started from the image.

**Told to David about Gemma's limits (14 November).** She is a chat window: she cannot open files, operate LibreOffice or act on the computer, and long unaided work is not realistic for this model on this PC. David asked whether dividing a long document into sections would work; Claude said yes for section-by-section tasks, untested (section 7, step D).

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
