# 晨间简报（DeepSeek + Bark + GitHub Actions）

每天北京时间 **07:00** 自动：

1. 用 DeepSeek 跑 3 个任务（游戏创意 / 概念寓言 / 商业故事）
2. 合并成一份「报纸式」简报
3. **Bark** 推到手机
4. 全文归档到仓库 `archive/YYYY-MM-DD.md`

## 目录

- `prompts/`：任务提示词（可改）
- `archive/`：每日完整简报（GitHub 归档）
- `feedback/`：任务一打分（手机编辑后次日生效）
- `src/`：脚本
- `.github/workflows/daily-brief.yml`：定时任务

## 一次性设置

### 1. 推到 GitHub

在桌面项目目录：

```powershell
cd $env:USERPROFILE\Desktop\daily-morning-brief
gh repo create daily-morning-brief --private --source=. --remote=origin --push
```

若不用 `gh`：在 GitHub 新建空私有仓库，再 `git remote add` + `push`。

### 2. 配置 Secrets

仓库 → **Settings → Secrets and variables → Actions**，添加：

| Name | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `BARK_DEVICE_KEY` | Bark 设备 key |
| `BARK_SERVER` | 可选，默认 `https://api.day.app` |

本地已有 `.env`（已 gitignore），仅供本机试跑，**不要提交**。

### 3. 试跑

本机：

```powershell
cd $env:USERPROFILE\Desktop\daily-morning-brief
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

或在 GitHub → Actions → **daily-morning-brief** → **Run workflow**。

## 手机打分（任务一反馈）

Bark **单向推送**，不能在通知里直接回复并回写仓库。等价做法：

1. 点推送打开「报纸」全文（`archive/`）
2. 再点正文里的「给游戏创意打分」链接（打开 GitHub 网页编辑 `feedback/当天.md`）
3. 填 1～10 分与评语 → Commit
4. **次日 07:00** 任务一会自动读昨日反馈并据此生成

手机建议装 GitHub App，编辑更稳。

## 时区说明

`cron: 0 23 * * *` = UTC 23:00 = 北京时间次日 07:00。若夏令时地区无需调整（中国无夏令时）。
