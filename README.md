# Antikythera

A robotic arm assembles your GitHub commit calendar. Each socket is one day, each chip is a day with public commits, and the arm places the chip for your most recent active day. The arm makes one pass and parks. Visitors who prefer reduced motion see the finished board immediately.

<picture>
  <source media="(max-width: 600px)" srcset="./gallery/assembly-log-compact.svg">
  <img src="./gallery/assembly-log.svg" alt="Live assembly calendar for hyyyyyyz" width="100%">
</picture>

[Open the compact calendar](./gallery/assembly-log-compact.svg)

## Put it on your profile

Fork this repository, enable GitHub Actions, and run **Refresh calendar** once from the Actions tab. The workflow reads the fork owner's public commit contributions and writes a wide and a compact SVG under `gallery/`. It refreshes daily at 03:19 UTC. The first run replaces the upstream example included in your fork.

Add the following to your profile README, replacing `YOUR-LOGIN` with your GitHub login. If you rename the fork, also update the repository name in the URL.

```html
<picture>
  <source media="(max-width: 600px)" srcset="https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log-compact.svg">
  <img src="https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg" width="100%" alt="My commit assembly calendar">
</picture>
```

## Use the Action in another repository

After checking out your repository, run the action in an Ubuntu job. The generated SVG is a local file in the caller's workspace. Commit it to the branch your README references, or publish it alongside your other generated assets.

```yaml
- uses: hyyyyyyz/antikythera@v1.0.0
  with:
    username: ${{ github.repository_owner }}
    output: assets/assembly-log.svg
    compact-output: assets/assembly-log-compact.svg
```

| Input | Default | Purpose |
| --- | --- | --- |
| `username` | Repository owner | GitHub user to draw |
| `output` | `assembly-log.svg` | Destination file |
| `compact-output` | Omitted | Optional portrait SVG with two bands of weeks |
| `token` | Workflow token | Authentication for GitHub GraphQL |

The rendering step works with read access. The included publishing workflow also needs permission to commit to the default branch. See the [working workflow](.github/workflows/calendar.yml).

## Reading the board

Weeks run left to right, with Sunday at the top. The board covers 365 days ending on the current UTC date. An empty socket means zero commits. Nine chip colors mark **1, 2, 3, 4–5, 6–9, 10–19, 20–39, 40–79, and 80+**. Blue and violet distinguish quieter days. Coral, copper, and gold mark the busiest days. An empty year leaves the arm parked.

Counts come from the daily `commitCount` records in GitHub's GraphQL contribution collection. Only public repositories are included. GitHub applies its profile contribution and attribution rules, so this measures commits credited on your profile. Issues, reviews, and pull requests are separate contribution types. [GitHub's contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

## Run locally

Use Python 3.9 or later and the authenticated GitHub CLI. Rendering uses only the Python standard library. Authentication can come from `gh auth login` or the `GH_TOKEN` environment variable.

```sh
python3 assembly.py --username YOUR-LOGIN --output assembly-log.svg
python3 -m unittest discover -s tests -v
```

The renderer completes the data request before replacing the output. Over-capacity queries are retried with smaller date windows. An incomplete single day stops the refresh and preserves the previous image.

[MIT license](LICENSE)
