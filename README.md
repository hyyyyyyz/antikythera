# Antikythera

A white collaborative arm places a single blue chip on your latest day of public commits. One year fits in a single strip on desktop and mobile. The SVG has a transparent background, adapts to dark or light mode, and shows the finished board immediately when reduced motion is enabled.

![Live commit calendar](gallery/assembly-log.svg)

## Put it on your profile

Fork this repository, enable GitHub Actions, and run **Refresh calendar** once from the Actions tab. The workflow reads the fork owner's public commit contributions and writes `gallery/assembly-log.svg`. It refreshes daily at 03:19 UTC. The first run replaces the upstream example included in your fork.

Add the following to your profile README, replacing `YOUR-LOGIN` with your GitHub login. If you rename the fork, also update the repository name in the URL.

```markdown
![My commit calendar](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```

## Use the Action in another repository

After checking out your repository, run the action in an Ubuntu job. The generated SVG is a local file in the caller's workspace. Commit it to the branch your README references, or publish it alongside your other generated assets.

```yaml
- uses: hyyyyyyz/antikythera@v1.0.0
  with:
    username: ${{ github.repository_owner }}
    output: assets/assembly-log.svg
```

| Input | Default | Purpose |
| --- | --- | --- |
| `username` | Repository owner | GitHub user to draw |
| `output` | `assembly-log.svg` | Destination file |
| `compact-output` | Omitted | Optional second path for the same single-strip SVG |
| `token` | Workflow token | Authentication for GitHub GraphQL |

The rendering step works with read access. The included publishing workflow also needs permission to commit to the default branch. See the [working workflow](.github/workflows/calendar.yml).

## Reading the board

Weeks run left to right, with Sunday at the top. The board covers 365 days ending on the current UTC date. The palest squares in light mode and the darkest squares in dark mode mark zero commits. Nine shades of blue distinguish **1, 2, 3, 4–5, 6–9, 10–19, 20–39, 40–79, and 80+**. Darker blues in light mode and lighter blues in dark mode indicate more commits. An empty year leaves the arm parked.

Counts come from the daily `commitCount` records in GitHub's GraphQL contribution collection. Only public repositories are included. GitHub applies its profile contribution and attribution rules, so this measures commits credited on your profile. Issues, reviews, and pull requests are separate contribution types. [GitHub's contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

## Run locally

Use Python 3.9 or later and the authenticated GitHub CLI. Rendering uses only the Python standard library. Authentication can come from `gh auth login` or the `GH_TOKEN` environment variable.

```sh
python3 assembly.py --username YOUR-LOGIN --output assembly-log.svg
python3 -m unittest discover -s tests -v
```

The renderer completes the data request before replacing the output. Over-capacity queries are retried with smaller date windows. An incomplete single day stops the refresh and preserves the previous image.

[MIT license](LICENSE)
