<template>
  <div class="stats-card glass-card">
    <div class="stats-icon" :style="{ background: iconGradient }">
      <el-icon :size="32">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stats-content">
      <div class="stats-value" :class="{ 'animate-number': animate }">
        <CountUp :endValue="value" :duration="2" />
      </div>
      <div class="stats-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    default: 0
  },
  iconGradient: {
    type: String,
    default: 'linear-gradient(135deg, #a855f7, #ec4899)'
  }
})

const animate = ref(false)

onMounted(() => {
  setTimeout(() => {
    animate.value = true
  }, 300)
})
</script>

<script>
// CountUp 简易实现
import { defineComponent, h, ref, onMounted, watch } from 'vue'

export const CountUp = defineComponent({
  props: {
    endValue: { type: Number, default: 0 },
    duration: { type: Number, default: 2 }
  },
  setup(props) {
    const displayValue = ref(0)
    
    const animateValue = () => {
      const startTime = performance.now()
      const startValue = 0
      const endValue = props.endValue
      
      const updateValue = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / (props.duration * 1000), 1)
        
        // 使用 easeOutQuart 缓动函数
        const easeProgress = 1 - Math.pow(1 - progress, 4)
        displayValue.value = Math.floor(startValue + (endValue - startValue) * easeProgress)
        
        if (progress < 1) {
          requestAnimationFrame(updateValue)
        } else {
          displayValue.value = endValue
        }
      }
      
      requestAnimationFrame(updateValue)
    }
    
    onMounted(() => {
      setTimeout(animateValue, 500)
    })
    
    watch(() => props.endValue, animateValue)
    
    return () => h('span', displayValue.value.toString())
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.stats-card {
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.stats-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: var(--spacing-xs);
}

.stats-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}
</style>
