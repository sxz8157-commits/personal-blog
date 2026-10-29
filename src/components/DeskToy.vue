<template>
  <article class="desk-toy" :data-toy="kind">
    <div ref="stage" class="toy-stage" @pointermove="lookAt" @pointerleave="look = 0">
      <span class="toy-shadow" aria-hidden="true"></span>
      <svg v-if="kind === 'star'" class="constellation" viewBox="0 0 144 110" aria-hidden="true"><polyline :points="starPoints.slice(0, starCount).map(p => p.join(',')).join(' ')"/><circle v-for="(p,i) in starPoints" :key="i" :cx="p[0]" :cy="p[1]" r="2.5" :class="{ 'is-collected': i < starCount }"/></svg>
      <span v-for="particle in particles" :key="particle.id" class="play-particle" :style="particle.style" aria-hidden="true">{{ particle.symbol }}</span>
      <span v-if="meteor" class="shooting-star" aria-hidden="true">✦</span>
      <div v-if="kind === 'bubble'" class="bubble-sheet" @pointerdown="startBubbles" @pointermove="sweepBubbles" @pointerup="stopBubbles" @pointercancel="stopBubbles" @lostpointercapture="stopBubbles">
        <button v-for="(_,index) in bubbleCells" :key="index" type="button" class="bubble-cell" :class="{ 'is-popped': bubbleCells[index] }" :aria-label="`第 ${index + 1} 颗泡泡`" :aria-pressed="bubbleCells[index]" :data-bubble="index" @click="popBubble(index)"><span aria-hidden="true"></span></button>
      </div>
      <button v-else ref="toy" type="button" class="toy-handle" :class="[{ 'is-dragging': dragging, 'is-settling': settling, 'is-playing': playing, 'is-lit': starCount > 0, 'is-pressing': pressing, 'is-charged': charged }, `toy-${kind}`]" :style="[style, { '--toy-turn': `${turn}deg`, '--spin-time': `${spinTime}ms` }]" :aria-label="`${name}：${help}`" :aria-describedby="`toy-help-${kind}`" :aria-busy="busy || undefined" :disabled="busy" @pointerdown="start" @click.capture="guard" @keydown="keydown" @click="activate">
        <svg v-if="kind === 'cat'" class="toy-art cat-art" viewBox="0 0 80 80" aria-hidden="true">
          <path class="cat-tail" d="M57 63c23 1 15-23 8-14"/>
          <path class="toy-fill" d="M23 42c-8 20-2 29 17 29s25-9 17-29Z"/>
          <path class="toy-fill" d="M18 34 20 9 35 20q6-2 11 0L61 9l2 25q0 20-23 20T18 34Z"/>
          <path class="cat-ear" d="m23 17 1 13 8-6m25-7-1 13-8-6"/>
          <g class="cat-eyes" :style="{ transform: `translateX(${look}px)` }"><path d="M28 34v4m24-4v4"/></g>
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
        <span v-else-if="kind === 'dice'" class="dice-art toy-art" aria-hidden="true">
          <span v-for="(dot,index) in dots" :key="index" class="dice-dot" :style="{ left: `${dot[0]}%`, top: `${dot[1]}%` }"></span>
        </span>
        <span v-else-if="kind === 'coin'" class="coin-lift" aria-hidden="true"><span class="coin-art toy-art">
          <span class="coin-face coin-front"><svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="9"/><path d="M30 9v5m0 32v5M9 30h5m32 0h5M15 15l4 4m22 22 4 4M15 45l4-4m22-22 4-4"/></svg></span>
          <span class="coin-face coin-back"><svg viewBox="0 0 60 60"><path d="M38 12a19 19 0 1 0 10 29c-21 3-25-16-10-29Z"/><path d="m43 12 1 4 4 1-4 1-1 4-1-4-4-1 4-1Z"/></svg></span>
        </span></span>
        <svg v-else class="toy-art star-art" viewBox="0 0 80 80" aria-hidden="true"><path class="star-shape" d="m40 8 10 20 23 3-17 17 4 24-20-11-20 11 4-24L7 31l23-3Z"/><path class="star-smile" d="M32 43q8 9 16 0m-19-9v3m22-3v3"/></svg>
      </button>
    </div>
    <div class="toy-caption">
      <h4>{{ name }}</h4><p :id="`toy-help-${kind}`" class="toy-help">{{ help }}</p>
      <div v-if="kind === 'cat'" class="affection" :aria-label="`亲密度 ${affection}/5`"><span v-for="n in 5" :key="n" :class="{ filled: n <= affection }" aria-hidden="true">♥</span></div>
      <div v-if="kind === 'windmill'" class="charge-meter" :class="{ charging: pressing }" aria-label="长按蓄风"><span></span></div>
      <div v-if="kind === 'star'" class="star-progress" :aria-label="`已收集 ${starCount}/5 颗星光`"><span v-for="n in 5" :key="n" :class="{ filled: n <= starCount }" aria-hidden="true">✦</span></div>
      <div v-if="kind === 'coin'" class="coin-history" aria-label="最近五次抛币结果"><span v-for="(side,index) in history" :key="index">{{ side ? '月' : '日' }}</span></div>
      <p class="toy-result" role="status" aria-live="polite">{{ result }}</p>
      <button v-if="kind === 'cat'" type="button" class="toy-action" @click="pet(2, true)">喂一口 <span aria-hidden="true">♡</span></button>
      <button v-if="kind === 'bubble'" type="button" class="toy-action" @click="resetBubbles">再来一板 ↺</button>
      <button v-if="kind === 'star'" type="button" class="toy-action" @click="resetStars">重新许愿 ↺</button>
      <div v-if="kind === 'dice'" class="dice-choices" role="group" aria-label="猜单双"><button type="button" :disabled="busy" :aria-pressed="guess === 'odd'" @click="guess = 'odd'">猜单</button><button type="button" :disabled="busy" :aria-pressed="guess === 'even'" @click="guess = 'even'">猜双</button></div>
    </div>
  </article>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { usePointerDrag } from '@/composables/usePointerDrag'
