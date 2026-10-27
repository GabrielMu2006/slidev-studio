# Agent installation playbook / Agent 安装执行指南

Slidev Studio 是插件包，其中包含 `slidev` 和 `slidev-template-import`。原生插件注册、skill 可发现性、文件/工具完整性是三个独立检查。仅复制 skill 不等于安装原生插件。

Slidev Studio is a plugin package containing two skills. Native registration, skill discovery and file/helper integrity are separate checks. A copied skills bundle is not a native plugin registration.

Repository: `https://github.com/GabrielMu2006/slidev-studio` · Native marketplace: `slidev-local` · Plugin: `slidev-studio`

## 先判断 / Decide first

- 识别**当前会话所属宿主**和实际运行 profile/工作区，不能仅根据机器安装了哪个 CLI 判断。先读取其现有插件记录，保留同名来源冲突和本地修改，按用户授权处理。
- 用户要求插件时，使用下面四条原生路线；不能操作某宿主界面时报告 pending，不能擅自改装 skills。用户已接受兼容方式时才走其他路线的 skills 分支。
- 缺少终端/网络/GUI 或管理员限制时，明确哪一步未完成。不要安装另一个 agent 来绕过限制，不要直接改未公开的插件注册配置。
- 原生安装无须另建名为 slidev-studio 的 SKILL.md，也无须复制到全局 skills。已有兼容副本先保留；原生验证通过且用户授权清理后，归档再移除重复副本。

Identify the active host and its actual profile/workspace, not merely available binaries. Inspect existing registrations first. Native-plugin requests use native routes; unavailable GUI control means pending, not silent fallback. Follow existing user authorization for conflicts and compatibility alternatives. Preserve compatibility copies until native checks pass and cleanup is authorized. Do not invent a top-level slidev-studio skill or edit undocumented registration stores.

<a id="claude"></a>
## Claude Code — native plugin / 原生插件

适用于当前宿主为 Claude Code，且其 CLI 支持 plugin 子命令。/ Use only for an active Claude Code host with native plugin commands.

```bash
claude plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio --json
claude plugin list --json
```

会话内可用 `/plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio`。已有版本先用 `claude plugin marketplace update slidev-local` 刷新，再 `claude plugin update slidev-studio@slidev-local`。检查插件身份、版本和启用状态；两项 skill 来自该插件。宿主版本不支持时查本机 --help 与官方文档，不要改成复制 skills 后声称插件完成。

The equivalent session slash command is supported. Refresh the marketplace and update the installed plugin for upgrades. Require a native registration, enabled state and plugin-origin skills. Consult local help for version differences; do not substitute copied skills and report native success.

<a id="zcode"></a>
## ZCode — native marketplace / 原生插件市场

ZCode 支持原生插件，并优先读取 `.zcode-plugin/plugin.json`，兼容 `.claude-plugin/plugin.json`。本仓库提供根 `marketplace.json` 与专用 `.zcode-plugin/plugin.json`。两项技能位于插件的单层 skills/<name>/SKILL.md 中。

ZCode supports native plugins; this repo supplies its recommended manifest plus a root marketplace catalog. Its bundled skills remain in the flat plugin skills tree.

1. 打开实际工作区。/ Open the intended workspace.
2. 进入 **设置 → 插件 → 创建 → 添加插件市场**。/ Open **Settings → Plugins → Create → Add marketplace**.
3. 添加 `https://github.com/GabrielMu2006/slidev-studio`。/ Add the repository URL.
4. 在市场 **slidev-local** 中安装并启用 **slidev-studio**。/ Install and enable the plugin from that marketplace.
5. 打开插件详情，核对版本与两个 skill；在 **设置 → 技能 → Plugin 技能** 中确认它们属于此插件。/ Check version/components in plugin details and both skills in the Plugin skills group.

若已有市场，刷新该市场并在插件管理页面检查更新；ZCode 以市场条目的 version 与已安装清单版本比较。若已安装只是不启用，启用已有注册，不要重复导入技能。只在“用户技能”或 ~/.zcode/skills 看见副本，不能证明插件已注册；反之，在 Plugin 技能分组看到两个 skill 是正常的。

Refresh an existing marketplace before checking updates. A plugin-owned skill listing is expected. User-level skill files alone do not establish native registration. If the agent has GUI tools, execute the UI path; otherwise report the precise remaining GUI actions. No ZCode installation CLI is assumed by this guide.

