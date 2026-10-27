# Agent compatibility

| Host | Installation | Validation scope |
| --- | --- | --- |
| Codex | Native Git marketplace/plugin | Fresh app-server skill discovery and installed helper execution |
| Claude Code | Native Claude manifest/marketplace, or project skill installer | Native manifest validation; no paid model session required |
| Cursor | `scripts/install_agent.py --agent cursor --project PATH` | Both skills and relative resources copied to documented project skill directory |
| Other Agent Skills hosts | `--agent generic`, or portable skills ZIP | Standard SKILL.md/resources and ordinary Python CLI; host must permit local tools |

Python 3.9+ runs the tools. Creating/presenting Slidev needs Node satisfying the deck's CLI engine requirement (53.0.0: >=22.12.0). PPTX inspection uses the Python standard library; optional source rendering uses LibreOffice and Poppler, or the agent host's own renderer. The LLM supplies design interpretation; there is no hidden API dependency.

The two skills travel together. References between them are relative to sibling directories. No runtime path points to a maintainer's home directory, another installed plugin, or Codex-only tool IDs. Host-provided render/browser capabilities are discovered at use time.

The visual picker manages style presets; full reference-backed templates use the agent import/library workflow. Full templates are not automatically published with the plugin. Native model execution in Claude/Cursor is separate from manifest/directory validation and should not be inferred from it.

Sources: [Codex packaging](https://developers.openai.com/plugins/build/plugins), [Claude manifests](https://code.claude.com/docs/en/plugins-reference), [Cursor skill directories](https://cursor.com/docs/skills).
