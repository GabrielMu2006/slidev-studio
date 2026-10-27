# Full template bundle, schema 1

```text
my-template/
  template.json
  design.md
  preview.png
  scaffold/
    slides.md
    package.json
    layouts/*.vue
    components/             optional
    styles/index.css
    public/                 retained/generated assets
  reference/
    source.pptx             or source.pdf
    analysis.json
    renders/*.png
  verification/
    report.md
    *.png                   checked rendered template pages
```

Example manifest (values must describe the actual reference and checks):

```json
{
  "schemaVersion": 1,
  "kind": "slidev-template",
  "id": "my-template",
  "name": "My template",
  "version": "1.0.0",
  "status": "verified",
  "description": "A reusable design distilled from the supplied deck",
  "aspectRatio": "16/9",
  "layouts": [{"name": "cover", "sourceSlides": [1]}],
  "source": "reference/source.pptx",
  "verification": {
    "build": "passed",
    "visual": "passed",
    "sourceSlides": [1],
    "renderedSlides": [1],
    "report": "verification/report.md"
  }
}
```

IDs are lowercase kebab-case. Template versions use stable `MAJOR.MINOR.PATCH`. Paths are relative, slash-separated and cannot escape the package; symlinks, runtime dependencies, environment files and embedded Git checkouts are rejected. Dependencies belong in `package.json` and a lockfile, not `node_modules/`. The scaffold is executable code, so inspect imported third-party templates before running them. Installation does not execute it.

The library stores `<id>/<version>/` packages with content hashes. Updating a template means publishing a new template version; this is independent of the plugin release version. Plugin releases bundle tools and skills, never automatically include private user libraries.

For PDF/image-only sources, the agent must reconstruct layouts from rendered evidence and record that limitation. XML style fields are sometimes inherited from masters or layouts, so the visual result remains the authority.
