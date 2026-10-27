# Host compatibility and validation / 宿主兼容性与验证

Slidev Studio is a plugin package with two skills; a skills-only content bundle is a separate compatibility installation. Start with [INSTALL.md](../INSTALL.md).

| Host | Route | Evidence / limits |
| --- | --- | --- |
| Claude Code | Native Claude manifest/marketplace | Native manifest validator; actual model session not run |
| ZCode | Root marketplace.json + .zcode-plugin/plugin.json | Layout/version/source checks against official format; no claim that the user's ZCode was migrated |
| DeepSeek Harness | Native Node/Cordis dsh.bundle and skill provider | Isolated native CLI bundle install and real DSH 0.2.1-rc.3 registry/provider loading passed; model session not run |
| Codex | Native Git marketplace/plugin | Installed content/helper checks and fresh app-server discovery |
| Other Agent Skills hosts | Explicitly accepted skills-compatibility installer | Content, receipts and local helpers; no native host registration |

A plugin can contain only skills plus resources. It does not need a dummy MCP server or unused commands to count as a plugin. Native status comes from the host registration and lifecycle, not a directory label or the mere presence of a SKILL.md file.

原生插件中的两项 skill 出现在技能列表里是正常现象。ZCode 的 Plugin 技能与用户技能来源不同；不能仅看见技能名就断言装错。通用安装器输出 skills-compatibility / nativePluginRegistered=false；包验证器验证清单和工具，但不会伪造宿主注册证明。

Python 3.9+ runs local tools. Node satisfying the deck CLI is needed for presentation creation; DSH also uses Node to load its native provider. References between skills are relative; both skills must travel together. User libraries and generated decks stay outside plugin caches.

Sources: [ZCode plugins](https://zcode.z.ai/cn/docs/plugin), [ZCode skills](https://zcode.z.ai/cn/docs/skill), [DSH](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md), [Claude](https://code.claude.com/docs/en/plugins-reference), [Codex](https://developers.openai.com/plugins/build/plugins).
