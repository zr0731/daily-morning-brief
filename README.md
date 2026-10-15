# 晨间简报（DeepSeek + PushPlus + GitHub Actions）

每天北京时间 **07:00** 自动：

1. 用 DeepSeek 跑 3 个任务（游戏创意 / 概念寓言 / 商业故事）
2. 合并成一份「报纸式」简报
3. **PushPlus** 推到微信服务号（全文，无需打开 GitHub）
4. 全文同时归档到仓库 `archive/YYYY-MM-DD.md`

## 目录

- `prompts/`：任务提示词（可改）
- `archive/`：每日完整简报
- `feedback/`：任务一打分（次日生效；建议在电脑填写）
- `src/`：脚本
- `.github/workflows/daily-brief.yml`：定时任务

## 一次性设置

### Secrets

仓库 → **Settings → Secrets and variables → Actions**：

| Name | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `PUSHPLUS_TOKEN` | PushPlus 用户/消息 token |

本地 `.env`（已 gitignore）示例：

```env
DEEPSEEK_API_KEY=...
PUSHPLUS_TOKEN=...
```

### 试跑

```powershell
cd $env:USERPROFILE\Desktop\daily-morning-brief
.\.venv\Scripts\Activate.ps1
python run.py
```

或 Actions → **Run workflow**。

## 手机打分

微信里读全文即可。打分请在**电脑**编辑 `feedback/当天.md` 后 Commit；次日任务一会读昨日反馈。

## 时区

`cron: 0 23 * * *` = UTC 23:00 ≈ 北京时间次日 07:00（GitHub 可能延迟）。
