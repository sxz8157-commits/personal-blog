<template>
  <div class="home">
    <!-- Hero 区域 -->
    <main class="hero-section">
      <section class="hero-content">
        <h1 class="hero-title fade-up" style="animation-delay: 0.1s">
          <span class="gradient-text">{{ displayText }}</span><span class="type-cursor" aria-hidden="true">|</span>
        </h1>
        <p class="hero-sub fade-up" style="animation-delay: 0.2s">从设计到代码，记录我的探索与赛博微光灵感。</p>

        <div class="hero-cta fade-up" style="animation-delay: 0.3s">
          <button class="btn btn-primary" @click="goArticles">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            阅读文章
          </button>
          <router-link to="/about" class="btn btn-ghost">了解更多</router-link>
        </div>
      </section>

      <!-- 隐藏的三重点击触发区域 -->
      <div
        class="admin-trigger-zone"
        @click="handleTripleClick"
      ></div>
    </main>

    <!-- 密码验证弹窗 -->
    <Teleport to="body">
      <transition name="dialog-fade">
        <div v-if="showPasswordDialog" class="dialog-overlay" @click.self="closePasswordDialog">
          <div class="password-dialog glass-card">
            <h3 class="dialog-title">管理员验证</h3>
            <p class="dialog-subtitle">请输入管理员密码</p>
            <input
              type="password"
              v-model="passwordInput"
              class="password-input"
              placeholder="请输入密码"
              @keyup.enter="verifyPassword"
              ref="passwordInputEl"
            />
            <div class="dialog-actions">
              <button class="btn btn-ghost" @click="closePasswordDialog">取消</button>
              <button class="btn btn-primary" @click="verifyPassword">确认</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const typedText = '欢迎来到沛心的博客';
const displayText = ref('');
let idx = 0;
let typingTimer = null;
let loopTimer = null;
let isDeleting = false;

// 三重点击计数器
const clickCount = ref(0);
let clickTimer = null;
const showPasswordDialog = ref(false);
const passwordInput = ref('');
const passwordInputEl = ref(null);
const CORRECT_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || '';

function handleTripleClick() {
  clickCount.value++;
  if (clickTimer) clearTimeout(clickTimer);
  clickTimer = setTimeout(() => {
    clickCount.value = 0;
  }, 600);

  if (clickCount.value >= 3) {
    clickCount.value = 0;
    showPasswordDialog.value = true;
    nextTick(() => {
      passwordInputEl.value?.focus();
    });
  }
}

function closePasswordDialog() {
  showPasswordDialog.value = false;
  passwordInput.value = '';
}

function verifyPassword() {
  if (passwordInput.value === CORRECT_PASSWORD) {
    closePasswordDialog();
    router.push('/admin');
  } else {
    passwordInput.value = '';
    alert('密码错误');
  }
}

function goArticles() {
  router.push('/articles');
}

// 打字循环动画
const startTypingLoop = () => {
  if (typingTimer) clearInterval(typingTimer);
  if (loopTimer) clearTimeout(loopTimer);

  idx = 0;
  displayText.value = '';
  isDeleting = false;

  typingTimer = setInterval(() => {
    if (!isDeleting) {
      idx++;
      displayText.value = typedText.slice(0, idx);
      if (idx >= typedText.length) {
        clearInterval(typingTimer);
        loopTimer = setTimeout(() => {
          isDeleting = true;
          startDeleting();
        }, 2000);
      }
    }
  }, 150);
};

const startDeleting = () => {
  typingTimer = setInterval(() => {
    idx--;
    displayText.value = typedText.slice(0, idx);
    if (idx <= 0) {
      clearInterval(typingTimer);
      loopTimer = setTimeout(() => {
        startTypingLoop();
      }, 1000);
    }
  }, 80);
};

onMounted(() => {
  startTypingLoop();
});

onUnmounted(() => {
  if (typingTimer) clearInterval(typingTimer);
  if (loopTimer) clearTimeout(loopTimer);
  if (clickTimer) clearTimeout(clickTimer);
});
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.home {
  min-height: calc(100vh - 68px);
  position: relative;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 68px);
  position: relative;
  z-index: 1;
  padding: 32px 24px;
}

.hero-content {
  text-align: center;
  max-width: 900px;
  width: 100%;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 4.2rem);
  line-height: 1.15;
  font-weight: 800;
  margin: 0 auto 16px;
  display: inline-block;
  color: #1a1a1a;

  .gradient-text {
    color: #1a1a1a;
    background: none;
    -webkit-background-clip: unset;
    background-clip: unset;
    -webkit-text-fill-color: unset;
    text-shadow: none;
    display: inline-block;
  }
}

.type-cursor {
  display: inline-block;
  width: 3px;
  height: 1.03em;
  margin-left: 6px;
  vertical-align: text-bottom;
  background: #1a1a1a;
  animation: blink 1s step-end infinite;
  will-change: opacity;
  border-radius: 1px;
}

.hero-sub {
  color: rgba(0, 0, 0, 0.65);
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
  padding: 14px 28px;
  transition: all 0.4s $ease-damped;
  will-change: transform, opacity;
  transform: translateZ(0);
  font-family: inherit;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  border-radius: 9999px;
  box-shadow: 0 4px 20px rgba(236, 72, 153, 0.4);

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 30px rgba(236, 72, 153, 0.5);
  }

  &:active { transform: scale(0.96); }

  svg { color: rgba(255, 255, 255, 0.9); }
}

.btn-ghost {
  background: rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #1a1a1a;
  border-radius: 12px;
  padding: 12px 24px;

  &:hover {
    transform: translateY(-3px);
    background: rgba(168, 85, 247, 0.08);
    box-shadow: 0 8px 22px rgba(168, 85, 247, 0.15);
    border-color: rgba(168, 85, 247, 0.25);
  }

  &:active { transform: scale(0.96); }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-up {
  opacity: 0;
  transform: translateY(24px);
  animation: fadeUp 0.72s $ease-damped forwards;
  will-change: transform, opacity;
}

@keyframes blink {
  50% { opacity: 0; }
}

// ===== 隐藏触发区域（不影响样式）=====
.admin-trigger-zone {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 30px;
  height: 30px;
  z-index: 0;
  opacity: 0;
  cursor: default;
}

// ===== 密码弹窗样式 =====
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.password-dialog {
  background: rgba(255, 255, 255, 0.65) !important;
  padding: 32px;
  border-radius: 20px;
  min-width: 320px;
  max-width: 90%;
}

.dialog-title {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
  color: #1a1a1a;
}

.dialog-subtitle {
  margin: 0 0 20px 0;
  color: rgba(0, 0, 0, 0.6);
  font-size: 0.9rem;
}

.password-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  margin-bottom: 20px;

  &:focus {
    border-color: #a855f7;
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.15);
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: all 0.3s $ease-damped;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .hero-section { padding: 24px 16px; }
  .hero-title { font-size: 1.8rem; }
  .hero-sub { font-size: 0.95rem; }
  .hero-cta { flex-direction: column; align-items: center; gap: 12px; }
  .btn { width: 100%; max-width: 280px; }
}
</style>