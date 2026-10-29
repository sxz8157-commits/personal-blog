<template>
  <Teleport to="body">
    <div v-show="!hidden && !editing && !(compactViewport && playAreaVisible)" ref="dock" class="interactive-dock" :class="{ 'is-dragging': dragging, 'is-settling': settling, 'is-collapsed': collapsed, 'is-right': alignRight, 'is-near-top': nearTop }" :style="style" @pointerdown="begin" @click.capture="guardClick" @keydown="keydown" @keydown.esc="menuOpen = false" aria-label="可拖动的音乐与壁纸控件">
      <button class="mini-record" type="button" :class="{ 'is-playing': playing }" :disabled="audioBusy && !collapsed" :aria-label="collapsed ? '展开互动控件' : playing ? '暂停音乐' : '播放音乐'" :title="collapsed ? '展开互动控件' : playing ? `暂停：${track}` : '点一下听音乐，也可以拖动'" @click="collapsed ? collapsed = false : $emit('toggle-play')">
        <span class="record-disc" aria-hidden="true"><span class="record-label"><svg viewBox="0 0 24 24"><path d="M9 17V6l10-2v11M9 8l10-2"/><circle cx="6" cy="17" r="3"/><circle cx="16" cy="15" r="3"/></svg></span></span>
        <span v-if="audioBusy" class="record-loading" aria-hidden="true"></span>
      </button>
      <button v-if="!collapsed" class="wallpaper-switch" type="button" :disabled="backgroundBusy" aria-label="切换壁纸" :title="backgroundBusy ? '正在准备下一张壁纸' : '换个背景，也可以拖动'" @click="$emit('next-background')"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="4"/><circle cx="8" cy="9" r="1.5"/><path d="m4 17 5-5 4 4 3-3 4 4"/></svg><span v-if="backgroundBusy" class="wallpaper-dot" aria-hidden="true"></span></button>
      <button v-if="!collapsed" type="button" class="dock-reset" data-no-drag aria-label="互动控件选项" :aria-expanded="menuOpen" title="复位或收起" @click="menuOpen = !menuOpen">⋮</button>
      <div v-if="menuOpen && !collapsed" class="dock-options" data-no-drag><button type="button" @click="reset(); menuOpen = false">复位位置</button><button type="button" @click="collapsed = true; menuOpen = false">收起控件</button></div>
      <p v-if="feedback" class="dock-feedback" role="status">{{ feedback }}</p>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { usePointerDrag } from '@/composables/usePointerDrag'
defineProps({ playing: Boolean, audioBusy: Boolean, backgroundBusy: Boolean, playAreaVisible: Boolean, hidden: Boolean, track: { type: String, default: '' }, feedback: { type: String, default: '' } })
defineEmits(['toggle-play', 'next-background'])
const dock = ref(null)
const editing = ref(false)
const compactViewport = ref(window.innerWidth <= 768)
const collapsed = ref(false), menuOpen = ref(false)
const { point, style, dragging, settling, begin, guardClick, keydown, reset } = usePointerDrag(dock, { snap: 'edge', storageKey: 'peixin-interactive-dock-v1', initial: bounds => ({ x: bounds.left, y: Math.max(bounds.top, bounds.bottom - 24) }) })
const alignRight = computed(() => point.value.x > window.innerWidth / 2)
const nearTop = computed(() => point.value.y < 150)
let focusTimer = null
function dismissMenu(event) { if (!dock.value?.contains(event.target)) menuOpen.value = false }
function updateEditing() {
  compactViewport.value = window.innerWidth <= 768
  clearTimeout(focusTimer)
  focusTimer = setTimeout(() => { editing.value = window.innerWidth <= 768 && !!document.activeElement?.matches('input, textarea, select, [contenteditable="true"]') }, 0)
}
onMounted(() => { document.addEventListener('focusin', updateEditing); document.addEventListener('focusout', updateEditing); document.addEventListener('pointerdown', dismissMenu); window.addEventListener('resize', updateEditing) })
onUnmounted(() => { clearTimeout(focusTimer); document.removeEventListener('focusin', updateEditing); document.removeEventListener('focusout', updateEditing); document.removeEventListener('pointerdown', dismissMenu); window.removeEventListener('resize', updateEditing) })
</script>

