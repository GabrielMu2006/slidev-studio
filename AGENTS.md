# Agent entry points

Installation/update request: Slidev Studio is a plugin package containing two skills. Read README.md and INSTALL.md, identify the active host, and execute its Claude Code / ZCode / DSH / Codex native route. A copied skills bundle is skills-compatibility mode, not native registration. Do not select a host merely because its CLI exists. Report native registration, skill discovery and content/helper checks separately; unavailable GUI access means pending, not silent skills fallback. Use existing user authorization for compatibility alternatives and cleanup.

用户从仓库要求安装/更新时，先判断当前宿主，再按 README.md、INSTALL.md 执行专用路线。只复制 skill 不能报告插件已注册；分别报告插件登记、技能发现、文件工具验证。保留已有项目与自定义设置。

Development: canonical skills live under plugins/slidev-studio/skills. Do not edit installed caches or maintain duplicate global skills. Read docs/UPDATING.md before releases. Synchronize VERSION, all host manifests, both skills and the DSH package with scripts/release.py; run Python and Node tests and build archives. Never include user references, generated projects, credentials or host-specific paths. Full imported templates require native reusable layouts and actual build/visual evidence.
