<template>
  <article class="desk-toy" :data-toy="kind">
    <div ref="stage" class="toy-stage">
      <span class="toy-shadow" aria-hidden="true"></span>
      <button ref="toy" type="button" class="toy-handle" :class="[{ 'is-dragging': dragging, 'is-settling': settling, 'is-playing': playing, 'is-lit': lit }, `toy-${kind}`]" :style="[style, { '--toy-turn': `${turn}deg` }]" :aria-label="`${name}：${result}`" :aria-describedby="`toy-help-${kind}`" :aria-pressed="kind === 'star' ? lit : undefined" @pointerdown="begin" @click.capture="guardClick" @keydown="keydown" @click="activate">
        <svg v-if="kind === 'cat'" class="toy-art cat-art" viewBox="0 0 80 80" aria-hidden="true">
          <path class="cat-tail" d="M57 63c23 1 15-23 8-14"/>
          <path class="toy-fill" d="M23 42c-8 20-2 29 17 29s25-9 17-29Z"/>
          <path class="toy-fill" d="M18 34 20 9 35 20q6-2 11 0L61 9l2 25q0 20-23 20T18 34Z"/>
          <path class="cat-ear" d="m23 17 1 13 8-6m25-7-1 13-8-6"/>
          <g class="cat-eyes"><path d="M28 34v4m24-4v4"/></g>
          <g class="cat-happy"><path d="m25 37 5-3 4 3m12 0 5-3 4 3"/></g>
          <path class="cat-smile" d="m37 41 3 2 3-2m-3 2q-4 6-7 1m7-1q4 6 7 1"/>
          <ellipse class="cat-blush" cx="24" cy="42" rx="4" ry="2"/><ellipse class="cat-blush" cx="56" cy="42" rx="4" ry="2"/>
          <path class="cat-paws" d="M30 62v7m20-7v7"/>
        </svg>
        <svg v-else-if="kind === 'windmill'" class="toy-art windmill-art" viewBox="0 0 80 80" aria-hidden="true">
          <path class="windmill-stick" d="M40 37v38"/>
          <g class="windmill-blades"><path d="M40 36 17 10q29-9 23 26Z"/><path d="M40 36 66 13q9 29-26 23Z"/><path d="m40 36 23 26q-29 9-23-26Z"/><path d="M40 36 14 59q-9-29 26-23Z"/></g>
          <circle class="windmill-pin" cx="40" cy="36" r="4"/>
        </svg>
        <svg v-else-if="kind === 'bubble'" class="toy-art bubble-art" viewBox="0 0 80 80" aria-hidden="true">
          <circle class="bubble-shell" cx="40" cy="40" r="27"/><path class="bubble-shine" d="M21 34q4-15 19-15m15 40 4-5"/>
          <g class="bubble-spark"><path d="M40 2v9m0 58v9M2 40h9m58 0h9M12 12l7 7m42 42 7 7M12 68l7-7m42-42 7-7"/></g>
        </svg>
        <span v-else-if="kind === 'dice'" class="dice-art toy-art" aria-hidden="true">
          <span v-for="(dot,index) in dots" :key="index" class="dice-dot" :style="{ left: `${dot[0]}%`, top: `${dot[1]}%` }"></span>
        </span>
        <span v-else-if="kind === 'coin'" class="coin-art toy-art" aria-hidden="true">
          <span class="coin-face coin-front"><svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="9"/><path d="M30 9v5m0 32v5M9 30h5m32 0h5M15 15l4 4m22 22 4 4M15 45l4-4m22-22 4-4"/></svg></span>
          <span class="coin-face coin-back"><svg viewBox="0 0 60 60"><path d="M38 12a19 19 0 1 0 10 29c-21 3-25-16-10-29Z"/><path d="m43 12 1 4 4 1-4 1-1 4-1-4-4-1 4-1Z"/></svg></span>
        </span>
        <svg v-else class="toy-art star-art" viewBox="0 0 80 80" aria-hidden="true"><path class="star-shape" d="m40 8 10 20 23 3-17 17 4 24-20-11-20 11 4-24L7 31l23-3Z"/><path class="star-smile" d="M32 43q8 9 16 0m-19-9v3m22-3v3"/></svg>
      </button>
    </div>
    <div class="toy-caption"><h4>{{ name }}</h4><p :id="`toy-help-${kind}`">{{ hint }}</p><p class="toy-result" role="status" aria-live="polite">{{ result === hint ? '也可以拖一拖' : result }}</p></div>
  </article>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { usePointerDrag } from '@/composables/usePointerDrag'

