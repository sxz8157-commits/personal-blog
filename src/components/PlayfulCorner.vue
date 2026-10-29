<template>
  <section class="playful-corner" aria-labelledby="playful-title">
    <header class="playful-header"><div><p class="playful-eyebrow">A LITTLE PLAY</p><h3 id="playful-title">随手玩一会儿</h3></div><button type="button" class="playful-reset" @click="resetAll">全部归位 <span aria-hidden="true">↺</span></button></header>
    <p id="playful-help" class="playful-help">拖一拖纸飞机，挪挪小磁贴；点一下，也有回应。</p>
    <div ref="board" class="playful-board">
      <svg class="flight-trace" viewBox="0 0 400 160" aria-hidden="true"><path d="M24 132C40 78 104 144 132 94S170 36 194 62 170 126 236 102 284 22 358 38"/></svg>
      <button ref="plane" type="button" class="paper-plane" :class="{ 'is-dragging': dragging, 'is-settling': settling, 'is-fluttering': fluttering }" :style="style" aria-label="拖动纸飞机" aria-describedby="playful-help" @pointerdown="begin" @click.capture="guardClick" @keydown="keydown" @click="flutter">
        <svg viewBox="0 0 64 64" aria-hidden="true"><path class="plane-wing" d="M5 27 57 7 40 57 28 37Z"/><path class="plane-fold" d="m5 27 23 10L57 7 22 30Z"/><path class="plane-tail" d="m28 37-3 16 10-10"/><path class="plane-line" d="m22 30 35-23-29 30"/></svg>
      </button>
      <MagneticNote v-for="(topic,index) in topics.slice(0,3)" :key="topic.id" :topic="topic" :index="index" :area="board" :open="openNote === topic.id" :reset-key="resetKey" @toggle="openNote = openNote === topic.id ? '' : topic.id" />
      <span class="board-caption" aria-hidden="true">一点好奇心，就够了。</span>
    </div>
    <p class="playful-status" role="status" aria-live="polite">{{ status }}</p>
  </section>
</template>
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { usePointerDrag } from '@/composables/usePointerDrag'
import MagneticNote from '@/components/MagneticNote.vue'
defineProps({ topics: { type: Array, default: () => [] } })
const emit = defineEmits(['visibility-change'])
const board = ref(null), plane = ref(null), openNote = ref(''), resetKey = ref(0), fluttering = ref(false), status = ref('')
let flutterTimer = null, flutterFrame = 0, observer = null
const { style, dragging, settling, begin, guardClick, keydown, reset } = usePointerDrag(plane, { area: board, returnHome: true, initial: b => ({ x: (b.left + b.right) * .56, y: 24 }) })
function flutter() {
  clearTimeout(flutterTimer)
  cancelAnimationFrame(flutterFrame)
  fluttering.value = false
  flutterFrame = requestAnimationFrame(() => { flutterFrame = 0; fluttering.value = true; status.value = '纸飞机收到了这一阵风。' })
  flutterTimer = setTimeout(() => { fluttering.value = false; status.value = '' }, 1100)
}
function resetAll() { reset(); openNote.value = ''; resetKey.value++; status.value = '小玩意都回到原位了。' }
onMounted(() => { observer = new IntersectionObserver(([entry]) => emit('visibility-change', entry.isIntersecting), { rootMargin: '-72px 0px 0px 0px' }); observer.observe(board.value) })
onUnmounted(() => { clearTimeout(flutterTimer); cancelAnimationFrame(flutterFrame); observer?.disconnect(); emit('visibility-change', false) })
</script>
<style scoped>
.playful-corner { margin-top: 42px; color: #302638; }
.playful-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; }
.playful-eyebrow { margin: 0 0 6px; color: #876c99; font-size: 10px; letter-spacing: .17em; }
.playful-header h3 { margin: 0; color: #302638; font-size: 22px; font-weight: 650; letter-spacing: -.025em; }
.playful-reset { min-height: 44px; padding: 7px 0 7px 10px; border: 0; color: #76518e; background: transparent; font: inherit; font-size: 12px; cursor: pointer; white-space: nowrap; }
.playful-reset span { margin-left: 6px; font-size: 17px; }
.playful-help { margin: 14px 0 18px; color: #63576d; font-size: 12px; line-height: 1.8; }
.playful-board { position: relative; width: 100%; height: 324px; overflow: hidden; border: 1px solid rgba(255,255,255,.34); border-radius: 20px; background: linear-gradient(150deg,rgba(255,255,255,.13),rgba(242,225,255,.07)); }
.flight-trace { position: absolute; top: 18px; left: 7%; width: 80%; height: 150px; pointer-events: none; }
.flight-trace path { fill: none; stroke: rgba(126,91,155,.22); stroke-width: 1; stroke-dasharray: 3 7; }
.paper-plane { position: absolute; left: 0; top: 0; z-index: 3; width: 70px; height: 70px; padding: 4px; border: 0; background: transparent; cursor: grab; user-select: none; touch-action: none; }
.paper-plane > svg { width: 100%; height: 100%; overflow: visible; filter: drop-shadow(0 4px 5px rgba(82,51,102,.12)); }
.plane-wing { fill: #ead6f6; stroke: rgba(149,106,177,.5); stroke-width: 1; stroke-linejoin: round; }
.plane-fold { fill: #faf1ff; }
.plane-tail { fill: #be99d3; }
.plane-line { fill: none; stroke: rgba(139,99,168,.5); stroke-width: 1; }
.paper-plane.is-dragging { cursor: grabbing; z-index: 6; }
.paper-plane.is-settling { transition: transform 450ms cubic-bezier(.18,.85,.25,1.25); }
.is-fluttering > svg { animation: plane-flutter 700ms ease-in-out; }
.board-caption { position: absolute; bottom: 16px; right: 18px; color: #876d98; font-size: 10px; letter-spacing: .05em; pointer-events: none; }
.playful-status { min-height: 20px; margin: 10px 0 0; color: #76518e; font-size: 11px; text-align: center; }
button:focus-visible { outline: 2px solid #7c3aed; outline-offset: 4px; border-radius: 10px; }
@keyframes plane-flutter { 30% { transform: translate(9px,-10px) rotate(-9deg); } 65% { transform: translate(-3px,3px) rotate(4deg); } }
@media(max-width:480px) { .playful-corner { margin-top: 30px; } .playful-header h3 { font-size: 20px; } .playful-board { height: 456px; border-radius: 16px; } .paper-plane { width: 64px; height: 64px; } .playful-help { font-size: 12px; } }
@media(prefers-reduced-motion:reduce) { .paper-plane.is-settling { transition: none; } .is-fluttering > svg { animation: none; } }
</style>
