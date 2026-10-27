---
name: slide-hooks
description: Lifecycle hooks for slide components
---

# Slide Hooks

Lifecycle hooks for slide components.

## Available Hooks

```ts
import { onSlideEnter, onSlideLeave, useIsSlideActive } from '@slidev/client'

const isActive = useIsSlideActive()

onSlideEnter((to, from) => {
  // Called when slide becomes active
})

onSlideLeave((to, from) => {
  // Called when slide becomes inactive
})
```

## Important

Use `onSlideEnter` and `onSlideLeave` for active-slide behavior. Custom Vue components may use normal mount/unmount hooks for resource allocation and cleanup, but mounting does not mean their slide is active.

## Use Cases

- Start/stop animations
- Play/pause media
- Initialize/cleanup resources
- Track analytics
