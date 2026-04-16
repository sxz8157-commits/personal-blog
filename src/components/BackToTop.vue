<template>
  <transition name="back-to-top">
    <button 
      v-show="visible" 
      class="back-to-top-btn glass-card"
      @click="scrollToTop"
      aria-label="返回顶部"
    >
      <el-icon :size="24"><ArrowUp /></el-icon>
    </button>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ArrowUp } from '@element-plus/icons-vue'

const visible = ref(false)

const handleScroll = () => {
  visible.value = window.scrollY > 500
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.back-to-top-btn {
  position: fixed;
  bottom: var(--spacing-xl);
  right: var(--spacing-xl);
  width: 50px;
  height: 50px;
  border-radius: var(--radius-pill);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-primary);
  border: 1px solid rgba(168, 85, 247, 0.3);
  box-shadow: var(--glass-shadow), 0 0 15px rgba(168, 85, 247, 0.2);
  z-index: 999;
  transition: var(--transition-smooth);
  
  &:hover {
    transform: translateY(-5px) scale(1.1);
    border-color: var(--primary-color);
    box-shadow: var(--glass-shadow), 0 0 25px rgba(168, 85, 247, 0.4);
    background: rgba(168, 85, 247, 0.3);
  }
}

// 过渡动画
.back-to-top-enter-active,
.back-to-top-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.back-to-top-enter-from,
.back-to-top-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
