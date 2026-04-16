<template>
  <article class="article-card glass-card" :style="cardStyle">
    <!-- 封面图片 -->
    <div class="article-cover" v-if="article.cover_image">
      <div class="skeleton-loader" v-if="!imageLoaded"></div>
      <img 
        :src="article.cover_image" 
        :alt="article.title"
        @load="imageLoaded = true"
        :class="{ 'loaded': imageLoaded }"
        loading="lazy"
      />
    </div>
    
    <!-- 文章内容 -->
    <div class="article-content">
      <!-- 分类标签 -->
      <span class="article-category" v-if="article.category">
        {{ article.category.name }}
      </span>
      
      <!-- 标题 -->
      <h3 class="article-title">
        <router-link :to="`/article/${article.id}`">
          {{ article.title }}
        </router-link>
      </h3>
      
      <!-- 摘要 -->
      <p class="article-summary" v-if="article.summary">
        {{ article.summary }}
      </p>
      
      <!-- 底部元信息 -->
      <div class="article-meta">
        <span class="meta-item">
          <el-icon><View /></el-icon>
          {{ article.views }}
        </span>
        <span class="meta-item">
          <el-icon><Star /></el-icon>
          {{ article.likes }}
        </span>
        <span class="meta-item">
          <el-icon><Clock /></el-icon>
          {{ formatRelativeDate(article.created_at) }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { ref, computed } from 'vue'
import { View, Star, Clock } from '@element-plus/icons-vue'
import { formatRelativeDate } from '@/utils/date'

const props = defineProps({
  article: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0
  }
})

const imageLoaded = ref(false)

const cardStyle = computed(() => ({
  animationDelay: `${props.index * 0.1}s`
}))
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.article-card {
  overflow: hidden;
  animation: fadeInUp 0.6s cubic-bezier(0.25, 0.8, 0.25, 1) backwards;
}

.article-cover {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: var(--radius-card) var(--radius-card) 0 0;
  
  .skeleton-loader {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
      rgba(255, 255, 255, 0.05) 25%, 
      rgba(255, 255, 255, 0.1) 50%, 
      rgba(255, 255, 255, 0.05) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: var(--transition-smooth);
    
    &.loaded {
      opacity: 1;
    }
  }
  
  &:hover img {
    transform: scale(1.1);
  }
}

.article-content {
  padding: var(--spacing-md);
}

.article-category {
  display: inline-block;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-pink));
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.article-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  line-height: 1.4;
  
  a {
    color: var(--text-primary);
    text-decoration: none;
    transition: var(--transition-fast);
    
    &:hover {
      color: var(--primary-light);
    }
  }
}

.article-summary {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: var(--spacing-md);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: var(--spacing-md);
  padding-top: var(--spacing-sm);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: var(--text-muted);
    font-size: 0.75rem;
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
