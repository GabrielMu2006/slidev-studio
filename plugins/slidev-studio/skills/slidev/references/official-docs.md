# Official docs, version checks, and reference map

Research date: **2026-10-27**. npm `@slidev/cli` and the official latest release were **53.0.0**; package engines require **Node >=22.12.0**. Tested baseline: CLI 53.0.0 and default theme 0.25.0. Use the installed CLI as authority for an existing deck.

The original syntax references were retained from the [official Slidev skill](https://github.com/slidevjs/slidev/tree/main/skills/slidev), distributed under MIT. This local extension adds production workflows, explanatory recipes, validation guidance, and a runnable starter. It is not an automatically synced upstream mirror.

## Check rather than guess

```bash
node --version
pnpm exec slidev --version
pnpm exec slidev build --help
pnpm exec slidev export --help
# For a new project or a requested update, query current release metadata:
npm view @slidev/cli version engines --json
```

Keep project-local CLI/package manager and the lockfile. Do not update globally or reinstall the upstream skill over this local customization as routine maintenance. Reconcile upstream changes deliberately.

Official [llms.txt](https://sli.dev/llms.txt) indexes Markdown docs; individual pages support `.md`, e.g. `https://sli.dev/guide/exporting.md`. [llms-full.txt](https://sli.dev/llms-full.txt) is useful for a broad documentation audit, not necessary context for every deck. Check [releases](https://github.com/slidevjs/slidev/releases) and installed types when the docs and runtime disagree.

In the verified 53.0.0 package, export help includes `pptx-editable`, config types include `pwa`, and the CLI exposes MCP. The Monaco setup page uses `ata` in one example while installed config types use `cdn`; prefer the installed `'cdn' | 'local' | 'none'` contract for this release. Remote asset bundling is **off by default** in the published parser even where a feature page describes caching automatically.

## Official navigation

| Task | Primary pages |
| --- | --- |
| Understand Slidev/start a project | [why](https://sli.dev/guide/why), [start](https://sli.dev/guide), [syntax](https://sli.dev/guide/syntax), [FAQ](https://sli.dev/guide/faq) |
| Present and rehearse | [UI](https://sli.dev/guide/ui), [animations](https://sli.dev/guide/animations), [recording](https://sli.dev/features/recording), [remote](https://sli.dev/features/remote-access) |
| Discover built-ins | [features](https://sli.dev/features), [components](https://sli.dev/builtin/components), [layouts](https://sli.dev/builtin/layouts), [configuration](https://sli.dev/custom/) |
| Code teaching | [highlighter](https://sli.dev/custom/config-highlighter), [Magic Move](https://sli.dev/features/shiki-magic-move), [TwoSlash](https://sli.dev/features/twoslash), [Monaco](https://sli.dev/custom/config-monaco), [runners](https://sli.dev/custom/config-code-runners) |
| Diagrams and math | [Mermaid](https://sli.dev/features/mermaid), [Mermaid setup](https://sli.dev/custom/config-mermaid), [renderer](https://sli.dev/custom/config-mermaid-renderer), [KaTeX](https://sli.dev/custom/config-katex), [PlantUML](https://sli.dev/features/plantuml) |
| Project/style extension | [directories](https://sli.dev/custom/directory-structure), [Vue](https://sli.dev/custom/config-vue), [Vite](https://sli.dev/custom/config-vite), [UnoCSS](https://sli.dev/custom/config-unocss), [fonts](https://sli.dev/custom/config-fonts) |
| Advanced integration | [global context](https://sli.dev/guide/global-context), [parser](https://sli.dev/custom/config-parser), [transformers](https://sli.dev/custom/config-transformers), [routes](https://sli.dev/custom/config-routes), [shortcuts](https://sli.dev/custom/config-shortcuts), [context menu](https://sli.dev/custom/config-context-menu) |
| Distribution | [CLI](https://sli.dev/builtin/cli), [export](https://sli.dev/guide/exporting), [hosting](https://sli.dev/guide/hosting), [PWA](https://sli.dev/features/pwa) |
| AI and editor integration | [AI workflow](https://sli.dev/guide/work-with-ai), [MCP](https://sli.dev/features/mcp), [VS Code](https://sli.dev/features/vscode-extension) |
| Visual and reusable resources | [showcases](https://sli.dev/resources/showcases), [themes](https://sli.dev/resources/theme-gallery), [addons](https://sli.dev/resources/addon-gallery), [covers](https://sli.dev/resources/covers) |

## Additional local lookups

These focused references supplement the capability table in `SKILL.md`:

- Configuration: [headmatter](core-headmatter.md), [frontmatter merge](syntax-frontmatter-merging.md).
- Code density: [line numbers](code-line-numbers.md), [scrolling](code-max-height.md).
- Canvas: [dimensions](layout-canvas-size.md), [zoom](layout-zoom.md), [Transform](layout-transform.md).
- Build: [PDF download](build-pdf.md), [remote assets](build-remote-assets.md), [OG image](build-og-image.md), [SEO](build-seo-meta.md).
- Presenter: [ruby notes](presenter-notes-ruby.md), [direction variants](style-direction.md).
- Authoring tools: [side editor](editor-side.md), [VS Code](editor-vscode.md), [Prettier](editor-prettier.md), [eject theme](tool-eject-theme.md).
- Runtime: [slide hooks](api-slide-hooks.md).

When changing syntax references, check their linked official page and an actual small deck. Keep observed compatibility issues separate from general guidance; do not turn one failed example into a blanket ban on the feature.
