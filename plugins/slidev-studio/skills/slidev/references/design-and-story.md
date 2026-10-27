# Design and story

Use when creating or improving the communication and visual quality of a deck. These are starting heuristics, not a mandatory template.

## Shape the explanation

- Identify what the audience should understand or decide at the end, then order the evidence that gets them there. Introduce the problem before the mechanism and the mechanism before implementation detail.
- Give each slide one dominant purpose: claim, comparison, diagram, example, derivation, interaction, or conclusion. Choose the composition accordingly. “Caching removes the repeated fetch” communicates more than “Architecture”.
- Keep the slide readable without the transcript. Put background detail, transitions, source links, and demo instructions in the final HTML comment for notes.
- Match slide count and click count to the time budget; a live demo needs rehearsal time and a recovery path.
- Preserve citations, units, denominators, dates, and uncertainty for data. Do not invent benchmark improvements or imply demo values are measurements.

## Establish a visual system

Respect a supplied brand or existing theme. Otherwise choose a suitable type hierarchy, restrained palette, spacing scale, and a small set of recurring compositions. Themes supply layout and CSS; the author still controls hierarchy and density.

For a 980 px wide, 16:9 canvas, initial ranges might be titles around 36–52 px, body around 22–28 px, and code around 18–22 px. These are canvas units, not pixels on a scaled browser window. Judge from a full-slide screenshot. Large tables and long code should become focused excerpts or multiple slides before shrinking text or applying `zoom`.

Use layout rhythm: claim, diagram, code, and comparison slides can share tokens without sharing the same grid. Put the main idea at the strongest visual position. Avoid repeated decorative cards that add no structure.

## Compose with Slidev

- Use `two-cols-header` for a shared title over code/explanation, `image-left/right` for a real visual paired with text, and `full` or a custom layout for a simulation. Check theme-specific props rather than assuming they are universal.
- Scope project CSS under `.slidev-layout` so it does not restyle the presenter UI. Slide-local `<style>` is already scoped. Reserve absolute positioning and dragging for intentional overlays.
- Use per-slide layers for elements that need each slide's `$page` or frontmatter. A global layer is one persistent instance, not one per exported page.
- Keep code lines short for their column. Import meaningful regions with `<<< @/snippets/file.ts#region`. Highlight a few lines per explanatory stage. Scrolling code is useful live, but hides content in a handout.
- Prefer a labelled diagram for system relationships. Simplify graphs before scaling labels down.
- Use local assets for essential evidence; a random remote cover photo should not carry the explanation.

## Fonts and Chinese content

For a local/offline deck, set `fonts.provider: none` and use available fonts with explicit CJK fallbacks, such as `PingFang SC`, `Microsoft YaHei`, `Noto Sans CJK SC`, then `sans-serif`. Code comments may also need a CJK fallback. A font-family declaration does not install the font on the recipient's machine.

For reproducible cross-machine output, bundle permitted WOFF2 files in `public/fonts/`, declare `@font-face`, and verify actual font loading before capture. Check Chinese punctuation, mixed Latin/CJK baselines, awkward wraps, formula glyphs, and code comments. Avoid forced letter spacing and uppercase treatment on Chinese body text.

Read [font configuration](https://sli.dev/custom/config-fonts) for providers, weights, local families, and fallback behavior.

## Interaction and motion should explain something

Give controls accessible labels and visible values. Make the changed result explicit, with units and assumptions. A component can use HTML/SVG, browser APIs, or a locally installed chart library; another presentation engine is not needed.

Advance code and notes together. Prefer deliberate steps over revealing every word. Test backward navigation. Use slide lifecycle hooks to pause media and animation when inactive. Respect reduced motion for custom CSS; motion should not be needed to read the final result.

For static delivery, add a meaningful sample state, code result, diagram, or screenshot. `RenderWhen` distinguishes `print` and `slide` contexts, but inspect the specific export: some exports visit slides individually. Do not assume “print” covers every output route.

## Review questions

Can the audience identify the point within a few seconds? Are labels and code readable at presentation size? Does the final click state contain the takeaway? Can a recipient understand the PDF without running the demo? Are notes and sources available where expected? Revise the slide whose answer is weakest.
