<template>
  <button ref="note" type="button" class="magnetic-note" :class="{ 'is-open': open, 'is-dragging': dragging, 'is-settling': settling }" :style="[style, { '--note-tilt': `${tilt}deg` }]" :aria-label="`查看${topic.label}磁贴`" :aria-expanded="open" aria-describedby="playful-help" @pointerdown="begin" @click.capture="guardClick" @keydown="keydown" @click="$emit('toggle')">
    <span class="note-paper"><span class="note-number">0{{ index + 1 }}</span><strong>{{ topic.label }}</strong><span v-if="open" class="note-detail">{{ topic.note }}</span><span v-else class="note-hint">点开看看 <span aria-hidden="true">↗</span></span><span class="note-corner" aria-hidden="true"></span></span>
  </button>
</template>
<script setup>
import { ref, watch } from 'vue'
import { usePointerDrag } from '@/composables/usePointerDrag'
const props = defineProps({ topic: { type: Object, required: true }, index: Number, area: { type: Object, default: null }, open: Boolean, resetKey: Number })
defineEmits(['toggle'])
const note = ref(null)
const tilt = [-4, 3, -2][props.index] || 0
const { style, dragging, settling, begin, guardClick, keydown, reset } = usePointerDrag(note, {
  area: { get value() { return props.area } }, snap: 'grid',
  initial: b => {
    const width = props.area?.clientWidth || 0
    if (width < 420) return { x: props.index === 0 ? b.left : props.index === 1 ? b.right : (b.left + b.right) / 2, y: props.index === 2 ? 290 : 142 + props.index * 8 }
    return { x: b.left + (b.right - b.left) * (0.05 + props.index * .42), y: 150 + props.index % 2 * 10 }
  }
})
watch(() => props.resetKey, reset)
</script>
<style scoped>
.magnetic-note { position: absolute; left: 0; top: 0; z-index: 2; width: 138px; height: 124px; padding: 0; border: 0; background: transparent; text-align: left; color: #44324e; user-select: none; touch-action: none; cursor: grab; }
.note-paper { position: relative; display: flex; flex-direction: column; justify-content: center; gap: 9px; width: 100%; height: 100%; padding: 14px 17px; border: 1px solid rgba(255,255,255,.55); border-radius: 13px 13px 20px 13px; background: linear-gradient(135deg,rgba(250,238,254,.67),rgba(242,232,250,.33)); box-shadow: 0 6px 16px rgba(67,38,82,.08); transform: rotate(var(--note-tilt)); transition: background-color 180ms, box-shadow 180ms; }
.note-number { position: absolute; top: 10px; right: 12px; color: #856b97; font-size: 9px; letter-spacing: .08em; }
.note-paper strong { color: #44324e; font-size: 19px; font-weight: 650; }
.note-hint { display: flex; justify-content: space-between; color: #876b9a; font-size: 11px; }
.note-detail { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; color: #5e4b6d; font-size: 12px; line-height: 1.65; }
.note-corner { position: absolute; bottom: 0; right: 0; width: 17px; height: 17px; border-radius: 7px 0 18px 0; background: rgba(167,122,191,.14); }
.is-open .note-paper { background: rgba(250,240,255,.83); gap: 7px; }
.is-open strong { font-size: 15px; }
.is-dragging { z-index: 5; cursor: grabbing; }
.is-dragging .note-paper { transform: rotate(0); box-shadow: 0 12px 24px rgba(67,38,82,.18); }
.is-settling { transition: transform 340ms cubic-bezier(.2,.9,.3,1.1); }
.magnetic-note:focus-visible { outline: 2px solid #7c3aed; outline-offset: 6px; border-radius: 14px; }
@media(max-width:480px) { .magnetic-note { width: 112px; height: 120px; } .note-paper { padding: 14px 12px; } .note-paper strong { font-size: 18px; } .is-open strong { font-size: 15px; } }
@media(prefers-reduced-motion:reduce) { .is-settling,.note-paper { transition: none; } }
</style>
