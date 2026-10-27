# Template Studio

Use to choose a template, configure its settings, create a new deck, restyle a conventional existing deck, or save reusable project presets. Python 3.9+ is enough for the selector and CLI. Node and Slidev are needed to run the generated deck.

## Select a template

`<skill-dir>` means the directory containing this `SKILL.md`, whether installed standalone or bundled in the Slidev Studio plugin.

```bash
python3 <skill-dir>/scripts/studio.py list
python3 <skill-dir>/scripts/studio.py serve /absolute/path/to/talk --no-browser
```

Read the actual printed port and show that localhost URL in the available browser. It has a template gallery, cover/content style previews, title, colors, font style, sizes, spacing, aspect ratio, transition, page-number controls, and local cover-image import. It writes to the project passed at startup, not arbitrary browser-supplied paths. It does not install dependencies or run a public service.

| Preset | Useful for | Character |
| --- | --- | --- |
| `cyan-classroom` | Chinese teaching, course introductions | Dark cover, white content, cyan/blue gradient headings. Inspired by [the user's reference](https://slide.huh.moe/00/1); original local chip illustration, no copied personal details/photos. |
| `minimal-light` | General talks, product explanations | Warm white, green accent, restrained typography. |
| `academic-paper` | Research meetings, papers | Paper background, red headings, serif typography. |
| `terminal-dark` | Code demos, technical talks | Dark canvas, light text, mint accent. |
| `consulting-blue` | Business decisions, status reports | White/navy, left-aligned cover, ruled headings. |
| `editorial-amber` | Humanities, case studies | Cream/amber, serif hierarchy, editorial spacing. |
| `blueprint-lab` | Engineering, architecture | Navy grid, cyan annotations, monospaced headings. |
| `keynote-rose` | Keynotes, launches | Rose/berry, large headings, open poster composition. |

For a prompt such as “make a Chinese teaching deck like this reference,” `cyan-classroom` is a reasonable starting choice. For an existing branded project, inspect its theme first and preserve it unless restyling is requested.

## Direct commands

```bash
# Creates a new destination; refuses an existing directory, including empty ones.
python3 <skill-dir>/scripts/studio.py new ./talk --template cyan-classroom --title "计算机系统导论"

# Changes managed settings, preserves narrative and component code.
python3 <skill-dir>/scripts/studio.py apply ./talk --template academic-paper --set titleSize=40 --set accent=#8d2536

# Reuse the last applied settings when --template is omitted.
python3 <skill-dir>/scripts/studio.py apply ./talk --set aspectRatio=4/3 --set pageNumbers=false
python3 <skill-dir>/scripts/studio.py show ./talk

# Save settings as a project-local reusable template.
python3 <skill-dir>/scripts/studio.py save-template ./talk --id my-course --name "我的课程模板"
python3 <skill-dir>/scripts/studio.py list --project ./talk
python3 <skill-dir>/scripts/studio.py apply ./talk --template my-course

# Restore the preceding file state (also snapshots the current state).
python3 <skill-dir>/scripts/studio.py restore ./talk --backup latest
```

Settings are validated data, not arbitrary CSS or executable templates. The composition control selects classic, briefing, editorial, blueprint or poster heading/cover rules. Older saved presets without that control inherit classic composition. Template selection resets settings to that template's defaults, while retaining the current title. Custom templates live in `slidev-templates/*.json`; copy that folder and referenced cover assets when moving them to another project. The picker can save its current unsaved settings directly as a custom template after a deck exists.

## Managed scope and recoverability

- `slidev-studio.json`: selected preset and validated settings.
- `slides.md`: only selected top-level scalar headmatter (`title`, `aspectRatio`, `transition`, `colorSchema`). The rest of the file, notes, imports, and fences stay intact.
- `styles/index.css`: only a `slidev-studio:begin/end` block is appended or replaced; surrounding CSS stays intact.
- `public/studio/`: original bundled cover art and user-imported images.
- `.slidev-studio/backups/`: timestamped snapshots of the three managed text files. Reapplying identical settings is a no-op. Restore keeps a snapshot of the state it replaces.

The deterministic helper supports the ordinary `slides.md` entry with scalar YAML headmatter and `styles/index.css`. It rejects alternate style entrypoints, complex managed headmatter, broken markers, and managed paths escaping via symlinks. For a more complex existing project, inspect its actual theme/style structure, generate settings and CSS with the module's `css(config)` function, and integrate the stylesheet through its established entrypoint. Do not delete its configuration to make the helper pass.

The helper leaves existing theme layouts/components in place; custom theme selectors can override Studio rules. For an exact visual adaptation, inspect and adjust relevant layouts rather than claiming a template switch guarantees a clone.

## Real-deck acceptance

After selection/settings are applied, install with the project's package manager, start Slidev, and inspect actual content at relevant click states. Check 4:3 separately from 16:9 because available height changes. Verify custom image paths, font availability, gradient contrast, and code color schema. The gallery renders representative HTML with the generated tokens; it does not run Vue, Mermaid, or code animations.

Use [design and story](design-and-story.md), [feature recipes](feature-recipes.md), and [verification and delivery](verification-and-delivery.md) for authoring and acceptance. Stop only the selector process started for this work when it is no longer needed; do not stop unrelated dev servers.
