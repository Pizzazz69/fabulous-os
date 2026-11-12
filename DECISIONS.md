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
