# Slidev Studio

Claude Code install: `/plugin install slidev-studio --marketplace GabrielMu2006/slidev-studio`.

This release includes `slidev-template-import` alongside `slidev`. Read that skill for full reference-backed layouts/components/assets and template library commands. The picker below manages lightweight style presets. See the repository README for unified updates and cross-agent installation.

本地 Codex 插件：选择和设置模板，再制作、预演、检查和导出 Slidev 演示文稿。

包含四套样式：**ICS 课程、清简、纸上学术、夜间技术**。ICS 风格参考了 [这份课程演示](https://slide.huh.moe/00/1) 的深色封面、白底内容页和青蓝标题；使用原创本地芯片插画，没有复制原作者的个人信息或封面照片。

## 使用

安装后，在新聊天中调用插件，或直接说：

- “用 Slidev Studio 帮我选择模板，并创建一份中文课程演示。”
- “打开这份 Slidev 项目的模板设置，把强调色改成深红，使用 4:3。”
- “把当前样式保存成我自己的课程模板。”

插件包含一个 skill 和一个 Python 标准库实现的本地模板选择器。选择器在浏览器中运行；它不是 Codex 原生设置面板，也不需要云端服务、API 密钥或额外 MCP 服务。制作演示时，Codex 会继续使用完整的 Slidev 工作流。

## 本地安装

在解压后的 `slidev-marketplace` 目录中执行：

```bash
codex plugin marketplace add .
codex plugin add slidev-studio@slidev-local
codex plugin list --marketplace slidev-local --json
```

如果当前 CLI 没有 `plugin add`，将该目录作为本地 marketplace 添加后，在桌面应用的插件目录中选择 **Slidev Local Studio** 安装。安装/更新后重新打开聊天，必要时重启应用以重新加载技能。参考 [官方打包说明](https://developers.openai.com/plugins/build/plugins)。

## 直接运行选择器

从插件根目录执行：

```bash
python3 skills/slidev/scripts/studio.py serve /absolute/path/to/my-talk --no-browser
```

打开终端打印的 localhost 链接。选择模板、调整标题/颜色/字体/字号/留白/比例/转场/页码，查看封面与内容页样式预览，再应用。首次创建项目后可导入本地封面图片，或将当前设置另存为项目模板。

Python 3.9+ 即可运行选择器。演示项目需要 Node；已验证的 CLI 53.0.0 要求 Node >=22.12.0。

## 命令行

```bash
python3 skills/slidev/scripts/studio.py list
python3 skills/slidev/scripts/studio.py new ./my-talk --template ics-course --title "计算机系统导论"
python3 skills/slidev/scripts/studio.py apply ./my-talk --template academic-paper --set titleSize=40
python3 skills/slidev/scripts/studio.py apply ./my-talk --set aspectRatio=4/3 --set pageNumbers=false
python3 skills/slidev/scripts/studio.py save-template ./my-talk --id my-course --name "我的课程模板"
python3 skills/slidev/scripts/studio.py restore ./my-talk
```

创建命令拒绝覆盖已有目录。应用模板保留正文、备注和组件；它修改指定的 headmatter 标量和一个受管理的 CSS 区块，并保存备份。重复应用相同配置不改文件。

配置保存在 `slidev-studio.json`；自定义模板在 `slidev-templates/`；备份在 `.slidev-studio/backups/`。复制自定义模板到别的项目时，同时复制引用的 `public/` 资源。

现有项目的自动应用目前支持普通 `slides.md` 与 `styles/index.css`。如果已有 `style.css`、`styles/index.ts/js`、复杂的受管理 YAML 字段或自定义主题覆盖，助手需要沿用项目现有入口手动整合样式；工具会拒绝直接覆盖。不要为套模板而删除项目设置。

## 制作与验证演示

在新演示项目目录内：

```bash
pnpm install
pnpm run dev
pnpm run build
# 需要 CLI 导出时：
pnpm add -D playwright-chromium
pnpm run export --output handout.pdf --with-clicks false
```

模板预览是样式示意，不运行 Vue/代码动画。最终交付前，需要在真实 Slidev 页面中检查点击状态、图表、公式、交互和导出。普通 PPTX 是图片；`pptx-editable` 需要版本支持，并可能部分回退为图片。相关知识和验收步骤位于 `skills/slidev/`。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖模板应用、正文与 CSS 保留、无效配置、备份恢复、自定义模板、重复应用、覆盖拒绝和符号链接边界。具体运行记录见随包交付的调研与验收说明。
