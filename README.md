# Fabulous OS

A Linux system based on Debian 13, with an offline AI assistant (Gemma 4), delivered as a USB stick image.

Status: early development. Nothing here has been installed on real hardware yet. See `TESTING.md`.

- `build/` — image recipe (Debian live-build)
- `packages/fabulous-probe/` — reads the computer's hardware, changes nothing
- `rules/` — chooses the Gemma model and app set from the hardware profile
- `tests/` — tools that drive the build servers' test machines
- `DECISIONS.md` — what was decided and why
- `.github/workflows/build.yml` — builds the image and test-starts it

Run the tests: `python3 -m pytest -q packages rules`

Fabulous OS is based on Debian but is not affiliated with or endorsed by the Debian Project.
