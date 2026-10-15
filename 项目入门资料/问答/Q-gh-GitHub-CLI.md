# Q：`gh`（GitHub CLI）是什么？

## 一句话
在终端里操作 GitHub（建仓、登录、看 Actions、设 Secrets），不是替代 `git`，也不是跑 CI 的必需品。

## 安装（Windows）
```powershell
winget install --id GitHub.cli
```
装完**新开终端**，再：
```powershell
gh --version
gh auth login
```

## 常见用途
| 事 | 示例 |
|----|------|
| 本地项目一键变私有仓并推送 | `gh repo create <名> --private --source=. --remote=origin --push` |
| 打开仓库网页 | `gh repo view --web` |
| 手动跑 workflow | `gh workflow run <文件名>` |
| 看运行记录 | `gh run list` |
| 设 Secret | `gh secret set NAME` |

改代码、提交仍用：`git add` / `commit` / `push`。

## 有 gh vs 没有 gh
| | 有 gh | 没有 gh |
|--|-------|---------|
| 新建远程仓 | 一条命令 | 网页 New → `git remote add` → `push` |
| 鉴权 | `gh auth login` | HTTPS 凭据或 SSH |
| Actions / Secrets | 终端或网页 | 主要靠网页 |
| CI 能否跑 | 一样 | 一样（靠 GitHub Actions） |

## 排障：刚装好却提示找不到 `gh`
- 可执行文件常在 `Program Files\GitHub CLI\`，系统 Path 已写，但**旧终端进程仍是安装前的 PATH**。
- 处理：关掉所有终端再开；或当前窗口刷新 Path 后再试。
