<script setup lang="ts">
import { computed, ref, useId } from 'vue'

const inputId = useId()
const hitRate = ref(80)
const latency = computed(() => hitRate.value / 100 * 8 + (1 - hitRate.value / 100) * 120)
</script>

<template>
  <section class="latency-demo" aria-label="Illustrative cache latency model">
    <div class="demo-controls">
      <label :for="inputId">Cache hit rate <strong>{{ hitRate }}%</strong></label>
      <input :id="inputId" v-model.number="hitRate" type="range" min="0" max="100" step="1" :aria-valuetext="`${hitRate} percent`">
      <p>Hit: 8 ms · Miss: 120 ms</p>
      <button type="button" @click="hitRate = 80">Reset to 80%</button>
    </div>
    <div class="demo-output" role="status" aria-live="polite">
      <span>Illustrative mean latency</span>
      <strong>{{ latency.toFixed(1) }} <small>ms</small></strong>
      <div class="latency-track" aria-hidden="true"><div :style="{ width: `${latency / 120 * 100}%` }"></div></div>
      <p>{{ hitRate }}% × 8 + {{ 100 - hitRate }}% × 120</p>
    </div>
  </section>
</template>

<style scoped>
.latency-demo { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; margin-top: 36px; padding: 30px; border: 1px solid #c8d6d0; background: #f0f5f1; border-radius: 8px; }
.demo-controls label { display: block; font-size: 23px; }
.demo-controls label strong { float: right; color: #126a58; }
input { display: block; width: 100%; margin: 26px 0 16px; accent-color: #126a58; }
input:focus-visible, button:focus-visible { outline: 3px solid #126a58; outline-offset: 4px; }
p, .demo-output > span { font-size: 17px; color: #52605a; }
button { margin-top: 18px; padding: 8px 14px; border: 1px solid #126a58; border-radius: 4px; color: #126a58; font-size: 17px; background: white; cursor: pointer; }
.demo-output > strong { display: block; margin: 10px 0 16px; font-size: 62px; line-height: 1.1; color: #126a58; font-variant-numeric: tabular-nums; }
small { font-size: 24px; font-weight: 500; }
.latency-track { height: 10px; background: #d8e3dc; border-radius: 5px; overflow: hidden; }
.latency-track > div { height: 100%; background: #126a58; }
</style>