<style scoped>
.interactive-dock { position: fixed; left: 0; top: 0; z-index: 90; display: flex; align-items: center; gap: 7px; padding: 7px 9px 7px 7px; width: 136px; height: 64px; color: #665575; background: rgba(255,255,255,.32); border: 1px solid rgba(255,255,255,.48); border-radius: 38px; box-shadow: 0 5px 22px rgba(45,23,74,.12); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); user-select: none; touch-action: none; }
.interactive-dock.is-collapsed { width: 64px; padding: 7px; }
.is-settling { transition: transform 360ms cubic-bezier(.2,.9,.3,1.12); }
.is-dragging { cursor: grabbing; box-shadow: 0 9px 26px rgba(45,23,74,.2); }
button { flex-shrink: 0; padding: 0; border: 0; color: inherit; cursor: grab; background: transparent; touch-action: none; }
button:focus-visible { outline: 2px solid #7c3aed; outline-offset: 3px; }
button:disabled { cursor: wait; }
.mini-record { position: relative; width: 48px; height: 48px; border-radius: 50%; }
.record-disc { position: absolute; inset: 0; display: grid; place-items: center; border: 1px solid rgba(255,255,255,.3); border-radius: 50%; background: repeating-radial-gradient(circle at center,#292331 0 2px,#403548 3px,#292331 4px 6px); box-shadow: 0 2px 7px rgba(24,17,36,.2); animation: record-spin 9s linear infinite; animation-play-state: paused; }
.is-playing .record-disc { animation-play-state: running; }
.record-label { display: grid; place-items: center; width: 21px; height: 21px; border-radius: 50%; background: linear-gradient(140deg,#cd9bef,#ad80da); color: #fff; }
.record-label svg { width: 13px; height: 13px; fill: none; stroke: currentColor; stroke-width: 1.6; }
.wallpaper-switch { position: relative; display: grid; place-items: center; width: 36px; height: 44px; border-radius: 12px; color: #775493; }
.wallpaper-switch svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.4; stroke-linecap: round; stroke-linejoin: round; }
.wallpaper-switch:hover { background: rgba(255,255,255,.2); }
.wallpaper-dot { position: absolute; width: 5px; height: 5px; right: 5px; top: 7px; border-radius: 50%; background: #a56bc8; animation: dock-pulse .9s ease-in-out infinite alternate; }
.dock-reset { width: 16px; height: 36px; border-radius: 8px; font-size: 17px; cursor: pointer; opacity: .65; }
.dock-options { position: absolute; bottom: calc(100% + 8px); left: 0; display: grid; min-width: 112px; padding: 5px; border: 1px solid rgba(255,255,255,.65); border-radius: 12px; background: rgba(250,246,255,.96); box-shadow: 0 5px 16px rgba(45,23,74,.1); }
.dock-options button { min-height: 44px; padding: 8px 12px; font: inherit; font-size: 12px; cursor: pointer; text-align: left; border-radius: 8px; }
.dock-options button:hover { background: rgba(124,58,237,.07); }
.dock-feedback { position: absolute; bottom: calc(100% + 10px); left: 0; min-width: 128px; max-width: min(230px,calc(100vw - 40px)); margin: 0; padding: 9px 12px; border-radius: 12px; background: rgba(249,246,253,.94); color: #51435f; font-size: 12px; line-height: 1.6; box-shadow: 0 3px 14px rgba(45,23,74,.08); pointer-events: none; }
.is-right .dock-feedback { left: auto; right: 0; }
.is-near-top .dock-feedback,.is-near-top .dock-options { bottom: auto; top: calc(100% + 10px); }
.record-loading { position: absolute; inset: 3px; border: 2px solid transparent; border-top-color: #e4c6ff; border-radius: 50%; animation: record-spin 1s linear infinite; }
@keyframes record-spin { to { transform: rotate(360deg); } }
@keyframes dock-pulse { to { opacity: .25; } }
@media(max-width:768px) { .interactive-dock { width: 160px; height: 64px; gap: 4px; padding-right: 6px; } .wallpaper-switch { width: 44px; } .dock-reset { width: 44px; height: 44px; } }
@media(prefers-reduced-motion:reduce) { .is-settling { transition: none; } .record-disc,.record-loading,.wallpaper-dot { animation: none; } }
</style>
