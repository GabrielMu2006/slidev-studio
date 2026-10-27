# Offline presentation and PWA

Use when internet may be unavailable. A local Slidev server or locally served build can already work offline if dependencies and assets are local; PWA caching is an additional delivery option.

## Remove network assumptions

- Keep essential images, video/posters, diagram assets, and permitted fonts local. Use `fonts.provider: none` for local fonts; declaring a family does not install it.
- Remote image bundling does not make iframes, API calls, PlantUML servers, or CDN scripts work offline. Verify emitted assets and browser requests.
- Prefer locally bundled Monaco types. Provide local demos/static evidence for required external services.
- Serve the build with its correct base URL. Opening `dist/index.html` via `file://` is unreliable.

## Version-gate PWA support

The official [PWA guide](https://sli.dev/features/pwa) describes `pwa: build`/`true` and the optional peer `vite-plugin-pwa`. Verify installed config types and build behavior before enabling it; website docs may be ahead of npm. Do not enable it on every deck.

When supported and useful:

```bash
pnpm add -D vite-plugin-pwa
```

```yaml
---
pwa: build
fonts:
  provider: none
---
```

Build and serve on HTTPS or localhost. On a fresh browser profile, wait for precaching, disconnect network, reload, and visit every required slide. Exercise media and controls at the actual base URL. External assets are not precached simply because a service worker exists; large media and seeking need separate checks.

Report whether offline behavior was actually tested and what still needs a network. If the release lacks PWA, deliver a locally served asset-complete deck rather than promising cache persistence.
