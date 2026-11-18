<h1 align="center">Antikythera</h1>
<p align="center"><a href="../README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <strong>繁體中文</strong></p>
<p align="center"><strong>為 GitHub 個人首頁設計的動態提交日曆。</strong></p>
<p align="center">
  <a href="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml"><img alt="日曆測試" src="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hyyyyyyz/antikythera/releases/latest"><img alt="最新版本" src="https://img.shields.io/github/v/release/hyyyyyyz/antikythera?color=44687a&amp;label=release"></a>
</p>

![固定基座上的 Franka Panda 手持紅色蓋亞狂徒，清空提交方塊後，金色小旗在機械手臂旁升起。](../gallery/assembly-log.svg)

Franka Panda 在固定基座上轉動手腕，依每張日曆特有的順序發出光束，逐一擊中有提交的日期。最後一個方塊熄滅，一面金色小旗從機械手臂旁升起。

Jason 的首頁範例使用紅色原版 **Gaia’s Vengeance Vandal** 的模型算繪圖。通用 Action 預設採用原創光束發射器。[同人美術與作者標示](../gallery/artwork/README.md)

[快速上手](#快速上手) · [使用 GitHub Action](#使用-github-action) · [本機開發](#本機開發)

## 快速上手

1. 在自己的 GitHub 帳號下建立一份公開的 Fork。[建立 Fork](https://github.com/hyyyyyyz/antikythera/fork)
2. 在 Fork 中啟用 Actions，前往 **Actions → Refresh calendar → Run workflow**，在預設分支執行。第一次成功後，就會以你的日曆取代範例動畫。
3. 將下方這行貼到個人首頁的 README，並將 `YOUR-LOGIN` 換成你的 GitHub 使用者名稱。若有更改儲存庫名稱或預設分支，也請一併修改網址。

```markdown
![固定基座上的 Franka Panda 手持紅色蓋亞狂徒，清空提交方塊後，金色小旗在機械手臂旁升起。](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```
Franka Panda 在固定基座上轉動手腕，依每張日曆特有的順序發出光束，逐一擊中有提交的日期。最後一個方塊熄滅，一面金色小旗從機械手臂旁升起。

Jason 的首頁範例使用紅色原版 **Gaia’s Vengeance Vandal** 的模型算繪圖。通用 Action 預設採用原創光束發射器。[同人美術與作者標示](../gallery/artwork/README.md)
內建的工作流程每天於 UTC 03:19 更新 SVG，個人首頁可持續使用同一個圖片網址。[發佈工作流程](../.github/workflows/calendar.yml)

## 使用 GitHub Action

若要在既有儲存庫產生日曆，請在 Ubuntu 作業的 checkout 步驟之後加入以下設定。

```yaml
- uses: hyyyyyyz/antikythera@v1.3.0
  with:
    username: ${{ github.repository_owner }}
    output: assets/first-light.svg
```

這個步驟會將 SVG 寫入作業的工作目錄。接著將檔案發佈到個人首頁 README 引用的分支。讀取提交資料需要讀取權限，透過工作流程提交圖片則需要 `contents: write`。

| 輸入項目 | 預設值 | 用途 |
| --- | --- | --- |
| `username` | 儲存庫擁有者 | 要顯示其公開提交的 GitHub 帳號 |
| `output` | `assembly-log.svg` | 輸出至呼叫端工作目錄的路徑 |
| `compact-output` | 省略 | 選用的第二個輸出路徑，內容為同一張單列日曆 |
| `artwork` | 原創光束發射器 | 選用，呼叫端儲存庫中 SVG 道具插畫的路徑 |
| `token` | `${{ github.token }}` | 讀取 GitHub GraphQL API 的權杖 |

## 如何閱讀日曆

日曆顯示截至 UTC 當天的最近 365 天。每一欄代表一週，由左至右排列，星期日位於最上方。每格統計 GitHub 歸入該使用者個人貢獻的公開儲存庫提交。[GitHub 貢獻統計規則](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

每一輪開始時，空格代表當天沒有提交。被光束清除的格子會在下一輪開始時重新亮起。九階藍色依序代表 **1、2、3、4–5、6–9、10–19、20–39、40–79、80 次以上（含 80 次）**。SVG 會配合淺色或深色主題。系統開啟「減少動態效果」時，會顯示整年日曆與靜止的機械手臂。全年都沒有提交時，場景會維持靜止。

## 本機開發

請使用 Python 3.9 以上版本，並以 `gh auth login` 或 `GH_TOKEN` 登入 GitHub CLI。日常產生日曆只需要 Python 標準函式庫。

```sh
python3 assembly.py --username YOUR-LOGIN --output first-light.svg
python3 -m unittest discover -s tests -v
```

機械手臂、夾爪與基座以同一台正交攝影機預先算繪。手持道具、光束與旗幟也封裝於同一張 SVG 中，嵌入 README 即可播放。[美術流程與自訂道具](../art/README.md)

## 授權

程式碼、基座與預設道具採用 MIT 授權，Franka Panda 模型採用 Apache-2.0 授權。範例中的《特戰英豪》同人美術另有來源與使用條款。[MIT 授權條款](../LICENSE) · [Panda 模型來源](../third_party/panda/README.md) · [範例美術](../gallery/artwork/README.md)
