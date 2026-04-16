<template>
  <section class="hero">
    <div class="hero-content">
      <!-- 打字机标题 -->
      <h1 class="hero-title">
        <span class="typed-text">{{ displayText }}</span>
        <span class="cursor" :class="{ 'typing': isTyping }">|</span>
      </h1>
      
      <!-- 个性签名 -->
      <p class="hero-subtitle" :class="{ 'fade-in': typingComplete }">
        {{ subtitle }}
      </p>
      
      <!-- CTA 按钮 -->
      <div class="hero-actions" :class="{ 'fade-in': typingComplete }">
        <router-link to="/articles" class="btn-primary">
          <el-icon><Document /></el-icon>
          <span>浏览文章</span>
        </router-link>
        <a href="#about" class="btn-glass">
          <el-icon><InfoFilled /></el-icon>
          <span>了解更多</span>
        </a>
      </div>
    </div>
    
    <!-- 装饰性元素 -->
    <div class="hero-decoration">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, InfoFilled } from '@element-plus/icons-vue'

const titleText = '欢迎来到沛心的博客'
const subtitle = '探索技术之美，记录生活点滴 ✨'

const displayText = ref('')
const isTyping = ref(true)
const typingComplete = ref(false)

// 打字机效果
const typeText = async () => {
  for (let i = 0; i < titleText.length; i++) {
    displayText.value += titleText[i]
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  isTyping.value = false
  typingComplete.value = true
}

onMounted(() => {
  setTimeout(typeText, 500)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: var(--spacing-xxl) var(--spacing-lg);
}

.hero-content {
  text-align: center;
  z-index: 1;
  max-width: 800px;
}

.hero-title {
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
  line-height: 1.2;
  min-height: 1.2em;
  
  .typed-text {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-pink), var(--secondary-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .cursor {
    display: inline-block;
    width: 3px;
    height: 1em;
    background: var(--primary-color);
    margin-left: 2px;
    vertical-align: text-bottom;
    
    &.typing {
      animation: cursor-blink 0.8s ease-in-out infinite;
    }
  }
}

.hero-subtitle {
  font-size: clamp(1.125rem, 3vw, 1.5rem);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xl);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &.fade-in {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) 0.2s;
  
  &.fade-in {
    opacity: 1;
    transform: translateY(0);
  }
  
  a {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: 1rem;
  }
}

// 装饰性浮动元素
.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  
  &.shape-1 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, var(--primary-color), transparent);
    top: 10%;
    left: -10%;
    animation: float 20s ease-in-out infinite;
  }
  
  &.shape-2 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, var(--secondary-pink), transparent);
    bottom: 10%;
    right: -10%;
    animation: float 25s ease-in-out infinite reverse;
  }
  
  &.shape-3 {
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, var(--secondary-blue), transparent);
    top: 50%;
    right: 20%;
    animation: float 15s ease-in-out infinite;
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(20px, 10px) scale(1.05);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .hero {
    min-height: 80vh;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
    
    a {
      width: 100%;
      max-width: 280px;
      justify-content: center;
    }
  }
}
</style>
