# Slidev Studio

[中文 / English README](https://github.com/GabrielMu2006/slidev-studio#readme) · [Agent 安装 / Agent installation](https://github.com/GabrielMu2006/slidev-studio/blob/main/INSTALL.md)

## 中文

插件包含两项统一版本的 skill：`slidev`（Slidev 创作、风格选择器、交互与导出）和 `slidev-template-import`（从 PPT 提炼完整模板并验证、入库、复用）。八套内置风格为 ICS 课程、清简、纸上学术、夜间技术、咨询蓝、琥珀叙事、蓝图实验和玫瑰演讲。它们是可调整的风格预设；从 PPT 提取的完整布局模板使用单独的模板库。

从 GitHub 安装：

```bash
codex plugin marketplace add GabrielMu2006/slidev-studio
codex plugin add slidev-studio@slidev-local --json
```

Claude Code 使用 `claude plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio`。Cursor 和其他 agent 请按上方安装文档操作。安装/更新后新建聊天；两项 skill 共用一个版本，不再另装全局重复副本。

从本插件目录运行：

```bash
python3 skills/slidev/scripts/studio.py list
python3 skills/slidev/scripts/studio.py serve /path/to/talk --no-browser
python3 skills/slidev/scripts/studio.py new ./talk --template editorial-amber --title "让复杂的想法变得清晰"
python3 skills/slidev/scripts/studio.py apply ./talk --template consulting-blue
python3 skills/slidev/scripts/studio.py restore ./talk
```

选择器可设置颜色、字体、字号、留白、比例、转场、页码和版式气质，支持本地封面图片和项目预设。应用保留正文、备注与组件，并备份受管理文件；遇到复杂样式入口或 YAML 会拒绝自动覆盖。完整 PPT 模板导入流程见 `skills/slidev-template-import/SKILL.md`。

Python 3.9+ 可运行工具；真实演示需要符合 CLI 要求的 Node。样式预览不执行 Vue 动画；交付前须检查真实 Slidev 页面及导出。普通 PPTX 是图片；可编辑导出需检查当前 CLI 支持及实际结果。

## English

Two coordinated skills ship together: `slidev` (authoring, preset picker, interactions and exports) and `slidev-template-import` (PPT-derived full templates, verification, library registration and reuse). Eight built-in styles are ICS Course, Minimal Light, Academic Paper, Terminal Dark, Consulting Blue, Editorial Amber, Blueprint Lab and Keynote Rose. These are configurable style presets; full layout bundles use a separate template library.

Install from GitHub using the Codex commands above, or `claude plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio` for Claude Code. Cursor and generic hosts follow the linked installation guide. Start a fresh chat after installation/update; do not add duplicate global skill copies.

Run the commands above from this plugin directory to list, preview, create, apply and restore presets. The picker configures colors, typography, spacing, aspect ratio, transitions, page numbers and composition. It supports local cover images and project presets. Applying preserves narrative, notes and components, backs up managed files, and refuses complex style-entry/YAML replacements. See `skills/slidev-template-import/SKILL.md` for full reference-template import.

Python 3.9+ runs the tools; real decks require Node satisfying the installed CLI. Style previews do not execute Vue animation. Inspect real Slidev pages and exports before delivery. Ordinary PPTX uses rendered images; verify editable-export availability and actual output against the installed CLI.

[Templates / 模板预览](https://github.com/GabrielMu2006/slidev-studio/blob/main/docs/TEMPLATES.md) · [Unified updates / 统一更新](https://github.com/GabrielMu2006/slidev-studio/blob/main/docs/UPDATING.md)