import { useToyGesture } from '@/composables/useToyGesture'

const props = defineProps({ kind: { type: String, required: true }, name: { type: String, required: true }, hint: { type: String, required: true }, resetKey: Number })
const stage = ref(null), toy = ref(null), playing = ref(false), busy = ref(false), turn = ref(0), face = ref(1), result = ref(''), spinTime = ref(1200), look = ref(0)
const affection = ref(0), bubbleCells = ref(Array(9).fill(false)), starCount = ref(0), meteor = ref(false), history = ref([]), guess = ref('odd'), wins = ref(0), rounds = ref(0), particles = ref([])
const starPoints = [[12,35],[34,12],[78,15],[132,35],[113,92]]
const help = computed(() => ({ cat: '点按抚摸 · 长按或喂食', windmill: '点按吹风 · 长按蓄力松手', bubble: '点按或按住划过九颗泡泡', dice: '先猜单双，再点骰子开奖', coin: '点按抛币，看看阳光或月色', star: '点按集星 · 长按放一颗流星' })[props.kind] || props.hint)
let timer = null, rollTimer = null, particleTimer = null, particleId = 0, coinSide = 0, bubblePointer = null
const drag = usePointerDrag(toy, { area: stage, returnHome: props.kind === 'cat', initial: b => ({ x: (b.left + b.right) / 2, y: (b.top + b.bottom) / 2 }) })
const { style, dragging, settling, keydown, reset } = drag
const { pressing, charged, start, guard, cancel } = useToyGesture(drag, gesturePlay)
const pipPositions = [[], [[50,50]], [[27,27],[73,73]], [[27,27],[50,50],[73,73]], [[27,27],[73,27],[27,73],[73,73]], [[27,27],[73,27],[50,50],[27,73],[73,73]], [[27,25],[73,25],[27,50],[73,50],[27,75],[73,75]]]
const dots = computed(() => pipPositions[face.value])

