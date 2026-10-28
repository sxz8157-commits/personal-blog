<template>
  <div
    class="startup-loading"
    :class="{ 'startup-loading--ready': ready }"
    role="status"
    aria-live="polite"
    aria-atomic="true"
  >
    <div class="startup-loading__content">
      <div class="startup-loading__brand">
        <span class="startup-loading__brand-mark" aria-hidden="true"></span>
        <span>{{ brand }}</span>
      </div>
      <h1 class="startup-loading__title">正在准备页面</h1>
      <p class="startup-loading__message">{{ message }}</p>
      <div
        class="startup-loading__progress"
        role="progressbar"
        aria-label="页面加载"
        :aria-valuetext="message"
      >
        <span class="startup-loading__progress-fill"></span>
      </div>
      <p class="startup-loading__hint">准备就绪后将自动进入</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  brand: {
    type: String,
    default: '沛心的博客'
  },
  message: {
    type: String,
    default: '正在加载背景与页面内容…'
  },
  ready: {
    type: Boolean,
    default: false
  }
})
</script>

<style>
@import '../styles/startup-loading.css';
</style>
