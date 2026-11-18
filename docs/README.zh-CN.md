<h1 align="center">Antikythera</h1>
<p align="center"><a href="../README.md">English</a> &nbsp;·&nbsp; <strong>简体中文</strong> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a></p>
<p align="center"><strong>把一年的 GitHub 提交记录变成机械臂的街机关卡。</strong></p>
<p align="center">
  <a href="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml"><img alt="日历测试" src="https://github.com/hyyyyyyz/antikythera/actions/workflows/check.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hyyyyyyz/antikythera/releases/latest"><img alt="最新版本" src="https://img.shields.io/github/v/release/hyyyyyyz/antikythera?color=44687a&amp;label=release"></a>
</p>

![Franka Panda 乘着黄色小车，用光束逐一清除提交方块。月面天线发出信号，胜利旗随后升起。](../gallery/assembly-log.svg)

在《第一束信号》（First Light）里，Franka Panda 沿日历下方的公路行驶，用光束点射有提交的日期。每命中一次，对应的格子就暗下去。最后一格清空，月面天线展开并发出第一束信号，一面金色胜利旗随之升起。

[快速开始](#快速开始) · [GitHub Action 用法](#github-action-用法) · [本地开发](#本地开发)

## 快速开始

1. 在自己的 GitHub 账号下创建一个公开的 Fork。[创建 Fork](https://github.com/hyyyyyyz/antikythera/fork)
2. 在 Fork 中启用 Actions，打开 **Actions → Refresh calendar → Run workflow**，在默认分支上运行。首次成功后，示例动画就会换成你的日历。
3. 把下面这行粘贴到个人主页的 README，将 `YOUR-LOGIN` 换成你的 GitHub 用户名。如果改过仓库名或默认分支名，也请更新链接中的对应部分。

```markdown
![我的提交日历](https://raw.githubusercontent.com/YOUR-LOGIN/antikythera/main/gallery/assembly-log.svg)
```

自带的工作流每天在 UTC 03:19 刷新 SVG，主页可以一直使用同一个图片地址。[发布工作流](../.github/workflows/calendar.yml)

## GitHub Action 用法

要在已有仓库中生成日历，在 Ubuntu 作业的 checkout 步骤后添加下面这段配置。

```yaml
- uses: hyyyyyyz/antikythera@v1.2.0
  with:
    username: ${{ github.repository_owner }}
    output: assets/first-light.svg
```

这一步会把 SVG 写入作业的工作目录。将文件发布到主页 README 引用的分支即可。读取提交数据需要读权限，通过工作流提交图片还需要 `contents: write`。

| 输入项 | 默认值 | 用途 |
| --- | --- | --- |
| `username` | 仓库所有者 | 要展示其公开提交的 GitHub 账号 |
| `output` | `assembly-log.svg` | 输出到调用方工作目录的路径 |
| `compact-output` | 省略 | 可选的第二个输出路径，内容为同一张单排日历 |
| `token` | `${{ github.token }}` | 用于读取 GitHub GraphQL API 的令牌 |

## 如何读这张日历

日历展示截至 UTC 当天的最近 365 天。每列是一周，从左向右排列，星期日在最上方。每格统计 GitHub 计入该用户个人贡献的公开仓库提交。[GitHub 贡献统计规则](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)

空格表示当天没有提交。九档蓝色分别对应 **1、2、3、4–5、6–9、10–19、20–39、40–79、80 次及以上**。SVG 会适配浅色和深色主题。系统开启“减少动态效果”时，会显示完整日历和停靠的小车。全年没有提交时，场景保持静止。

## 本地开发

使用 Python 3.9 或更高版本，并通过 `gh auth login` 或 `GH_TOKEN` 登录 GitHub CLI。日常生成日历只用到 Python 标准库。

```sh
python3 assembly.py --username YOUR-LOGIN --output first-light.svg
python3 -m unittest discover -s tests -v
```

机械臂的三维姿态由 MuJoCo 预先渲染。小车、光束、折叠天线与旗帜都在 SVG 内播放。[美术素材生成流程](../art/README.md)

## 许可证

代码与原创美术采用 MIT 许可证，Franka Panda 模型采用 Apache-2.0 许可证。[MIT 许可证](../LICENSE) · [模型来源与署名](../third_party/panda/README.md)
