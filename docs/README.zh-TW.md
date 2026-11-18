<h1 align="center">Antikythera</h1>
<p align="center"><a href="../README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <strong>繁體中文</strong></p>
<p align="center"><strong>把一整年的 GitHub 提交紀錄變成機械手臂的街機關卡。</strong></p>
<p align="center">
  <a href="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml"><img alt="日曆測試" src="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hyyyyyyz/antikythera/releases/latest"><img alt="最新版本" src="https://img.shields.io/github/v/release/hyyyyyyz/antikythera?color=44687a&amp;label=release"></a>
</p>

![Franka Panda 搭著黃色小車，以光束清除提交方塊。月面天線發出訊號後，勝利旗隨之升起。](../gallery/assembly-log.svg)

在《第一束訊號》（First Light）裡，Franka Panda 沿著日曆下方的道路前進，用光束逐一擊中有提交的日期。每命中一格，那一天就會暗下來。最後一格清空後，月面天線展開，送出第一束訊號，再升起金色的勝利旗。

[快速上手](#快速上手) · [使用 GitHub Action](#使用-github-action) · [本機開發](#本機開發)

## 快速上手

1. 在自己的 GitHub 帳號下建立一份公開的 Fork。[建立 Fork](https://github.com/hyyyyyyz/antikythera/fork)
2. 在 Fork 中啟用 Actions，前往 **Actions → Refresh calendar → Run workflow**，在預設分支執行。第一次成功後，就會以你的日曆取代範例動畫。
3. 將下方這行貼到個人首頁的 README，並將 `YOUR-LOGIN` 換成你的 GitHub 使用者名稱。若有更改儲存庫名稱或預設分支，也請一併修改網址。

```markdown
![我的提交日曆](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```

內建的工作流程每天於 UTC 03:19 更新 SVG，個人首頁可持續使用同一個圖片網址。[發佈工作流程](../.github/workflows/calendar.yml)

## 使用 GitHub Action

若要在既有儲存庫產生日曆，請在 Ubuntu 作業的 checkout 步驟之後加入以下設定。

```yaml
- uses: hyyyyyyz/antikythera@v1.2.0
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
| `token` | `${{ github.token }}` | 讀取 GitHub GraphQL API 的權杖 |

## 如何閱讀日曆

日曆顯示截至 UTC 當天的最近 365 天。每一欄代表一週，由左至右排列，星期日位於最上方。每格統計 GitHub 歸入該使用者個人貢獻的公開儲存庫提交。[GitHub 貢獻統計規則](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

空格代表當天沒有提交。九階藍色依序代表 **1、2、3、4–5、6–9、10–19、20–39、40–79、80 次以上（含 80 次）**。SVG 會配合淺色或深色主題。系統開啟「減少動態效果」時，會顯示完整日曆和停靠的小車。全年都沒有提交時，場景會維持靜止。

## 本機開發

請使用 Python 3.9 以上版本，並以 `gh auth login` 或 `GH_TOKEN` 登入 GitHub CLI。日常產生日曆只需要 Python 標準函式庫。

```sh
python3 assembly.py --username YOUR-LOGIN --output first-light.svg
python3 -m unittest discover -s tests -v
```

機械手臂的三維姿態由 MuJoCo 預先算繪，小車、光束、折疊天線與旗幟的動畫都在 SVG 內播放。[美術素材製作流程](../art/README.md)

## 授權

程式碼與原創美術採用 MIT 授權，Franka Panda 模型採用 Apache-2.0 授權。[MIT 授權條款](../LICENSE) · [模型來源與作者標示](../third_party/panda/README.md)
