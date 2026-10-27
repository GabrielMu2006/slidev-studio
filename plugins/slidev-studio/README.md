# Slidev Studio — Plugin / 插件

本目录是 **原生插件包**，包含 slidev 与 slidev-template-import 两项 skill、本地工具和八套已保留风格预设（第 1 套为青蓝课堂）。安装入口是仓库 [README](https://github.com/GabrielMu2006/slidev-studio#readme) 与 [INSTALL.md](https://github.com/GabrielMu2006/slidev-studio/blob/main/INSTALL.md)。

请按当前宿主选择 Claude Code、ZCode、DeepSeek Harness 或 Codex 的原生路线；其他 agent 先确认实际插件格式。只复制 skills 目录属于 skills 兼容模式，不能报告已在宿主中注册插件。插件提供的 skill 出现在技能列表中是正常现象；还需核对插件管理器登记与来源。

This is the **native plugin payload**, containing two skills, local tools and the eight retained presets. Follow the repository README and INSTALL.md for the active host's native route. A copied skills directory is compatibility mode, not a native registration. Plugin-origin skills normally appear in skill lists; check host registration as well.

The package verifier proves manifests/content/helper execution only. Report native registration, skill discovery and helper checks separately. Claude Code native install: `/plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio`.

The DSH native adapter lives in the repository's root Node package and reads this payload.

```bash
python3 skills/slidev/scripts/studio.py list
python3 skills/slidev/scripts/studio.py serve /path/to/talk --no-browser
```

创作与完整模板导入分别遵循 skills/slidev/SKILL.md 和 skills/slidev-template-import/SKILL.md。用户项目和模板库放在插件缓存之外；更新随统一插件版本发布。

Use the two bundled skill entry points for authoring and full reference-template import. Keep projects/libraries outside caches; both skills update with the plugin release.
