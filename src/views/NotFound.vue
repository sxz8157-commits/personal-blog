<template>
  <div class="not-found-page">
    <div class="not-found-content glass-card">
      <div class="error-code">404</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-description">
        抱歉，您访问的页面不存在或已被移除。
      </p>
      <div class="action-buttons">
        <router-link to="/" class="btn-primary">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="9 22 9 12 15 12 15 22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回首页
        </router-link>
        <router-link to="/articles" class="btn-ghost">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 7h8M8 11h8M8 15h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          浏览文章
        </router-link>
        <button @click="goBack" class="btn-ghost">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M5 12l6 6M5 12l6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回上一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.not-found-page {
  min-height: calc(100vh - 68px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.not-found-content {
  padding: 48px;
  text-align: center;
  border-radius: 24px;
  max-width: 600px;
  width: 100%;
}

.error-code {
  font-size: 7rem;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1;
  margin-bottom: 24px;
}

.error-title {
  font-size: 2rem;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.error-description {
  font-size: 1.05rem;
  color: rgba(0, 0, 0, 0.6);
  line-height: 1.6;
  margin-bottom: 32px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary,
.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 9999px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.4s $ease-damped;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  box-shadow: 0 4px 20px rgba(236, 72, 153, 0.3);

  &:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 30px rgba(236, 72, 153, 0.45);
  }
}

.btn-ghost {
  background: rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #1a1a1a;

  &:hover {
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.25);
    color: #a855f7;
    transform: translateY(-2px);
  }
}

@media (max-width: 640px) {
  .error-code { font-size: 5rem; }
  .error-title { font-size: 1.5rem; }
  .action-buttons { flex-direction: column; align-items: center; }
  .btn-primary, .btn-ghost { width: 100%; max-width: 280px; justify-content: center; }
  .not-found-content { padding: 32px 24px; }
}
</style>