已有 skills 兼容副本的迁移：检查其来源和安装凭据，先完成原生插件注册及 A/B/C 检查，再按用户授权归档重复副本。不要在诊断时删除自定义技能或仅因看到技能列表就卸载插件。

For migration, identify compatibility origins/receipts, finish native A/B/C checks, then archive duplicates only within user-authorized cleanup scope. Preserve customized skills.

<a id="dsh"></a>
## DeepSeek Harness / DSH — native bundle / 原生 bundle

DSH 使用 Cordis/Node 插件机制，与 Claude/ZCode 的 JSON 插件清单不同。本仓库根 package.json 声明 dsh.bundle，`adapters/dsh` 原生适配器向当前 ctx.skills 注册 provider；直接读取同一份 canonical 两项 skill，不往全局 skills 复制文件。

DSH uses a distinct Cordis/Node plugin system. The root package declares dsh.bundle; its adapter registers a provider over the same canonical skill files without copying global skills.

1. 通过当前会话/DSH 插件管理器确认 **实际正在运行的 profile**，例如 desktop、web、headless 或用户自定义名称。CLI 存在不代表目标 profile；不知道时先确定，不要随意新建 web/headless 冒充当前安装。
2. 读取本仓库 VERSION，使用匹配 tag 的 Git 源，或下载 GitHub Release 中同版本的 `slidev-studio-dsh-VERSION.tgz`。
3. 在该 profile 的原生插件管理器安装 bundle，或使用本机 CLI 支持的命令：

Determine the profile actually running the user's session. Resolve VERSION and its matching Git tag or release tarball, then install into that profile through its plugin manager or CLI. Replace both placeholders below with confirmed values:

```bash
dsh plugin --profile "ACTIVE_PROFILE" add "git+https://github.com/GabrielMu2006/slidev-studio.git#vVERSION"
# Alternatively: use the downloaded same-version native package.
dsh plugin --profile "ACTIVE_PROFILE" add "/absolute/path/to/slidev-studio-dsh-VERSION.tgz"
```

4. 在该 profile 的插件/bundle 列表确认 slidev-studio 已启用且无挂载错误；确认 provider 激活，两个 skill 可发现并能加载正文。只有依赖下载成功或 bundle 已选中，不足以证明 provider 已激活。
5. profile 需要提供 skills 注册服务和面向模型的 skill consumer（官方 dsh-skill、dsh-tool-skill）；缺少时依据该 profile 的官方机制处理，不能只拷贝 skills 假装原生。按宿主要求刷新/重启，使新 bundle 生效。

Require enabled, error-free native bundle activation, then actual provider/skill discovery. A downloaded dependency or selected bundle alone is insufficient. The profile needs its skill registry and consumer services; follow the installed host's documented mechanism if absent. Refresh/restart when required. No model API call is required for file/provider checks.

更新时按当前 CLI/plugin-manager 能力替换为新 VERSION 的 Git tag/tarball，保留当前 profile 与启用状态；Git/tarball来源不保证享受 npm 版本检查按钮，显式版本替换是本仓库支持的更新路径。不要把不存在的 npm 包名当作已发布包安装。

Update by explicitly replacing the Git/tag or tarball version in the same profile. Registry-only auto-update features need not apply to Git/tarball sources. This project does not claim an npm registry publication.

<a id="codex"></a>
## Codex — native plugin / 原生插件

```bash
codex plugin marketplace list --json
```

不存在 slidev-local 时添加；已跟踪本仓库时升级。/ Add if absent; refresh if it already tracks this repository.

```bash
codex plugin marketplace add GabrielMu2006/slidev-studio --json
# For an existing marketplace:
codex plugin marketplace upgrade slidev-local
codex plugin add slidev-studio@slidev-local --json
codex plugin list --marketplace slidev-local --json
```

检查 installed/enabled、version 和来源；保存安装返回的 installedPath。仅在当前 Codex 宿主执行。旧 CLI 若不支持 plugin add，则使用桌面插件目录完成，不要转成 skills 兼容后报告原生安装成功。新会话应发现 slidev-studio:slidev 与 slidev-studio:slidev-template-import，来源为该插件。

Require installed/enabled state, correct version/source and the returned installedPath. A host without plugin add needs its supported desktop installation path. Fresh skill discovery should show both plugin-origin skills. Do not use a different host's CLI as evidence for the active agent.

