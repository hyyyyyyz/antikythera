<h1 align="center">Antikythera</h1>
<p align="center"><strong>English</strong> &nbsp;·&nbsp; <a href="docs/README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="docs/README.zh-TW.md">繁體中文</a></p>
<p align="center"><strong>An animated commit calendar for your GitHub profile.</strong></p>
<p align="center">
  <a href="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml"><img alt="Calendar tests" src="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hyyyyyyz/antikythera/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/hyyyyyyz/antikythera?color=44687a&amp;label=release"></a>
</p>

![A Franka Panda holds Gaia’s Vengeance on a fixed pedestal and a gold pennant rises beside the cleared calendar.](gallery/assembly-log.svg)

A Franka Panda turns on its pedestal and sends a pulse through each active date, in a different order for each calendar. Watch the last square go dark and a gold pennant rise beside the arm.

Jason’s profile edition features a rendering of the red **Gaia’s Vengeance Vandal**. The reusable Action ships with an original studio light. [Fan artwork and credits](gallery/artwork/README.md)

[Quick start](#quick-start) · [GitHub Action](#github-action) · [Local development](#local-development)

## Quick start

1. Create a public fork under your GitHub account. [Fork Antikythera](https://github.com/hyyyyyyz/antikythera/fork)
2. In your fork, enable Actions. Open **Actions → Refresh calendar → Run workflow** on the default branch. The first successful run replaces the example with your calendar.
3. Paste this line into your profile README. Replace `YOUR-LOGIN` with your username. If you renamed the fork or its default branch, adjust the URL too.

```markdown
![A Franka Panda holds Gaia’s Vengeance on a fixed pedestal and a gold pennant rises beside the cleared calendar.](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```
A Franka Panda turns on its pedestal and sends a pulse through each active date, in a different order for each calendar. Watch the last square go dark and a gold pennant rise beside the arm.

Jason’s profile edition features a rendering of the red **Gaia’s Vengeance Vandal**. The reusable Action ships with an original studio light. [Fan artwork and credits](gallery/artwork/README.md)
The included workflow refreshes the SVG daily at 03:19 UTC. Your profile keeps the same image URL. [Publishing workflow](.github/workflows/calendar.yml)

## GitHub Action

To generate the calendar in an existing repository, add this step after checkout in an Ubuntu job.

```yaml
- uses: hyyyyyyz/antikythera@v1.3.0
  with:
    username: ${{ github.repository_owner }}
    output: assets/first-light.svg
```

The step writes the SVG to the job's workspace. Publish that file on the branch your README uses. Reading contributions requires read access. Committing the image from a workflow also requires `contents: write`.

| Input | Default | Purpose |
| --- | --- | --- |
| `username` | Repository owner | GitHub account whose public commits appear |
| `output` | `assembly-log.svg` | File path in the caller's workspace |
| `compact-output` | Omitted | Optional second path for the same single-strip image |
| `artwork` | Studio light | Optional path to a flat SVG illustration in the caller repository |
| `token` | `${{ github.token }}` | Token used to read GitHub's GraphQL API |

## Reading the calendar

The board covers 365 days ending today in UTC. Weeks run left to right, with Sunday at the top. Each tile counts commits GitHub credits to that user in public repositories. [GitHub's contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

At the start of a round, an empty socket means zero commits. Dates cleared during play light up again when the next round begins. Nine shades of blue mark **1, 2, 3, 4–5, 6–9, 10–19, 20–39, 40–79 and 80+**. The SVG adapts to light and dark themes. Visitors who prefer reduced motion see the entire year and the arm at rest. An empty year stays idle.

## Local development

Use Python 3.9 or later and an authenticated GitHub CLI (`gh auth login` or `GH_TOKEN`). The daily renderer uses the Python standard library.

```sh
python3 assembly.py --username YOUR-LOGIN --output first-light.svg
python3 -m unittest discover -s tests -v
```

The model, gripper and fixed base are rendered together in an orthographic studio. The resulting SVG also contains the wrist illustration, pulses and flag, so the entire animation plays as a single README image. [Art pipeline and custom artwork](art/README.md)

## License

The code, pedestal and default studio light use the MIT license. The Franka Panda geometry uses Apache-2.0. The gallery’s VALORANT fan art has separate credits and terms. [MIT license](LICENSE) · [Panda attribution](third_party/panda/README.md) · [Gallery artwork](gallery/artwork/README.md)
