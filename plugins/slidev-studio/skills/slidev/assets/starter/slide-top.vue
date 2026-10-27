<template>
  <footer v-if="$page > 1" class="talk-footer">
    <span>{{ $slidev.configs.title }}</span>
    <span>{{ $page }} / <SlidesTotal /></span>
  </footer>
</template>

<style scoped>
.talk-footer { position: absolute; bottom: 18px; left: 52px; right: 52px; display: flex; justify-content: space-between; gap: 24px; font-size: 13px; color: #59665f; pointer-events: none; }
.talk-footer > span:first-child { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.talk-footer > span:last-child { flex-shrink: 0; }
</style>
