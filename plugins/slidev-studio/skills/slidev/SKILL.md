---
name: slidev
description: Create, improve, debug, rehearse, and export Slidev presentations using Markdown and Vue; select and configure templates with the local Slidev Studio. Use for Slidev or sli.dev requests, presentation templates, and web slide decks with code, interactive demos, diagrams, or math. Do not select Slidev automatically for unrelated editable PowerPoint requests.
metadata:
  version: "0.3.1"
---

# Slidev

Produce a presentation that communicates clearly, runs in a browser, and survives its intended delivery format. Slidev's advantage is executable explanation: use code, diagrams, math, and interaction where they clarify the subject, rather than adding features to every slide.

## Import a reference deck as a full template

When a user provides a PPT/PPTX/PDF and asks to extract its reusable design, read the bundled [template import skill](../slidev-template-import/SKILL.md). It distills actual layouts, components, assets and verification evidence into a portable full-template library. A saved color/size preset is not equivalent to that bundle. Keep both skills together when installing for another agent.

## Template selection and settings

For choosing, previewing, applying, or saving a template, read [Template Studio](references/template-studio.md). The bundled local picker and CLI support eight presets with adjustable composition, including an Cyan Classroom style inspired by the supplied reference, plus project-local custom presets. Configuration is saved as `slidev-studio.json`, changes are backed up, and existing slide content is retained. Do not force the Cyan Classroom style on unrelated decks.

```bash
python3 <skill-dir>/scripts/studio.py serve /absolute/path/to/talk --no-browser
```

Use the printed localhost URL in the app browser. The picker is a local web interface, not a native settings panel inside Codex. A style preview is not proof of the real deck's rendering; build and inspect the resulting Slidev deck too.

## Start with the actual project and audience

1. Inspect the entry Markdown, package scripts, lockfile, theme, components, layouts, and assets before editing. Keep the existing package manager and visual system. Do not scaffold over an existing deck or upgrade its dependencies as a side effect of a content edit.
2. Infer audience, language, time budget, narrative, reference style, and required output from the request. Ask only for missing facts that materially change the result; otherwise state reasonable assumptions and begin.
3. Distinguish live web presentation, offline presentation, PDF handout, image PPTX, and editable PPTX early. Plan a static explanation for any essential interaction. Read [verification and delivery](references/verification-and-delivery.md) when export, rehearsal, or hosting matters.

## Version and environment check

Use the **installed CLI and its help** as the execution contract. These instructions were researched against official docs on **2026-10-27**; the published CLI then was **53.0.0**, requiring **Node >=22.12.0**. Documentation on the website can describe features absent from a published package.

```bash
node --version
pnpm exec slidev --version
pnpm exec slidev export --help
```

Use `npm exec -- slidev ...` for a project using npm. Bare `npx slidev` outside an installed project can resolve the wrong package; the package is `@slidev/cli`. Check registry version/engines and local help before relying on MCP, editable PPTX, PWA, or a new animation option. Keep the lockfile for reproducibility. See [official docs and version checks](references/official-docs.md).

## Authoring workflow

1. **Structure the argument.** For a new deck, sketch each slide's takeaway, visual evidence, and spoken explanation. A title should convey the point where possible. Put supporting detail and pacing cues in presenter notes. Do not turn an essay into uniformly dense bullet slides.
2. **Establish visual rules.** Use [design and story](references/design-and-story.md) for layout rhythm, typography, code readability, CJK fonts, and static fallbacks. Build a cover and one dense representative slide first, check them in the browser, then apply the system to the rest. Small edits do not need a full redesign.
3. **Choose the explanatory feature.** Use the capability table below. A code evolution merits Magic Move; a relationship merits a diagram; a changing parameter merits a Vue control. Match effects to the talk's pacing, and keep code/examples accurate.
4. **Build a maintainable project.** Use Markdown for narrative, `components/` for behavior, `layouts/` for recurring composition, `styles/` for scoped design rules, `public/` for local assets, and `snippets/` for code. Read [project and extensions](references/project-and-extensions.md) before extending themes or setup hooks.
5. **Verify the deliverable.** Run the build, inspect rendered slides, traverse intended click states, exercise demos, and check the actual export. Fix clipping, missing fonts, render errors, and blank captures. A successful build alone does not establish visual quality. Use the detailed [verification workflow](references/verification-and-delivery.md).
6. **Hand off usable artifacts.** Supply the source project with its assets and lockfile, exact run commands, requested exports, and any material limitations. State which formats and interactions were actually checked. Build or publish a hosted deck only when within the user's requested scope.

## New-deck starter

For a new local project without an existing template, the optional starter provides a consistent, locally styled six-slide deck with code evolution, math/diagram content, an accessible Vue control, static fallback, and presenter notes. It is an example to adapt, not a required look or slide count.

```bash
python3 <skill-dir>/scripts/scaffold.py ./my-talk --title "My talk" --lang zh-CN
cd my-talk
pnpm install
pnpm run dev
pnpm run build
```

