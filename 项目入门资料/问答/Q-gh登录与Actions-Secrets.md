# Q：`gh auth` 要每次登吗？API Key 填在哪？

## `gh auth login` / 刷新 PATH
| 操作 | 要不要每次做 |
|------|----------------|
| `gh auth login` | **不用**。登录状态保存在本机（如 keyring），`gh auth status` 显示 Logged in 即可 |
| 刷新 `$env:Path = ...` | **不用每次**。只在「刚装完软件、当前窗口还是旧 PATH」时救急；以后新开终端一般自带 |
| `gh --version` | 可选自检，非必须 |

## GitHub Actions Secrets 在哪填
密钥给 **Actions 跑任务** 用，不在代码文件里、也不在普通 Settings 首页一眼看到。

网页路径（须是仓库 **owner**，已登录）：

1. 打开仓库 → **Settings**（设置）
2. 左侧 **Secrets and variables** → **Actions**
3. **New repository secret**
4. 逐个添加，例如：`DEEPSEEK_API_KEY`、`BARK_DEVICE_KEY`（可选 `BARK_SERVER`）

注意：
- 选的是 **Actions** secrets，不是 Environments，也不是 Dependabot。
- 个人免费仓：Settings 在仓库页顶栏；看不到 Settings 多半是没权限或看错了 fork。

命令行等价（本机已 `gh auth`）：
```powershell
gh secret set DEEPSEEK_API_KEY
gh secret set BARK_DEVICE_KEY
```
按提示粘贴值（不会显示在仓库文件里）。

## 和本地 `.env` 的关系
- 本地试跑：用项目里的 `.env`（勿提交）。
- GitHub 定时/手动 Actions：用仓库 Secrets；两边值应一致，但是两套存放位置。
