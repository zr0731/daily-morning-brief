# Q：终端相关配置改哪里？

## 口诀
外观 → Terminal 设置；一开机自动跑什么 → `$PROFILE`；conda 默认环境 → `.condarc`；命令认不认识 → PATH。

## 四层对照

| 层 | 管什么 | 常见位置 / 改法 |
|----|--------|-----------------|
| Windows Terminal | 字体、配色、默认壳、启动目录 | 终端 → 设置；或 `settings.json` |
| PowerShell Profile | 每次打开自动执行的脚本（conda 钩子、别名） | `echo $PROFILE` 打开该文件 |
| conda | 是否自动 `activate base` | 用户目录 `.condarc` 的 `auto_activate_base`；或 `conda config --set auto_activate_base false` |
| PATH | `gh`/`git` 等能否被找到 | 系统「环境变量」里的 Path；当前窗口可临时拼回 Machine+User Path |

## conda 自动进 base 又慢
- 关：`auto_activate_base: false`（写入 `.condarc`）
- 需要时再：`conda activate base`（或其它环境名）
- 改完要**新开终端**；「Anaconda Prompt」快捷方式仍可能一进来就激活，日常用普通 PowerShell 即可。

## 装完软件却「命令不存在」
进程启动时拷贝 PATH，不会自动跟上新安装。新开终端，或刷新当前会话的 Path。
