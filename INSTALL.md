# Install from GitHub / 从 GitHub 安装

Entry point for an agent receiving only the repository URL. / 本文件供只收到仓库链接的 agent 直接执行安装。

Read this file, infer the current host from the actual execution environment, and follow one path below. A browser-only agent needs terminal/network capability before it can install. Installing does not require Node, an LLM API key, PPT files or access to the maintainer's computer. Use Python 3.9+ for the project installers/verifier; on Windows use the available `python` launcher if `python3` is absent. Install deck runtimes only when creating a presentation.

先阅读本文件，根据实际运行环境识别宿主，再选择一条安装路径。只读网页的 agent 需要本地终端和网络工具才能执行安装。安装本身不需要 Node、模型 API 密钥、PPT 或维护者机器上的文件。项目安装器和验证器使用 Python 3.9+；Windows 没有 `python3` 时使用可用的 `python`。制作演示时再安装演示运行依赖。

Repository / 仓库：`https://github.com/GabrielMu2006/slidev-studio`
Marketplace ID / 市场标识：`slidev-local`
Plugin ID / 插件标识：`slidev-studio@slidev-local`
Skills / 两项技能：`slidev`, `slidev-template-import`

## 1. Codex native plugin / Codex 原生插件

Inspect first / 先检查：

```bash
codex plugin marketplace list --json
```

If `slidev-local` is absent, add the Git source. / 如果不存在该市场，添加 Git 源：

```bash
codex plugin marketplace add GabrielMu2006/slidev-studio --json
```

If it already tracks this repository, refresh it instead. If the same name points elsewhere, report the conflict and retain that configuration until the user authorizes migration. / 如果已跟踪本仓库，刷新即可；如果同名市场指向其他来源，说明冲突并保留配置，获得用户迁移授权后再处理。

```bash
codex plugin marketplace upgrade slidev-local
codex plugin add slidev-studio@slidev-local --json
codex plugin list --marketplace slidev-local --json
```

Require `installed: true`, `enabled: true` and the intended version. Use the `installedPath` from `plugin add --json` for the helper verification below. Do not edit plugin caches or manually copy another skill into global skills. If `plugin add` is unavailable, add the marketplace and install from the desktop plugin directory; CLI-only installation then needs a host with that command. Respect host permissions and admin restrictions.

确认 installed、enabled 为 true，且版本符合预期。后续工具验证使用安装返回的 installedPath。不要手改缓存或复制重复全局 skill。旧 CLI 若不支持 plugin add，应在桌面插件目录安装；只有 CLI 时需要具备该命令的宿主版本。遵守宿主权限和管理员限制。

## 2. Claude Code native plugin / Claude Code 原生插件

In a terminal / 终端中：

```bash
claude plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio --json
claude plugin list --json
```

Inside Claude Code, use `/plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio`. For an existing install, refresh the marketplace and update the plugin using the CLI's documented commands (`claude plugin marketplace update slidev-local`, then `claude plugin update slidev-studio@slidev-local`). Validate success using the returned installed-plugin metadata. Do not infer model-session discovery from a schema check alone.

会话内可用对应的 /plugin install 命令。已有安装时，按 CLI 支持的 marketplace update 与 plugin update 命令刷新；使用返回的安装元数据确认成功。清单校验通过不等同于真实模型会话已经加载。

If native CLI access is unavailable but project skills are supported, use path 3 with `--agent claude`. / 若没有原生 CLI 但支持项目 skills，使用路径 3 的 --agent claude。

## 3. Cursor / project Claude / generic Agent Skills

Clone into a new working directory; preserve any existing checkout and use `git pull --ff-only` only when it is clean and tracks this repository. Use the user's current project root as PROJECT_PATH; if no project is established, obtain that path before installing project skills. Do not silently use the home directory or the plugin checkout as the target project.

克隆到新的工作目录；保留既有源码，仅对干净且跟踪本仓库的 checkout 使用 git pull --ff-only。PROJECT_PATH 应为用户当前项目根目录；没有明确项目时先确定路径，不要默默选择用户主目录或插件源码目录。

```bash
git clone https://github.com/GabrielMu2006/slidev-studio.git
cd slidev-studio
python3 scripts/release.py validate
python3 scripts/install_agent.py --agent cursor --project PROJECT_PATH
python3 scripts/verify_install.py --agent cursor --project PROJECT_PATH
```

Replace `cursor` with `claude` for `.claude/skills/`, or `generic` for `.agents/skills/`. Cursor uses `.cursor/skills/`. Both skills install/update together, with a version/hash receipt; unrelated skills are preserved. Local edits are refused, not overwritten. Archive or merge only the affected local edits with user authorization, then retry. Re-running the installer from an updated checkout is the update path.

cursor 对应 .cursor/skills，claude 对应 .claude/skills，generic 对应 .agents/skills。两项技能一起安装或更新并写入版本/哈希凭据；保留其他 skill，遇到本地修改会拒绝覆盖。经用户授权合并或归档相关修改后重试。拉取新版仓库后重跑安装器即可更新。

## 4. Verify and report / 验证并交付

For a native install, clone/read this repository and execute the verifier against the actual installed root returned by the host, without replacing that value with a source checkout. / 原生安装后，从本仓库运行验证器，传入宿主实际返回的已安装插件目录；不要拿源码目录冒充安装目录：

```bash
python3 scripts/verify_install.py --plugin-root INSTALLED_PLUGIN_PATH
```

The verifier compares both installed skill hashes with this checkout, runs the installed preset-list helper and template-bundle CLI, and reports `presetCount: 8`. Project installs use the `--agent ... --project ...` form above. Run validation against the same release/version as the install. If the versions differ, update the checkout or install explicitly; do not modify hashes to bypass verification.

验证器比对两项已安装 skill 的内容哈希，直接运行安装副本中的预设列表和完整模板 CLI，报告 presetCount: 8。项目安装使用上面的 --agent/--project 参数。验证源码和安装应为同一版本；不一致时先对齐版本，不能修改哈希绕过验证。

Report host, install location, version, verification result and any remaining host-discovery step. Start a fresh chat/session to refresh skills. If the host exposes skill discovery, confirm both skills appear there; helper verification alone does not prove model invocation. Native Codex currently namespaces them as `slidev-studio:slidev` and `slidev-studio:slidev-template-import`. Test with “List Slidev Studio's eight style presets.”

向用户报告宿主、安装位置、版本、验证结果及尚需完成的宿主刷新步骤。新建聊天/会话刷新 skill；宿主若提供技能发现接口，还应确认两项技能确实出现。工具运行验证不能单独证明模型调用。Codex 当前以带插件前缀的名称显示技能。可用“列出 Slidev Studio 的八套风格模板”测试。

No local execution available? State the missing capability and supply the applicable commands; do not claim installation succeeded. / 没有本地执行能力时，明确缺少什么并给出适用命令，不要声称已经安装。

Sources / 官方依据：[Codex](https://developers.openai.com/plugins/build/plugins), [Claude Code](https://code.claude.com/docs/en/plugins-reference), [Cursor skills](https://cursor.com/docs/skills).