<a id="other"></a>
## 其他 agent / Other hosts

先查该宿主当前官方文档或实际工具。若支持 Claude 兼容插件市场，使用其原生市场入口添加本仓库；若是其他插件格式，不能仅凭有 SKILL.md 就宣称原生适配。若仅支持 Agent Skills，向用户说明将使用 skills 兼容模式；用户已授权该方式时再安装两项 skill，报告 mode 为 skills-compatibility。

Establish the host's actual native plugin format first. Use a documented Claude-compatible marketplace route when supported. A different plugin format needs a real adapter, not a renamed skills folder. For a skills-only host, explain compatibility mode and proceed when that mode is already authorized.

```bash
git clone https://github.com/GabrielMu2006/slidev-studio.git
cd slidev-studio
python3 scripts/release.py validate
python3 scripts/install_agent.py --agent generic --project "PROJECT_PATH"
python3 scripts/verify_install.py --agent generic --project "PROJECT_PATH"
```

仅在宿主文档确认会扫描 .agents/skills 时使用 generic；否则采用该宿主公开的技能导入入口或目录，保持两项 skill 相邻且资源完整，并验证发现结果，不能只凭文件存在宣告可用。

Use generic only when the host documents .agents/skills discovery. Otherwise use its documented skills import/directory, keep both sibling bundles and resources together, and verify discovery rather than file existence alone.

Cursor 项目 skills 使用 --agent cursor（.cursor/skills）；Claude 项目 skills 使用 --agent claude（.claude/skills）；generic 使用 .agents/skills。三者都只是 skills 兼容安装，不会注册到原生插件管理器。PROJECT_PATH 为用户已确认的项目根，不得默选主目录或插件源码目录。旧安装保留哈希凭据，更新拒绝覆盖本地修改。

All three installer targets are skills compatibility copies, never native registrations. Use the established project root, preserve unrelated files and respect local edits. Windows may use python instead of python3. Python 3.9+ is needed for these tools; installing a deck's Node dependencies belongs to presentation creation, not plugin setup.

## A / B / C 验证及交付 / Verify and report

| 层 / Layer | 证据 / Evidence |
| --- | --- |
| A 原生注册 / Native registration | 当前宿主插件管理器里的身份、来源、版本、启用和无错误状态；DSH 还要 bundle/provider 激活 / Current-host registration, version, source and active state |
| B Skill 可用 / Discovery | 两项 skill 属于该插件/provider，能发现并加载；pending 与已通过要分开 / Both plugin-origin skills discoverable/loadable |
| C 文件与工具 / Content | 同版本内容哈希、已安装副本工具、八套目录 / Same-version hashes and installed helper execution |

从同版本 checkout 运行下列命令，传入真实已安装的 portable plugin 子目录；DSH 包内对应 plugins/slidev-studio。不要拿源码目录冒充安装副本。

Run against the actual installed portable-plugin directory from a matching checkout. For DSH, that directory is plugins/slidev-studio inside the installed native package:

```bash
python3 scripts/verify_install.py --plugin-root "INSTALLED_PLUGIN_PATH"
```

输出 installationType=plugin-package 仅表示有插件清单且内容可用，hostRegistrationVerified=false 表示 A 仍需宿主证据。skills-compatibility 输出明确标识 nativePluginRegistered=false。两项 skill 是 slidev、slidev-template-import；八套清单为青蓝课堂、清简、纸上学术、夜间技术、咨询蓝、琥珀叙事、蓝图实验、玫瑰演讲。

A plugin-package result verifies package files, not native host registration. The explicit hostRegistrationVerified=false requires separate A evidence. Compatibility installs report nativePluginRegistered=false. Require both skills and all eight retained presets; file/helper checks do not establish a real model-session invocation.

最终报告 / Final report：宿主及 profile、mode（native-plugin / skills-compatibility / pending）、版本、位置、A/B/C 分别的状态和证据、尚需用户操作/会话刷新；无执行能力时具体说明阻塞，不能虚报安装成功。

官方依据 / Sources：[Claude](https://code.claude.com/docs/en/plugins-reference), [ZCode](https://zcode.z.ai/cn/docs/plugin), [DSH CLI](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md), [DSH skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md), [Codex](https://developers.openai.com/plugins/build/plugins).