Replace `<skill-dir>` with this skill's absolute directory. The scaffold refuses existing destinations, performs no package install, and pins CLI 53.0.0 as a reproducible baseline. `--slidev-version X.Y.Z` selects another verified release. Its English sample copy should be rewritten for the user's language and subject.

## Choose capabilities deliberately

Read only the references relevant to the request. [Feature recipes](references/feature-recipes.md) combines features into complete teaching patterns; the individual references remain the compact syntax lookup.

| Need | Slidev mechanism | Read |
| --- | --- | --- |
| Narrative and navigation | Separators, headmatter/frontmatter, notes, imports, aliases, Toc | [syntax](references/core-syntax.md), [frontmatter](references/core-frontmatter.md), [imports](references/syntax-importing-slides.md), [components](references/core-components.md) |
| Guide attention | `v-click`, `v-after`, `v-switch`, click markers, motion, transitions, rough markers | [animations](references/core-animations.md), [notes markers](references/animation-click-marker.md), [rough markers](references/animation-rough-marker.md), [direction](references/style-direction.md) |
| Explain code | Shiki stages, line numbers, imported regions, Magic Move, TwoSlash | [highlighting](references/code-line-highlighting.md), [snippets](references/code-import-snippet.md), [Magic Move](references/code-magic-move.md), [TwoSlash](references/code-twoslash.md) |
| Live coding | Monaco, diff, runner, file-backed editor | [Monaco](references/editor-monaco.md), [runner](references/editor-monaco-run.md), [file writes](references/editor-monaco-write.md), [recipes](references/feature-recipes.md) |
| Explain a system or derivation | Mermaid, PlantUML, KaTeX with highlight stages | [Mermaid](references/diagram-mermaid.md), [PlantUML](references/diagram-plantuml.md), [math](references/diagram-latex.md) |
| Compose expressive slides | Layout slots, Vue components, UnoCSS, scoped CSS, icons, draggable elements | [layouts](references/core-layouts.md), [slots](references/layout-slots.md), [styles](references/style-scoped.md), [icons](references/style-icons.md), [drag](references/layout-draggable.md) |
| Reuse a design system | Themes, addons, custom layouts, setup hooks, per-slide layers | [extensions](references/project-and-extensions.md), [layers](references/layout-global-layers.md), [global context](references/core-global-context.md) |
| Rich Markdown | Comark, code tabs, YAML block frontmatter | [Comark](references/syntax-comark.md), [code groups](references/code-groups.md), [block frontmatter](references/syntax-block-frontmatter.md) |
| Deliver a talk | Presenter view, notes, timer, drawing, recording, remote control | [delivery](references/verification-and-delivery.md), [timer](references/presenter-timer.md), [drawing](references/animation-drawing.md), [recording](references/presenter-recording.md), [remote](references/presenter-remote.md) |
| Share and preserve | SPA, PDF, PNG, image or editable PPTX, downloads, SEO, offline cache | [export](references/core-exporting.md), [hosting](references/core-hosting.md), [offline](references/offline-and-pwa.md), [SEO](references/build-seo-meta.md) |
| Agent-assisted editing | Built-in HTTP/stdio MCP; available tool discovery | [MCP](references/tool-mcp.md) |

For niche setup options, the remaining syntax references and authoritative page map are in [official docs](references/official-docs.md). Do not load the full documentation bundle by default.

## Non-obvious correctness rules

- `---` can delimit both slides and YAML. Never reorder or split a deck with `text.split('---')`; it corrupts frontmatter, fences, or imported slides. Prefer available Slidev MCP slide operations, or context-aware source edits.
- Relative click positions are **strings**: `v-click="'+1'"`. `v-click="+1"` is numeric absolute click 1. A visibility range `[2,5]` ends **before** click 5.
- `v-clicks` is a component (`<v-clicks>`), not a directive. Keep blank lines around Markdown lists inside Vue wrappers.
- Code options use separate groups: `` ```ts {1|2|all}{lines:true} ``. Magic Move needs a four-backtick outer fence around triple-backtick code steps.
- Styles in a slide are scoped. Project CSS should normally live under `.slidev-layout` so it does not restyle the presenter UI. Prefer `slide-bottom.vue` for a per-slide footer using `$page`; a global layer using current navigation state can export the wrong number.
- Use public imports from `@slidev/client` / `@slidev/types`; refs from composables need `.value` in script. Use slide enter/leave hooks for active-slide work, and ordinary component cleanup for resources allocated by custom components.
- Rendered Markdown export is an image-based document, not recovery of editable `slides.md`. `pptx` and `pptx-editable` have different limits; verify support and inspect output before promising editability.
- File-backed Monaco writes source files in development. PlantUML normally contacts a server. Live embeds and CDN assets need a network. Choose these deliberately and provide local/static alternatives when delivery requires them.
