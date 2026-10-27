# Slidev Studio

Create expressive Slidev decks, choose visual presets, and let your agent distill a complete reusable template from a reference PowerPoint.

Two skills ship in one versioned plugin:

- **slidev**: authoring, code walkthroughs, Vue interactions, diagrams, math, presentation and export verification, with a local style-preset picker.
- **slidev-template-import**: inspect/render a PPTX, infer its design, implement native layouts/components/assets, compare the result, and register a complete template bundle.

The agent interprets design. Python tools handle inspection and packaging; there is no hidden LLM API. Full templates contain actual layout code, resources, source references and verification evidence. Color presets remain a separate lightweight feature.

## Install

### Codex

```bash
codex plugin marketplace add GabrielMu2006/slidev-studio
codex plugin add slidev-studio@slidev-local
```

Start a fresh chat after installing. Example: “Extract a reusable Slidev template from this PowerPoint, then create a new talk in that style.”

### Claude Code

```text
/plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio
```

The traditional marketplace-add/plugin-install workflow also works. Native manifests load the same canonical skills.

### Cursor and other Agent Skills hosts

```bash
git clone https://github.com/GabrielMu2006/slidev-studio.git
cd slidev-studio
python3 scripts/install_agent.py --agent cursor --project /path/to/project
# --agent generic installs in .agents/skills/
# --agent claude installs in .claude/skills/
```

The managed installer records hashes, updates both skills together, and refuses to overwrite local changes. Releases include a portable skills ZIP. See [compatibility](docs/COMPATIBILITY.md) and [updates](docs/UPDATING.md).

## Use

中文示例：“读取这份 PPT，提炼封面、章节、图文和表格布局，制作完整 Slidev 模板并加入我的模板库。”然后：“从模板库选择刚才导入的模板，创建一份新演示。”

From the plugin directory (`plugins/slidev-studio` in a checkout):

```bash
python3 skills/slidev/scripts/studio.py serve /path/to/talk --no-browser
python3 skills/slidev-template-import/scripts/inspect_pptx.py reference.pptx --out ./analysis --render
python3 skills/slidev-template-import/scripts/template_bundle.py list --library ./my-template-library
python3 skills/slidev-template-import/scripts/template_bundle.py instantiate my-template --library ./my-template-library --out ./new-talk
```

The four presets are ICS Course, Minimal Light, Academic Paper and Terminal Dark. ICS adapts general traits from [this public reference](https://slide.huh.moe/00/1) with original SVG cover art. The picker edits presets; full templates use the agent/library workflow.

Full templates have independent immutable versions in a user-selected library outside plugin caches. Changed designs need a new template version. Installing never executes template code. Creating a deck refuses existing destinations. ZIP export includes references; publish them only when the user requested sharing them.

## Requirements

- Python 3.9+ for tooling.
- Node satisfying the deck CLI's engines (tested baseline: Slidev 53.0.0, Node >=22.12.0).
- Optional LibreOffice + Poppler for PPTX rendering, or a host-provided renderer.
- CLI PDF/PPTX/image export needs Playwright/Chromium as explained by the authoring skill.

Rendering and visual inspection are required before marking a template verified. Metadata extraction alone remains a draft. Static exports differ from live web decks. Slidev PPTX export uses rendered slide images; it does not produce object-editable PowerPoint slides.

## Development and releases

```bash
python3 scripts/release.py sync 0.2.1
python3 -m unittest discover -s plugins/slidev-studio/tests -v
python3 -m unittest discover -s tests -v
python3 scripts/release.py validate
python3 scripts/release.py build
```

One VERSION controls manifests, marketplace metadata and both skill versions/hashes. Pushing a matching `vX.Y.Z` tag runs tests and publishes deterministic archives with SHA256SUMS. The upstream-check workflow reports changes for deliberate review and never overwrites customizations or user libraries.

## License

MIT; see [LICENSE](plugins/slidev-studio/LICENSE) and [NOTICE](plugins/slidev-studio/NOTICE.md). Original syntax references derive from the official Slidev skill. This is an independent project, not an official Slidev or OpenAI plugin.
