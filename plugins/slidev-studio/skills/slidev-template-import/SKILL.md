---
name: slidev-template-import
description: Extract a reusable full Slidev template from a user-provided PowerPoint, PDF, or rendered presentation reference. Use when the user gives a PPT/PPTX and asks to learn its design, import it as a template, or make future Slidev decks in that style. Produces layouts, components, styles, assets and a validated template bundle, rather than only color presets or background screenshots.
metadata:
  version: "0.2.1"
---

# Import a full Slidev template

Let the agent interpret the design; use deterministic helpers for inspection, packaging and reuse. Work on copies. A successful extraction of XML is not a successful visual adaptation.

## Inspect the actual reference

1. Resolve the supplied file. For legacy `.ppt`, convert a copy to `.pptx` using an available office converter. For `.pptx`, run `python3 <this-skill>/scripts/inspect_pptx.py reference.pptx --out ./reference-analysis --render`.
2. The helper retains the source, extracts slide order, dimensions, text/style information, theme/master/layout XML and media, and optionally renders PDF/PNGs using local LibreOffice and Poppler. It does not call an LLM or a remote service. Rendering tools are optional dependencies; use the host's presentation renderer if unavailable. Do not claim visual inspection from XML alone.
3. Inspect all source pages as a contact sheet, then representative pages at full size. For PDF references, render pages with a local PDF tool and record that editable object information is unavailable. If rendering fails, fix the renderer or obtain usable rendered references; do not mark the template verified without seeing them.
4. Identify composition families from evidence: cover, section, ordinary content, columns, image/text, table/chart, closing, plus distinctive layouts actually present. Record margins, hierarchy, font fallback, palette, decorations, image crops, notes/footer behavior and source slide numbers. Preserve the reference's actual aspect ratio. Do not force every source into a fixed list of layouts.

## Distill and implement

Create a package outside the plugin cache:

```bash
python3 <this-skill>/scripts/template_bundle.py init ./my-template --id my-template --name "My template" --analysis ./reference-analysis
```

Read [bundle format](references/bundle-format.md), then fill the draft:

- Write `design.md`: design rules, source-page-to-layout mapping, editable vs raster elements, font requirements and deviations. Remove original presentation-specific wording from reusable sample content.
- Build a complete runnable Slidev project in `scaffold/`: `slides.md`, `package.json`, reusable `layouts/`, any `components/`, scoped `styles/`, `public/` assets and needed setup. Use generic example content demonstrating every retained layout.
- Use native Markdown/Vue/CSS/SVG for text and structure. Do not flatten whole source slides into background images and call that an editable template. Keep genuinely image-based illustrations as assets. Agent-generated layout code belongs in the bundle, not the installed plugin.
- Retain the exact source and analysis under `reference/` for later fidelity checks. Font files need not be bundled if unavailable; record the actual fallback and verify it. Keep private reference files in the user's local library unless they explicitly request sharing them.
- Set `layouts` in `template.json` to the actual layout names and source slide numbers. Use the Slidev authoring skill bundled alongside this skill for code, math, interactions and export details; when installed individually, keep both skills together.

## Validate before registering

1. Install scaffold dependencies with its package manager and run the build. Inspect actual Slidev pages and relevant clicks. Compare representative pages against the reference at the same aspect ratio; check titles, margins, footers, table density, image crops and fonts.
2. Save a representative rendered PNG as `preview.png` and checked comparison images in `verification/`. Record exact commands, results, inspected slide numbers, source slide numbers and any differences in `verification/report.md`. Both build and visual checks must describe real work, not a guessed success.
3. Set `verification.build` and `verification.visual` to `"passed"` only after those checks; set `status` to `"verified"`. Structural validation checks the evidence and scaffold, but cannot prove the honesty or quality of agent visual judgment.
4. Move generated `node_modules/`, `dist/` and `.slidev/` directories outside the bundle after verification; keep the dependency manifest and lockfile. Packages reject runtime caches and private environment files. Run `python3 <this-skill>/scripts/template_bundle.py validate ./my-template --verified`, then `install ./my-template --library ./slidev-template-library`. Failed checks leave the package a draft; fix the artifact and retry.

## Reuse, import and share

```bash
python3 <this-skill>/scripts/template_bundle.py list --library ./slidev-template-library
python3 <this-skill>/scripts/template_bundle.py instantiate my-template --library ./slidev-template-library --out ./new-talk
python3 <this-skill>/scripts/template_bundle.py export ./my-template --out ./my-template.zip
python3 <this-skill>/scripts/template_bundle.py install ./my-template.zip --library ./another-library
```

`install` registers the whole package including layouts and assets. `instantiate` copies the scaffold into a new destination and records its version/hash. Existing destinations are refused. To restyle an existing deck, inspect its structure and integrate layouts deliberately; never replace its narrative with the template's sample slides.

Template versions are immutable in a library: identical reinstallation is a no-op; changed content needs a new template version. Keep user libraries and projects outside plugin caches so plugin/skill updates cannot erase them. ZIP export includes retained references; share it only when the user requested sharing that source.

The local visual picker manages lightweight style presets. Full agent-built templates are selected through this workflow and its library commands; do not describe a preset JSON as a complete template.