function animate(duration, done) {
  clearTimeout(timer)
  playing.value = true
  timer = setTimeout(() => { playing.value = false; busy.value = false; timer = null; done?.() }, duration)
}
function burst(symbol = '✦') {
  clearTimeout(particleTimer)
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  particles.value = reduced ? [] : Array.from({ length: 12 }, (_, i) => { const angle = i * Math.PI / 6; return { id: ++particleId, symbol, style: { '--px': `${Math.cos(angle) * 48}px`, '--py': `${Math.sin(angle) * 44}px`, '--delay': `${i % 3 * 30}ms` } } })
  particleTimer = setTimeout(() => { particles.value = []; meteor.value = false; particleTimer = null }, 1300)
}
function pet(amount = 1, food = false) {
  affection.value = Math.min(5, affection.value + amount)
  result.value = food ? `好吃！亲密度 ${affection.value}/5` : affection.value === 5 ? '呼噜呼噜，已经是好朋友啦。' : `喵，再摸摸我吧 · ${affection.value}/5`
  burst('♥'); animate(900)
}
function blow(power = 1, direction = 1) {
  const circles = Math.max(1, Math.min(6, Math.round(power)))
  spinTime.value = 800 + circles * 220; turn.value += direction * circles * 360
  result.value = `这一阵风，转了 ${circles} 圈。`
}
function collectStars(full = false) {
  starCount.value = full ? 5 : Math.min(5, starCount.value + 1)
  result.value = starCount.value === 5 ? '小星座亮了，愿望出发。' : `攒下 ${starCount.value}/5 颗星光。`
  if (starCount.value === 5) meteor.value = true
  burst()
}
function resetStars() { starCount.value = 0; meteor.value = false; result.value = '新愿望，慢慢收集。' }
function popBubble(index) {
  if (!Number.isInteger(index) || index < 0 || index > 8 || bubbleCells.value[index]) return
  bubbleCells.value[index] = true
  const count = bubbleCells.value.filter(Boolean).length
  result.value = count === 9 ? '九颗清空！烦恼也清空。' : `噗！已解压 ${count}/9`
  if (count === 9) burst('○')
}
function resetBubbles() { bubbleCells.value = Array(9).fill(false); result.value = '新的一板，随手解压。' }
function startBubbles(event) {
  if (event.button !== 0 || event.isPrimary === false) return
  const index = event.target.closest('[data-bubble]')?.dataset.bubble
  if (index === undefined) return
  bubblePointer = event.pointerId
  event.currentTarget.setPointerCapture(event.pointerId)
  popBubble(Number(index))
}
function sweepBubbles(event) {
  if (event.pointerId !== bubblePointer) return
  const hit = document.elementFromPoint(event.clientX, event.clientY)?.closest('[data-bubble]')
  if (hit && stage.value.contains(hit)) popBubble(Number(hit.dataset.bubble))
}
function stopBubbles() { bubblePointer = null }
function lookAt(event) {
  if (props.kind !== 'cat' || event.pointerType === 'touch') return
  const rect = stage.value.getBoundingClientRect()
  look.value = Math.max(-2, Math.min(2, (event.clientX - rect.x - rect.width / 2) / 20))
}
function activate() {
  if (busy.value) return
  if (props.kind === 'cat') pet()
  else if (props.kind === 'windmill') blow(2)
  else if (props.kind === 'star') collectStars()
  else if (props.kind === 'dice') {
    busy.value = true; result.value = '骰子转一转…'
    const outcome = Math.floor(Math.random() * 6) + 1, prediction = guess.value
    rollTimer = setInterval(() => { face.value = face.value % 6 + 1 }, 70)
    animate(560, () => {
      clearInterval(rollTimer); rollTimer = null; face.value = outcome; rounds.value++
      const win = (outcome % 2 ? 'odd' : 'even') === prediction
      if (win) { wins.value++; burst() }
      result.value = `${outcome} 点，${win ? '猜中啦' : '再试一次'} · ${wins.value}/${rounds.value}`
    })
  } else if (props.kind === 'coin') {
    busy.value = true; result.value = '硬币抛起来了…'
    const outcome = Math.floor(Math.random() * 2)
    turn.value += 1080 + (outcome - coinSide) * 180; coinSide = outcome
    animate(850, () => { history.value = [...history.value, outcome].slice(-5); result.value = outcome ? '落在月色这一面。' : '落在阳光这一面。'; burst(outcome ? '☾' : '✧') })
  }
}
function gesturePlay(type, gesture) {
  if (props.kind === 'cat') pet(type === 'hold' ? 2 : 1)
  else if (props.kind === 'windmill') blow(type === 'hold' ? gesture.duration / 220 : Math.abs(gesture.dx) / 12, type === 'swipe' && gesture.dx < 0 ? -1 : 1)
  else if (props.kind === 'star' && type === 'hold') collectStars(true)
  else if (type === 'hold') activate()
}
function clean() {
  clearTimeout(timer); clearTimeout(particleTimer); clearInterval(rollTimer)
  timer = null; particleTimer = null; rollTimer = null
  particles.value = []; meteor.value = false; playing.value = false; busy.value = false; stopBubbles(); cancel()
}
watch(() => props.resetKey, () => {
  clean(); affection.value = 0; starCount.value = 0; bubbleCells.value = Array(9).fill(false); history.value = []; rounds.value = 0; wins.value = 0; turn.value = 0; face.value = 1; coinSide = 0; result.value = ''
  reset()
})
function visibilityChanged() { if (document.hidden) clean() }
onMounted(() => { document.addEventListener('visibilitychange', visibilityChanged); window.addEventListener('blur', clean) })
onUnmounted(() => { clean(); document.removeEventListener('visibilitychange', visibilityChanged); window.removeEventListener('blur', clean) })
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
.windmill-blades { transform-origin: 40px 36px; transform: rotate(var(--toy-turn)); transition: transform var(--spin-time) cubic-bezier(.12,.65,.15,1); fill: var(--toy-pink); stroke: var(--toy-line); stroke-width: .7; }
.windmill-blades path:nth-child(even) { fill: var(--toy-pale); }
.windmill-pin { fill: var(--toy-glow); stroke: var(--toy-line); }
.dice-art { position: relative; width: 58px; height: 58px; margin: 7px; border: 1px solid var(--toy-line); border-radius: 15px; background: linear-gradient(135deg,var(--toy-pale),rgba(239,214,249,.64)); box-shadow: inset -4px -4px 0 rgba(124,86,147,.08); transform: rotate(-9deg); }
.dice-dot { position: absolute; width: 7px; height: 7px; margin: -3.5px; border-radius: 50%; background: var(--toy-ink); }
.is-playing .dice-art { animation: toy-roll 500ms ease; }
.coin-art { position: relative; width: 64px; height: 64px; margin: 4px; transform-style: preserve-3d; transform: perspective(400px) rotateY(var(--toy-turn)); transition: transform 850ms cubic-bezier(.2,.7,.25,1); filter: none; }
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
.toy-caption p { margin: 7px 0 0; color: #685674; font-size: 11px; line-height: 1.6; }
.toy-caption .toy-help { min-height: 35px; color: #60456f; }
.toy-caption .toy-result { min-height: 34px; margin-top: 4px; color: #81648e; }
.toy-handle:disabled { cursor: wait; opacity: 1; }
.is-charged { filter: drop-shadow(0 0 7px rgba(209,162,230,.5)); }
.coin-lift { display: block; width: 100%; height: 100%; }
.is-playing .coin-lift { animation: coin-toss 850ms ease-in-out; }
.play-particle { position: absolute; left: 50%; top: 46%; z-index: 4; color: #bd72ba; font-size: 14px; pointer-events: none; animation: play-burst 1150ms var(--delay) ease-out both; }
.constellation { position: absolute; inset: 0; width: 100%; height: 100%; fill: rgba(138,104,162,.15); stroke: rgba(149,106,177,.35); stroke-width: 1; pointer-events: none; }
.constellation polyline { fill: none; }
.constellation .is-collected { fill: #bd92d3; stroke: #a57db9; }
.shooting-star { position: absolute; top: 8%; left: 5%; color: #dcae53; pointer-events: none; z-index: 4; animation: meteor-flight 1s ease-out both; }
[data-toy="bubble"] .toy-stage { height: 136px; }
.bubble-sheet { display: grid; grid-template-columns: repeat(3,44px); position: relative; width: 132px; margin: 0 auto; padding: 2px 0; touch-action: none; }
.bubble-cell { display: grid; place-items: center; width: 44px; height: 44px; padding: 0; border: 0; background: transparent; cursor: pointer; touch-action: none; }
.bubble-cell span { width: 34px; height: 34px; border: 1px solid rgba(170,132,194,.65); border-radius: 50%; background: radial-gradient(circle at 30% 25%,rgba(255,255,255,.93) 0 6%,rgba(246,235,255,.2) 22%,rgba(205,172,229,.22) 75%); box-shadow: inset -2px -3px 5px rgba(167,120,196,.12); transition: transform 130ms, background 130ms; }
.bubble-cell.is-popped span { transform: scale(.72); background: rgba(130,95,152,.05); box-shadow: inset 1px 1px 4px rgba(111,76,131,.15); border-style: dashed; opacity: .5; }
.toy-action,.dice-choices button { min-height: 44px; padding: 6px 12px; border: 1px solid rgba(145,104,171,.22); border-radius: 999px; background: rgba(255,255,255,.15); color: var(--toy-ink); font: inherit; font-size: 11px; cursor: pointer; }
.toy-action { width: 100%; }
.toy-action:hover,.dice-choices button:hover { background: rgba(244,227,253,.45); }
.toy-action:focus-visible,.bubble-cell:focus-visible,.dice-choices button:focus-visible { outline: 2px solid var(--toy-ink); outline-offset: 2px; }
.dice-choices { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 6px; }
.dice-choices button { padding: 6px 2px; }
.dice-choices button[aria-pressed="true"] { background: rgba(208,170,231,.45); border-color: rgba(145,104,171,.5); }
.affection,.star-progress { display: flex; justify-content: center; gap: 6px; min-height: 21px; color: rgba(140,100,161,.23); font-size: 13px; }
.affection .filled { color: #c27ab1; }
.star-progress .filled { color: #bb914b; }
.charge-meter { height: 4px; margin: 9px 14px 12px; border-radius: 4px; background: rgba(145,104,171,.12); overflow: hidden; }
.charge-meter span { display: block; width: 100%; height: 100%; background: #b082ca; transform: scaleX(0); transform-origin: left; }
.charge-meter.charging span { animation: wind-charge 1.2s linear forwards; }
.coin-history { display: flex; justify-content: center; gap: 5px; min-height: 22px; }
.coin-history span { display: grid; place-items: center; width: 20px; height: 20px; border-radius: 50%; border: 1px solid rgba(145,104,171,.25); background: rgba(255,245,222,.4); color: #896f4c; font-size: 10px; }
@keyframes toy-bounce { 25% { transform: translateY(-7px) rotate(-6deg); } 65% { transform: translateY(1px) rotate(4deg); } }
@keyframes play-burst { 0% { opacity: 0; transform: translate(-50%,-50%) scale(.5); } 15% { opacity: 1; } 100% { opacity: 0; transform: translate(calc(-50% + var(--px)),calc(-50% + var(--py))) scale(.8); } }
@keyframes coin-toss { 40% { transform: translateY(-24px) scale(.9); } 75% { transform: translateY(3px); } }
@keyframes meteor-flight { 0% { opacity: 0; transform: translate(0,0) scale(.6); } 20% { opacity: 1; } 100% { opacity: 0; transform: translate(105px,74px) scale(1); } }
@keyframes wind-charge { to { transform: scaleX(1); } }
@keyframes toy-roll { 35% { transform: rotate(20deg) scale(.88); } 70% { transform: rotate(-20deg); } }
@media(max-width:480px) { .desk-toy { width: 132px; } .toy-stage { height: 104px; } .toy-handle { width: 72px; height: 72px; } .dice-art { width: 54px; height: 54px; margin: 5px; } .coin-art { width: 58px; height: 58px; margin: 3px; } }
@media(prefers-reduced-motion:reduce) { .toy-handle,.windmill-blades,.coin-art,.star-shape,.bubble-cell span { transition: none; } .toy-art,.coin-lift,.play-particle,.shooting-star { animation: none !important; } .play-particle,.shooting-star { display: none; } .charge-meter.charging span { animation: none; transform: scaleX(1); } }
</style>
