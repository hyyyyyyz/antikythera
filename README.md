<h1 align="center">Antikythera</h1>
<p align="center"><strong>English</strong> &nbsp;·&nbsp; <a href="docs/README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="docs/README.zh-TW.md">繁體中文</a></p>
<p align="center"><strong>A year of GitHub commits, played as a single-arm arcade game.</strong></p>
<p align="center">
  <a href="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml"><img alt="Calendar tests" src="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hyyyyyyz/antikythera/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/hyyyyyyz/antikythera?color=44687a&amp;label=release"></a>
</p>

![A Franka Panda clears commit tiles from its yellow shuttle. A lunar antenna transmits and a victory flag rises.](gallery/assembly-log.svg)

In **First Light**, a Franka Panda rides beneath your calendar and clears active dates with bursts of light. Each date goes dark on impact. After the last tile, a lunar antenna unfolds, sends its first signal and raises a gold victory pennant.

[Quick start](#quick-start) · [GitHub Action](#github-action) · [Local development](#local-development)

## Quick start

1. Create a public fork under your GitHub account. [Fork Antikythera](https://github.com/hyyyyyyz/antikythera/fork)
2. In your fork, enable Actions. Open **Actions → Refresh calendar → Run workflow** on the default branch. The first successful run replaces the example with your calendar.
3. Paste this line into your profile README. Replace `YOUR-LOGIN` with your username. If you renamed the fork or its default branch, adjust the URL too.

```markdown
![My commit calendar](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```

The included workflow refreshes the SVG daily at 03:19 UTC. Your profile keeps the same image URL. [Publishing workflow](.github/workflows/calendar.yml)

## GitHub Action

To generate the calendar in an existing repository, add this step after checkout in an Ubuntu job.

```yaml
- uses: hyyyyyyz/antikythera@v1.2.0
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
| `token` | `${{ github.token }}` | Token used to read GitHub's GraphQL API |

## Reading the calendar

The board covers 365 days ending today in UTC. Weeks run left to right, with Sunday at the top. Each tile counts commits GitHub credits to that user in public repositories. [GitHub's contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

At the start of a round, an empty socket means zero commits. Dates cleared during play light up again when the next round begins. Nine shades of blue mark **1, 2, 3, 4–5, 6–9, 10–19, 20–39, 40–79 and 80+**. The SVG adapts to light and dark themes. Visitors who prefer reduced motion see the full calendar and a parked shuttle. An empty year stays idle.

## Local development

Use Python 3.9 or later and an authenticated GitHub CLI (`gh auth login` or `GH_TOKEN`). The daily renderer uses the Python standard library.

```sh
python3 assembly.py --username YOUR-LOGIN --output first-light.svg
python3 -m unittest discover -s tests -v
```

The arm's 3D poses are baked in MuJoCo. The shuttle, light pulses, folding reflector and pennant play inside the SVG. [Art pipeline](art/README.md)

## License

The code and original artwork use the MIT license. The Franka Panda geometry uses Apache-2.0. [MIT license](LICENSE) · [Model source and attribution](third_party/panda/README.md)