const props = defineProps({ kind: { type: String, required: true }, name: { type: String, required: true }, hint: { type: String, required: true }, resetKey: Number })
const stage = ref(null), toy = ref(null), playing = ref(false), lit = ref(false), turn = ref(0), face = ref(1), popped = ref(0), result = ref(props.hint)
let timer = null
const { style, dragging, settling, begin, guardClick, keydown, reset } = usePointerDrag(toy, { area: stage, returnHome: props.kind === 'cat', initial: b => ({ x: (b.left + b.right) / 2, y: (b.top + b.bottom) / 2 }) })
const pipPositions = [[], [[50,50]], [[27,27],[73,73]], [[27,27],[50,50],[73,73]], [[27,27],[73,27],[27,73],[73,73]], [[27,27],[73,27],[50,50],[27,73],[73,73]], [[27,25],[73,25],[27,50],[73,50],[27,75],[73,75]]]
const dots = computed(() => pipPositions[face.value])

function animate(duration) {
  clearTimeout(timer)
  playing.value = true
  timer = setTimeout(() => { playing.value = false; timer = null }, duration)
}
function activate() {
  if (props.kind === 'cat') { result.value = '喵，今天也要开心。'; animate(900) }
  else if (props.kind === 'windmill') { turn.value += 1080; result.value = '替你收集了一点风。' }
  else if (props.kind === 'bubble') {
    if (playing.value) return
    popped.value++
    result.value = `第 ${popped.value} 颗泡泡，烦恼少一点。`
    animate(600)
  } else if (props.kind === 'dice') {
    // 每次换到不同点数，点击反馈清晰；仅作页面玩具。
    face.value = (face.value + Math.floor(Math.random() * 5)) % 6 + 1
    result.value = `掷到了 ${face.value} 点。`
    animate(500)
  } else if (props.kind === 'coin') { turn.value += 180; result.value = turn.value % 360 ? '这一面，是月色。' : '这一面，是阳光。' }
  else { lit.value = !lit.value; result.value = lit.value ? '给今天留一盏小星光。' : '星星休息一会儿。' }
}
watch(() => props.resetKey, () => {
  clearTimeout(timer); timer = null
  playing.value = false; lit.value = false; turn.value = 0; face.value = 1; popped.value = 0; result.value = props.hint
  reset()
})
onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.desk-toy { --toy-ink: #6f4c83; --toy-pale: #f5e9fd; --toy-line: #b296c4; --toy-pink: #eebdd6; --toy-glow: #f7db93; width: 144px; max-width: 100%; min-width: 0; }
.toy-stage { position: relative; height: 110px; overflow: hidden; }
.toy-shadow { position: absolute; width: 54px; height: 8px; bottom: 8px; left: calc(50% - 27px); border-radius: 50%; background: rgba(104,69,128,.09); pointer-events: none; }
.toy-handle { position: absolute; left: 0; top: 0; width: 80px; height: 80px; border: 0; padding: 4px; background: transparent; color: var(--toy-ink); cursor: grab; touch-action: none; user-select: none; }
.toy-handle.is-dragging { cursor: grabbing; z-index: 2; }
.toy-handle.is-settling { transition: transform 340ms cubic-bezier(.2,.9,.3,1.15); }
.toy-handle:focus-visible { outline: 2px solid var(--toy-ink); outline-offset: 2px; border-radius: 14px; }
.toy-art { display: block; width: 100%; height: 100%; overflow: visible; filter: drop-shadow(0 4px 5px rgba(89,53,111,.1)); }
.toy-fill { fill: var(--toy-pale); stroke: var(--toy-line); stroke-width: 1.3; stroke-linejoin: round; }
.cat-tail { fill: none; stroke: var(--toy-line); stroke-width: 5; stroke-linecap: round; }
.cat-ear,.cat-blush { fill: var(--toy-pink); }
.cat-eyes,.cat-happy,.cat-smile,.cat-paws { fill: none; stroke: var(--toy-ink); stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.cat-happy { opacity: 0; }
.is-playing .cat-eyes { opacity: 0; }
.is-playing .cat-happy { opacity: 1; }
.is-playing .cat-art { animation: toy-bounce 700ms ease; }
.windmill-stick { stroke: var(--toy-line); stroke-width: 3; stroke-linecap: round; }
.windmill-blades { transform-origin: 40px 36px; transform: rotate(var(--toy-turn)); transition: transform 1200ms cubic-bezier(.15,.6,.2,1); fill: var(--toy-pink); stroke: var(--toy-line); stroke-width: .7; }
.windmill-blades path:nth-child(even) { fill: var(--toy-pale); }
.windmill-pin { fill: var(--toy-glow); stroke: var(--toy-line); }
.bubble-shell { fill: rgba(241,222,252,.24); stroke: var(--toy-line); stroke-width: 1.2; }
.bubble-shine { fill: none; stroke: rgba(255,255,255,.9); stroke-width: 4; stroke-linecap: round; }
.bubble-spark { stroke: var(--toy-line); stroke-width: 1.7; opacity: 0; transform-origin: center; }
.is-playing .bubble-shell,.is-playing .bubble-shine { opacity: 0; }
.is-playing .bubble-spark { animation: toy-pop 600ms ease-out; }
.dice-art { position: relative; width: 58px; height: 58px; margin: 7px; border: 1px solid var(--toy-line); border-radius: 15px; background: linear-gradient(135deg,var(--toy-pale),rgba(239,214,249,.64)); box-shadow: inset -4px -4px 0 rgba(124,86,147,.08); transform: rotate(-9deg); }
.dice-dot { position: absolute; width: 7px; height: 7px; margin: -3.5px; border-radius: 50%; background: var(--toy-ink); }
.is-playing .dice-art { animation: toy-roll 500ms ease; }
.coin-art { position: relative; width: 64px; height: 64px; margin: 4px; transform-style: preserve-3d; transform: perspective(400px) rotateY(var(--toy-turn)); transition: transform 650ms cubic-bezier(.2,.7,.25,1); filter: none; }
.coin-face { position: absolute; inset: 0; border: 2px solid var(--toy-line); border-radius: 50%; background: var(--toy-pale); box-shadow: inset 0 0 0 4px rgba(255,255,255,.55),0 4px 6px rgba(89,53,111,.1); backface-visibility: hidden; }
.coin-face svg { width: 100%; height: 100%; fill: none; stroke: var(--toy-ink); stroke-width: 1.6; stroke-linecap: round; }
.coin-front { background: #f4e6cb; }
.coin-back { transform: rotateY(180deg); }
.star-shape { fill: var(--toy-pale); stroke: var(--toy-line); stroke-width: 1.3; stroke-linejoin: round; transition: fill 250ms; }
.star-smile { fill: none; stroke: var(--toy-ink); stroke-width: 1.7; stroke-linecap: round; }
.is-lit .star-shape { fill: var(--toy-glow); }
.is-lit .star-art { filter: drop-shadow(0 0 8px rgba(246,207,109,.55)); }
.toy-caption { padding: 2px 2px 6px; text-align: center; }
.toy-caption h4 { margin: 0; color: var(--toy-ink); font-size: 12px; font-weight: 600; letter-spacing: .03em; }
.toy-caption > p[id] { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip-path: inset(50%); }
.toy-caption p { margin: 7px 0 0; color: #685674; font-size: 11px; line-height: 1.6; }
.toy-caption .toy-result { min-height: 34px; margin-top: 4px; color: #81648e; }
@keyframes toy-bounce { 25% { transform: translateY(-7px) rotate(-6deg); } 65% { transform: translateY(1px) rotate(4deg); } }
@keyframes toy-pop { 10% { opacity: 1; transform: scale(.6); } 100% { opacity: 0; transform: scale(1.1); } }
@keyframes toy-roll { 35% { transform: rotate(20deg) scale(.88); } 70% { transform: rotate(-20deg); } }
@media(max-width:480px) { .desk-toy { width: 132px; } .toy-stage { height: 104px; } .toy-handle { width: 72px; height: 72px; } .dice-art { width: 54px; height: 54px; margin: 5px; } .coin-art { width: 58px; height: 58px; margin: 3px; } }
@media(prefers-reduced-motion:reduce) { .toy-handle,.windmill-blades,.coin-art,.star-shape { transition: none; } .toy-art,.bubble-spark { animation: none !important; } .is-playing .bubble-spark { opacity: .7; } }
</style>
