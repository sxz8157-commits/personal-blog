<template>
  <div class="about-page">
    <div class="hollow-window">
      <section class="about-section">
        <!-- 个人简介 -->
        <div class="about-header fade-up" style="animation-delay: 0.1s">
          <h1 class="about-title">关于我</h1>
          <p class="about-subtitle text-readable">在代码与像素之间，构建属于自己的赛博世界</p>
        </div>

        <div class="about-content">
          <!-- 个人介绍卡片 -->
          <div class="about-intro glass-card fade-up" style="animation-delay: 0.2s">
            <div class="intro-avatar">
              <!-- 确保src是 / 开头的根路径，文件名和服务器里的完全一致 -->
              <img src="/toux/img.png" alt="沛心头像" />
            </div>
            <div class="intro-text">
              <h2 class="intro-name">{{ aboutData.intro.name }}</h2>
              <p class="intro-desc text-readable">
                {{ aboutData.intro.subtitle }}
              </p>
              <p class="intro-bio text-readable">
                {{ aboutData.intro.bio }}
              </p>
              <div class="intro-tags">
                <span class="tag text-readable" v-for="tag in aboutData.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <!-- 技能树 -->
          <div class="skills-section fade-up" style="animation-delay: 0.3s">
            <h3 class="section-title text-readable">技能树</h3>
            <div class="skills-grid">
              <div class="skill-card glass-card" v-for="skill in aboutData.skills" :key="skill.name">
                <div class="skill-header">
                  <span class="skill-name text-readable">{{ skill.name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 联系方式卡片 -->
          <div class="contact-card glass-card fade-up" style="animation-delay: 0.4s">
            <h3 class="section-title text-readable">联系我</h3>
            <div class="contact-links">
              <a :href="'mailto:' + aboutData.contact.email" class="contact-link" target="_blank" rel="noopener">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="4" width="20" height="16" rx="3" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M2 7l10 6 10-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <span class="text-readable">{{ aboutData.contact.email }}</span>
              </a>
              <a :href="aboutData.contact.github" class="contact-link" target="_blank" rel="noopener">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                <span class="text-readable">GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '@/utils/request';

// 关于页面数据
const aboutData = ref({
  intro: {
    name: '沛心',
    subtitle: '全栈开发者 / 赛博美学探索者 / 代码诗人',
    bio: '我是一名热爱技术与艺术交汇的开发者。在这里，我用代码编织梦想，用像素绘制灵感。从前端交互的丝滑动效，到后端逻辑的精妙设计，每一个细节都是对完美的追求。欢迎来到我的数字花园，这里记录着我在赛博空间中的每一次探索与成长。'
  },
  tags: ['Vue 3', 'Flask', 'Node.js', 'Python', '爬虫', 'UI/UX', '全栈开发', '开源贡献'],
  skills: [
    { name: 'Vue 3 / Composition API', delay: '0.1s' },
    { name: 'JavaScript / TypeScript', delay: '0.15s' },
    { name: 'CSS / SCSS / Tailwind', delay: '0.2s' },
    { name: 'Node.js / Express', delay: '0.25s' },
    { name: 'Python / Flask', delay: '0.3s' },
    { name: 'UI/UX 设计', delay: '0.35s' },
    { name: '数据库 (SQL / MySQL)', delay: '0.4s' },
    { name: 'requests / BeautifulSoup(BS4) 爬虫', delay: '0.45s' },
  ],
  contact: {
    email: 'zzzppx@hotmail.com',
    github: 'https://github.com/sxz8157-commits'
  }
});

async function loadAboutData() {
  try {
    const data = await request.get('/api/about');
    console.log('关于页面 API 返回数据:', data);

    // 处理个人简介
    if (data.intro && data.intro.length > 0) {
      const intro = {};
      for (const item of data.intro) {
        intro[item.key] = item.value;
      }
      aboutData.value.intro = {
        name: intro.name || '沛心',
        subtitle: intro.subtitle || '',
        bio: intro.bio || ''
      };
    }

    // 处理技能标签
    if (data.tags && data.tags.length > 0) {
      aboutData.value.tags = data.tags.map(item => item.value);
    }

    // 处理技能树
    if (data.skills && data.skills.length > 0) {
      aboutData.value.skills = data.skills.map((item, index) => ({
        name: item.value,
        delay: `${0.1 + index * 0.05}s`
      }));
    }

    // 处理联系方式
    if (data.contact && data.contact.length > 0) {
      const contact = {};
      for (const item of data.contact) {
        contact[item.key] = item.value;
      }
      aboutData.value.contact = {
        email: contact.email || 'zzzppx@hotmail.com',
        github: contact.github || 'https://github.com/sxz8157-commits'
      };
    }
  } catch (err) {
    console.error('加载关于页面数据失败:', err);
  }
}

onMounted(() => {
  loadAboutData();
});
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.about-page {
  padding-top: 24px;
  padding-bottom: 80px;
  min-height: 100vh;
}

.about-section {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

// ===== 标题 =====
.about-header {
  text-align: center;
  margin-bottom: 48px;
}

.about-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.about-subtitle {
  color: rgba(0, 0, 0, 0.55);
  font-size: 1.1rem;
}

// ===== 个人介绍 =====
.about-intro {
  display: flex;
  gap: 32px;
  padding: 32px;
  margin-bottom: 40px;
  align-items: flex-start;
}

.intro-avatar {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
  border-radius: 24px;
  overflow: hidden;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.25);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.intro-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.intro-desc {
  font-size: 0.95rem;
  color: #a855f7;
  font-weight: 600;
  margin-bottom: 12px;
}

.intro-bio {
  color: rgba(0, 0, 0, 0.65);
  line-height: 1.8;
  font-size: 0.95rem;
  margin-bottom: 20px;
}

.intro-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 14px;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.18);
  color: #7c3aed;
  transition: all 0.3s $ease-damped;

  &:hover {
    background: rgba(168, 85, 247, 0.25);
    border-color: rgba(168, 85, 247, 0.4);
    transform: translateY(-2px);
  }
}

// ===== 技能树 =====
.skills-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 20px;
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

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.skill-card {
  padding: 20px;

  .skill-header {
    margin-bottom: 0;
  }

  .skill-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: rgba(0, 0, 0, 0.8);
  }
}

// ===== 联系方式 =====
.contact-card {
  padding: 32px;
}

.contact-links {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 12px;
}

.contact-link {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.06);
  color: rgba(0, 0, 0, 0.75);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.4s $ease-damped;
  will-change: transform;

  svg {
    color: #a855f7;
    flex-shrink: 0;
  }

  &:hover {
    background: rgba(168, 85, 247, 0.12);
    border-color: rgba(168, 85, 247, 0.3);
    color: #fff;
    transform: translateX(6px);
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
  .about-section { padding: 0 1rem; }
  .about-intro { flex-direction: column; align-items: center; text-align: center; padding: 24px; }
  .intro-tags { justify-content: center; }
  .skills-grid { grid-template-columns: 1fr; }
}
</style>
