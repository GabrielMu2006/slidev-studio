---
name: remote-assets
description: Bundle remote images and assets for offline use
---

# Bundle Remote Assets

In the verified 53.0.0 parser, `remoteAssets` defaults to `false`. Enable supported remote asset bundling deliberately:

```yaml
---
remoteAssets: build
---
```

Check emitted assets; remote iframes, APIs, fonts and scripts are not made offline automatically.

## Remote Images

```md
![Remote Image](https://sli.dev/favicon.png)
```

When enabled, handled by vite-plugin-remote-assets.

## Local Images

Place in `public/` folder and reference with leading slash:

```md
![Local Image](/pic.png)
```

Do NOT use relative paths like `./pic.png`.

## Custom Styling

Convert to img tag for custom sizes/styles:

```html
<img src="/pic.png" class="m-40 h-40 rounded shadow" />
```
