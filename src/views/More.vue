<template>
  <div class="more-page">
    <div class="hollow-window">
      <section class="more-section">
        <!-- 标题 -->
        <div class="more-header fade-up" style="animation-delay: 0.1s">
          <h1 class="more-title">{{ pagesStore.text('more', 'title', '了解更多') }}</h1>
          <p class="more-subtitle text-readable">{{ pagesStore.text('more', 'subtitle', '探索博客背后的故事与技术') }}</p>
        </div>

        <!-- 开发日志 Timeline -->
        <div class="timeline-section fade-up" style="animation-delay: 0.2s">
          <h3 class="section-title text-readable">{{ pagesStore.text('more', 'logs_title', '开发日志') }}</h3>
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

        <p v-if="cardsLoading" class="content-load-status" role="status">正在加载项目与技术栈…</p>
        <div v-else-if="cardsError" class="content-load-status" role="status">
          {{ cardsError }} <button @click="loadCards" type="button">重新加载</button>
        </div>

        <!-- 项目展示区（使用介绍卡片数据） -->
        <div class="projects-section fade-up" style="animation-delay: 0.4s" v-if="!cardsLoading && introCards.length > 0">
          <h3 class="section-title text-readable">{{ pagesStore.text('more', 'projects_title', '我的项目') }}</h3>
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

    <!-- 保留隐藏的三连击入口，不显示公开的后台链接。 -->
    <div class="admin-trigger-zone" @click="handleTripleClick" title="三重点击进入后台管理"></div>
  </div>
</template>

<script setup>
import { usePagesStore } from '@/stores/pages';
const pagesStore = usePagesStore();
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';

const router = useRouter();
const clickCount = ref(0);
let clickTimer = null;

// 卡片数据
const introCards = ref([]);
const skillCards = ref([]);
const cardsLoading = ref(false);
const cardsError = ref('');

async function loadCards() {
  cardsLoading.value = true;
  cardsError.value = '';
  try {
    const data = await request.get('/api/cards');
    introCards.value = data?.intro_cards || [];
    skillCards.value = data?.skill_cards || [];
  } catch (err) {
    cardsError.value = '项目资料暂时加载失败';
    console.error('加载卡片失败:', err);
  } finally {
    cardsLoading.value = false;
  }
}

function handleTripleClick() {
  clickCount.value++;
  if (clickTimer) clearTimeout(clickTimer);
  clickTimer = setTimeout(() => { clickCount.value = 0; }, 600);
  if (clickCount.value >= 3) {
    clickCount.value = 0;
    router.push('/admin');
  }
}

onMounted(() => {
  loadCards();
});

const defaultTimelineLogs = [
  {
    date: '2026 年 10 月 4 日',
    title: '🗂 文章与文档统一管理',
    desc: '后台将文章和文档集中在一个入口，保留新建文章、草稿与发布，也能直接拖入文档上传和管理。'
  },
  {
    date: '2026 年 10 月 4 日',
    title: '🖼 拖拽上传文章封面',
    desc: '写文章时可以拖入或选择封面图片，上传后直接预览，无需手动填写图片地址。'
  },
  {
    date: '2026 年 10 月 4 日',
    title: '📖 更专注的文章阅读',
    desc: '电脑端固定标题、大纲与正文区域，阅读时只滚动内容；手机上的 PDF 可以直接在网站内阅读和翻页。'
  },
  {
    date: '2026 年 10 月 4 日',
    title: '📱 手机布局与加载优化',
    desc: '调整手机导航与页面比例，改用透明玻璃效果；压缩首屏资源并缓存常用资源，减少重复加载的等待。'
  },
  {
    date: '2026 年 10 月 4 日',
    title: '🎵 音乐信息与封面补全',
    desc: '音乐盒读取歌曲文件中的歌名、歌手和内嵌封面，保留上一首与下一首，并显示加载与播放状态。'
  },
  {
    date: '2026 年 10 月 3 日',
    title: '✍️ 内容后台与网站上线',
    desc: '加入文章草稿与发布、页面文案、个人介绍和媒体管理；博客上线，朋友可以通过安全连接访问。'
  }
];

const timelineLogs = computed(() => pagesStore.pages.more?.timeline ?? defaultTimelineLogs);
onUnmounted(() => { if (clickTimer) clearTimeout(clickTimer); });
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
  line-height: 1.7;
}

.content-load-status { color: #666; font-size: 14px; margin: 20px 0; }
.content-load-status button { color: #7c3aed; border: 0; background: #f1e7ff; padding: 8px 12px; border-radius: 8px; min-height: 44px; cursor: pointer; }

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
  .more-page { padding-top: 0; padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px)); min-height: calc(100svh - 56px); }
  .more-section { padding: 24px 16px; }
  .more-header { margin-bottom: 28px; }
  .more-title { font-size: 28px; line-height: 1.3; margin-bottom: 8px; }
  .more-subtitle { font-size: 14px; }
  .section-title { font-size: 20px; margin-bottom: 20px; }
  .timeline-section { margin-bottom: 28px; }
  .timeline { padding-left: 18px; }
  .timeline::before { left: 3px; }
  .timeline-dot { left: -20px; width: 12px; height: 12px; top: 12px; border-width: 2px; }
  .timeline-item { margin-bottom: 16px; }
  .timeline-card { padding: 16px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04); border-radius: 12px; }
  .timeline-date { font-size: 12px; line-height: 1.5; letter-spacing: 0; }
  .timeline-title { font-size: 16px; line-height: 1.5; overflow-wrap: anywhere; }
  .timeline-desc { font-size: 14px; line-height: 1.7; overflow-wrap: anywhere; }
  .tech-categories, .projects-grid { grid-template-columns: minmax(0, 1fr); gap: 12px; }
  .project-card, .tech-category { padding: 16px; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); }
  .project-name, .category-name { font-size: 16px; line-height: 1.5; }
  .project-desc, .tech-tag { font-size: 14px; line-height: 1.6; overflow-wrap: anywhere; }
  .project-arrow { opacity: 1; transform: none; }
  .projects-section, .tech-stack-section { margin-bottom: 28px; }
  .admin-trigger-zone { top: 64px; width: 36px; height: 36px; }
}

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
  .admin-trigger-zone { left: 16px; top: 84px; }
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
