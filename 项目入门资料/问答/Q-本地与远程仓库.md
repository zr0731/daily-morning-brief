# Q：本地副本和 GitHub 是什么关系？没有本地行不行？

## 关系
- **本地目录**：编辑、本机试跑、放 `.env`（通常不进 Git）的工作副本。
- **GitHub 远程仓**：备份 +（若用了）Actions 定时跑任务、网页/手机改文件与打分反馈。

可以只有远程：需要时再 `git clone`。也可以本地长期留着方便改。

## 没有本地时怎么改 prompt 等
GitHub 网页或 App：打开文件 → Edit → Commit。下次 Actions 用最新提交。

## 没有本地时怎么试跑 `run.py`
- **不必 SSH。**
- 用仓库 **Actions → Run workflow**（`workflow_dispatch`），在云上跑；密钥用仓库 Secrets。
- 有本地时：项目目录 `python run.py`（或 `--dry-run`），密钥用本地 `.env`。

## SSH 何时才需要
自己另有一台服务器、要登录上去跑命令时。本机试跑或 GitHub Actions 都不依赖 SSH。
