# Project structure and extension choices

Use for reusable decks, custom layouts/components, themes/addons, and setup hooks. Keep simple decks simple.

## Conventions

```text
slides.md                 entry, headmatter, content and notes
pages/                    optional imported sections via src:
snippets/                 real code, optionally with named regions
components/               auto-imported Vue components
layouts/                  custom layouts with <slot /> and named slots
styles/index.css          project styles (or style.css)
public/                   static assets, referenced as /asset.svg
setup/                    documented setup hooks
slide-bottom.vue          one instance per slide, good for page-aware footers
global-top.vue            one persistent overlay
vite.config.ts            extend Vite without replacing Slidev's integration
uno.config.ts             UnoCSS rules, shortcuts, icon safelist
package.json + lockfile   reproducible local tooling
```

`@/` denotes the project root for snippet imports. Assets in `public/` use a leading slash. For asset URLs computed in Vue, account for `import.meta.env.BASE_URL` when deploying under a prefix; verify the actual built URL. Do not overwrite existing config to apply an example.

Imported slides are edited in their source files. Importing-entry frontmatter overrides matching imported fields. Rendered numbers can differ from local source order because of imports or disabled slides; inspect the rendered deck or MCP result before addressing by number.

## Theme, addon, layout, or component?

| Change | Extension |
| --- | --- |
| Apply an established visual identity | Inspect a compatible theme from the [gallery](https://sli.dev/resources/theme-gallery), then install its package explicitly. |
| Reuse behavior across decks | Inspect or author an addon and its dependencies. |
| Repeat a composition | Create a local layout. |
| Add a demo, chart, or control | Create a Vue component. |
| Refine one slide | Local Markdown/HTML and scoped styles. |
| Deeply customize an installed theme | Eject locally; edit the copy and preserve attribution. |

A new theme is optional. Examine representative screenshots and actual layout props rather than choosing by name. [Showcases](https://sli.dev/resources/showcases) help with direction; they do not authorize copying a talk's assets.

## Setup hooks and runtime boundaries

Read the current official page and installed types before implementing a hook. Entry points are version-dependent.

| File | Helper from `@slidev/types` | Purpose |
| --- | --- | --- |
| `setup/shiki.ts` | `defineShikiSetup` | Code languages, themes, transformers |
| `setup/monaco.ts` | `defineMonacoSetup` | Browser editor options |
| `setup/code-runners.ts` | `defineCodeRunnersSetup` | Additional language runtimes |
| `setup/katex.ts` | `defineKatexSetup` | Math macros/options |
| `setup/mermaid.ts` | `defineMermaidSetup` | Diagram configuration |
| `setup/mermaid-renderer.ts` | `defineMermaidRendererSetup` | Optional replacement renderer |
| `setup/main.ts` | `defineAppSetup` | Vue app registration/plugins |
| `setup/routes.ts` | `defineRoutesSetup` | Additional routes |
| `setup/shortcuts.ts` | `defineShortcutsSetup` | Keyboard controls |
| `setup/context-menu.ts` | `defineContextMenuSetup` | Context menu |

Vite/highlighting/KaTeX setup can run in Node; Vue/Monaco/runners and renderers run in the browser. Check the environment annotation on each official page; do not import Node-only packages in client hooks. For Markdown rewriting, read [pre-parser](https://sli.dev/custom/config-parser) and [transformers](https://sli.dev/custom/config-transformers); avoid naive separator splitting.

## Vue context and lifecycle

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useNav, useSlideContext } from '@slidev/client'

const { currentPage } = useNav()
const { $slidev } = useSlideContext()
const atStart = computed(() => currentPage.value === 1)
</script>

<template>
  <span>{{ $slidev.configs.title }} · {{ atStart ? 'Start' : 'Continue' }}</span>
</template>
```

Templates unwrap refs; script needs `.value`. Calling `useSlideContext` disables automatic `$slidev` injection in that file, so destructure what you use. Use public composables, not internal `@slidev/client/logic/...` modules.

Use `onSlideEnter`, `onSlideLeave`, or `useIsSlideActive` for activity-sensitive work. Custom components may mount early or stay mounted after leaving. Clean up resources on component unmount as well as slide deactivation where relevant. A per-slide footer should use local `$page`, not global current page in a print-all view.

Sources: [directories](https://sli.dev/custom/directory-structure), [customization](https://sli.dev/custom/), [layouts](https://sli.dev/guide/write-layout), [themes](https://sli.dev/guide/write-theme), [addons](https://sli.dev/guide/write-addon), [context](https://sli.dev/guide/global-context).
