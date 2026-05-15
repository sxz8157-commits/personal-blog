<template>
  <div class="more-page">
    <div class="hollow-window">
      <section class="more-section">
        <!-- 标题 -->
        <div class="more-header fade-up" style="animation-delay: 0.1s">
          <h1 class="more-title">了解更多</h1>
          <p class="more-subtitle text-readable">探索博客背后的故事与技术</p>
        </div>

        <!-- 开发日志 Timeline -->
        <div class="timeline-section fade-up" style="animation-delay: 0.2s">
          <h3 class="section-title text-readable">开发日志</h3>
          <div class="timeline">
            <div class="timeline-item" v-for="(log, index) in timelineLogs" :key="index">
              <div class="timeline-dot"></div>
              <div class="timeline-card glass-card">
                <div class="timeline-date">{{ log.date }}</div>
                <h4 class="timeline-title text-readable">{{ log.title }}</h4>
                <p class="timeline-desc text-readable">{{ log.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 项目展示区（使用介绍卡片数据） -->
        <div class="projects-section fade-up" style="animation-delay: 0.4s" v-if="!cardsLoading && introCards.length > 0">
          <h3 class="section-title text-readable">我的项目</h3>
          <div class="projects-grid">
            <template v-for="card in introCards" :key="card.id">
              <a
                v-if="card.link && card.link !== '#'"
                :href="card.link"
                target="_blank"
                rel="noopener noreferrer"
                class="project-card glass-card"
              >
                <div class="project-info">
                  <h4 class="project-name text-readable">{{ card.title }}</h4>
                  <p class="project-desc text-readable">{{ card.description || '暂无描述' }}</p>
                </div>
                <div class="project-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M7 17L17 7M17 7H7M17 7v10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </a>
              <div v-else class="project-card glass-card project-card--static">
                <div class="project-info">
                  <h4 class="project-name text-readable">{{ card.title }}</h4>
                  <p class="project-desc text-readable">{{ card.description || '暂无描述' }}</p>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 技能书展示区 -->
        <div class="tech-stack-section fade-up" style="animation-delay: 0.3s" v-if="!cardsLoading && skillCards.length > 0">
          <h3 class="section-title text-readable">技术栈</h3>
          <div class="tech-categories">
            <div class="tech-category glass-card" v-for="cat in skillCards" :key="cat.id">
              <div class="category-content">
                <h4 class="category-name text-readable">{{ cat.title }}</h4>
                <div class="tech-tags">
                  <span class="tech-tag text-readable">{{ cat.description || '暂无描述' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 隐藏的三重点击触发区域（放在 hollow-window 外面避免 overflow:hidden 影响） -->
    <div
      class="admin-trigger-zone"
      @click="handleTripleClick"
      title="三重点击进入后台管理"
    ></div>

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
import { ref, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';

const router = useRouter();

// 三重点击计数器
const clickCount = ref(0);
let clickTimer = null;
const showPasswordDialog = ref(false);
const passwordInput = ref('');
const passwordInputEl = ref(null);
const CORRECT_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || '';

// 卡片数据
const introCards = ref([]);
const skillCards = ref([]);
const cardsLoading = ref(false);

async function loadCards() {
  cardsLoading.value = true;
  try {
    const data = await request.get('/api/cards');
    introCards.value = data?.intro_cards || [];
    skillCards.value = data?.skill_cards || [];
  } catch (err) {
    console.error('加载卡片失败:', err);
  } finally {
    cardsLoading.value = false;
  }
}

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

onMounted(() => {
  loadCards();
});

const timelineLogs = [
  {
    date: '2026 年 4 月（本周）',
    title: '🛠 文章页重构为词云导航',
    desc: '文章列表改为 3D 词云入口，点击词云标题直接跳转文章详情；移除了词云内嵌小卡片并完成居中点击优化。'
  },
  {
    date: '2026 年 4 月',
    title: '🧾 Markdown 渲染层级修复',
    desc: '详情页 Markdown 解析升级，支持 # ~ ###### 标题层级、目录同步与列表/引用/代码块结构化渲染。'
  },
  {
    date: '2026 年 4 月',
    title: '🎵 音乐播放器切歌修复',
    desc: '修复“无法切换歌曲”问题，播放列表扩展为多首并改为顺序循环切换，上一首/下一首行为更符合直觉。'
  },
  {
    date: '2026 年 3 月',
    title: '📱 响应式与交互细节优化',
    desc: '完善移动端触控和布局，优化导航、卡片动效与页面加载反馈，提升整体浏览流畅度。'
  },
  {
    date: '2026 年 1 月',
    title: '🚀 项目初始化',
    desc: '基于 Vue 3 + Vite + Flask 搭建前后端分离架构，完成文章接口、详情渲染和基础页面框架。'
  }
];

</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.more-page {
  padding-top: 24px;
  padding-bottom: 80px;
  min-height: 100vh;
}

.more-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

// ===== 标题 =====
.more-header {
  text-align: center;
  margin-bottom: 48px;
}

.more-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.more-subtitle {
  color: rgba(0, 0, 0, 0.55);
  font-size: 1.1rem;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 28px;
  position: relative;
  display: inline-block;

  &::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -6px;
    width: 40px;
    height: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, #a855f7, #ec4899);
  }
}

// ===== 开发日志 Timeline =====
.timeline-section {
  margin-bottom: 56px;
}

.timeline {
  position: relative;
  padding-left: 32px;

  &::before {
    content: '';
    position: absolute;
    left: 7px;
    top: 8px;
    bottom: 8px;
    width: 2px;
    background: linear-gradient(180deg, rgba(168, 85, 247, 0.5), rgba(236, 72, 153, 0.3), transparent);
    border-radius: 2px;
  }
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-dot {
  position: absolute;
  left: -32px;
  top: 8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  border: 3px solid rgba(255, 255, 255, 0.8);
  z-index: 1;
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
}

.timeline-card {
  padding: 20px 24px;
}

.timeline-date {
  font-size: 0.8rem;
  font-weight: 600;
  color: #a855f7;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.timeline-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.timeline-desc {
  color: rgba(0, 0, 0, 0.55);
  font-size: 0.9rem;
  line-height: 1.7;
}

// ===== 技术栈 =====
.tech-stack-section {
  margin-bottom: 40px;
}

.tech-categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.tech-category {
  display: flex;
  gap: 16px;
  padding: 20px;
  align-items: flex-start;
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.category-content {
  flex: 1;
  min-width: 0;
}

.category-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 10px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tech-tag {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: rgba(0, 0, 0, 0.65);
  transition: all 0.3s $ease-damped;

  &:hover {
    background: rgba(168, 85, 247, 0.15);
    border-color: rgba(168, 85, 247, 0.3);
    color: #c084fc;
  }
}

// ===== 项目展示区 =====
.projects-section {
  margin-bottom: 40px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.project-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  text-decoration: none;
  color: inherit;
  transition: all 0.4s $ease-damped;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 32px rgba(168, 85, 247, 0.2),
                0 6px 20px rgba(0, 0, 0, 0.15);
  }

  .project-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .project-info {
    flex: 1;
    min-width: 0;
  }

  .project-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 4px;
  }

  .project-desc {
    font-size: 0.82rem;
    color: rgba(0, 0, 0, 0.55);
    line-height: 1.5;
  }

  .project-arrow {
    color: #a855f7;
    opacity: 0;
    transform: translateX(-8px);
    transition: all 0.3s $ease-damped;
    flex-shrink: 0;
  }

  &:hover .project-arrow {
    opacity: 1;
    transform: translateX(0);
  }
}

.project-card--static {
  cursor: default;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(168, 85, 247, 0.12);
  }
}

// ===== 淡入动画 =====
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-up {
  opacity: 0;
  transform: translateY(24px);
  animation: fadeUp 0.72s $ease-damped forwards;
  will-change: transform, opacity;
}

@media (max-width: 640px) {
  .more-section { padding: 0 1rem; }
  .tech-categories { grid-template-columns: 1fr; }
  .timeline { padding-left: 24px; }
  .timeline-dot { left: -24px; }
}

// ===== 隐藏触发区域（不影响样式）- 固定在页面左上角 =====
.admin-trigger-zone {
  position: fixed;
  top: 84px;
  left: calc((100% - 54%) / 2);
  width: 60px;
  height: 60px;
  z-index: 10;
  opacity: 0;
  cursor: pointer;
}

@media (max-width: 768px) {
  .admin-trigger-zone {
    left: 16px;
    top: 84px;
  }
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
  font-family: inherit;

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

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
  padding: 10px 20px;
  transition: all 0.3s $ease-damped;
  font-family: inherit;
  text-decoration: none;
  border-radius: 12px;
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;

  &:hover {
    transform: scale(1.05);
  }
}

.btn-ghost {
  background: rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #1a1a1a;

  &:hover {
    transform: translateY(-2px);
    background: rgba(168, 85, 247, 0.08);
    border-color: rgba(168, 85, 247, 0.25);
  }
}
</style>
