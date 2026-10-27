# Verification and delivery

Use for build/run acceptance, visual inspection, export, rehearsal, and hosting. Scale checks to the change and requested formats.

## Build and inspect

Use the project's scripts. For the starter or a conventional pnpm project:

```bash
pnpm run dev --port 3030
pnpm run build
```

For npm, add the argument separator: `npm run dev -- --port 3030`. Read startup output for the actual port. A ready message is not a successful rendering check.

Inspect the canvas in a browser at presentation size (e.g. a 1440×900 window), then a smaller window for controls. Slidev scales a fixed canvas; treating it as a scrolling responsive webpage gives the wrong layout.

- For edits, inspect every changed slide and relevant click states. For a new deck, review all slides as a contact sheet and inspect dense/interactive slides full-size.
- Traverse clicks forward and backward: code highlights, Magic Move, formula stages, overlays, notes markers. URLs such as `/3?clicks=2` help inspect a state; verify installed router behavior.
- Exercise actual controls: edit/run Monaco, change/reset a Vue parameter, revisit the slide, pause media. Check console errors, broken assets/fonts, and clipped labels.
- DOM measurements flag overflow, not composition quality. Intentional backgrounds may extend outside the canvas; visible text must not. Look at screenshots.
- Check `/presenter` for notes/timing and `/overview` for visual rhythm when relevant.

## Choose the output

| Output | Preserves | Limit |
| --- | --- | --- |
| Built SPA | Vue, Monaco, navigation, code animations | Requires HTTP(S) serving; network dependencies remain. |
| PDF | Fixed handout, selectable browser text where supported | No live controls; choose click-state handling. |
| PNG | Faithful rendered image | No selectable text or interaction. |
| `pptx` | Visual fidelity, notes | Images per slide. Current docs include click steps by default. |
| `pptx-editable` | Native text/shapes where supported, notes | Version-gated; SVG, math, canvas, video, iframe, gradients/effects may remain pictures. Individual slides can fall back. Fonts are referenced, not embedded. |
| `md` export | Markdown containing rendered slide images | Not editable source; deliver original Markdown separately. |

Inspect editable PPTX logs for fallbacks and referenced fonts. Open/render the actual file with an available presentation tool and confirm native text where requested. A valid ZIP is not proof of PowerPoint layout fidelity.

## CLI export

```bash
pnpm add -D playwright-chromium
pnpm exec slidev export slides.md --output handout.pdf --with-clicks false
pnpm exec slidev export slides.md --format png --output slide-images
pnpm exec slidev export slides.md --format pptx --with-clicks false
# Only when the installed export --help supports it:
pnpm exec slidev export slides.md --format pptx-editable --with-clicks false
```

Install the browser binary if missing. An existing compatible Chrome/Edge can be supplied via `--executable-path /absolute/path/to/browser`; the Playwright package is still required. Check skipped install scripts or browser downloads before retrying.

Pass `--with-clicks` when intermediate states belong in the handout, or explicit `--with-clicks false` for one page per logical slide. Defaults differ by format. Check local help for `--range`, `--wait`, `--timeout`, `--wait-until`, `--with-toc`, and `--per-slide`; do not combine per-slide with editable PPTX when unsupported.

Inspect actual pages for blank frames, footer errors, missing formulas/assets, clipped code, and invisible final text. Compare page count against rendered slides plus requested stages. Confirm PPTX notes when needed. Supply notes separately if the PDF export does not include them. Browser-only workflows can use `/export`, followed by the same inspection.

## Diagnose by symptom

| Symptom | Investigate |
| --- | --- |
| CLI fails before serving | Node engine, lockfile install, theme/addon dependency, entry path |
| Blank slide | Vue errors, malformed YAML/fences, disabled slide, remote content |
| Missing dynamic content in export | Stable state, render context, animation completion, asset/font readiness |
| Export stalls | External services/fonts, live connections preventing `networkidle`; diagnose before changing wait options |
| Wrong footer everywhere | Global current-page state; use a per-slide layer with `$page` |
| Broken under a URL prefix | Build `--base`, computed URLs, deep-route rewrites |
| Bad math/diagrams | KaTeX command support, Mermaid version, label size, renderer config |
| Stale built deck | Service worker/browser cache; recheck the current build |
| `Failed to patch FloatingVue` | Observed with CLI 53.0.0, `@shikijs/vitepress-twoslash` 4.5.0 and `floating-vue` 5.4.0. A caught upstream hover-patch error; check tooltips separately and record it. Disabling TwoSlash headmatter does not prevent this always-installed client plugin. Do not hide console errors or call exports pristine merely because rendering succeeds. |

Longer timeouts do not fix invalid URLs or broken components. An exit code of zero still requires a visual check.

## Rehearse and share

Use the talk's actual `duration` and `timer`. Check notes, next previews, drawing persistence, and demo recovery. If recording is requested, check permissions, codec, and a short playback sample. Do not activate microphone/camera or a public tunnel merely for verification.

For a URL prefix, build with `pnpm exec slidev build --base /talks/demo/`. Serve and reload a deep route; configure rewrites or `routerMode: hash` for hosts without them. `--without-notes` removes notes from a public build; hiding presenter UI alone does not. `--download` generates a PDF and needs working export dependencies. Publish only within the requested scope.

Read [offline](offline-and-pwa.md) when needed. Hand off source, assets, package metadata/lockfile, commands, and requested exports. State tested version and formats plus any unverified recipient-specific fonts or PowerPoint rendering.

Sources: [CLI](https://sli.dev/builtin/cli), [export](https://sli.dev/guide/exporting), [hosting](https://sli.dev/guide/hosting), [UI](https://sli.dev/guide/ui).
