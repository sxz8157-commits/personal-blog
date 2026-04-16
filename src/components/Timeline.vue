<template>
  <div class="timeline-section">
    <h3 class="section-title">
      <el-icon><Timer /></el-icon>
      开发进度
    </h3>
    
    <div class="timeline">
      <div 
        v-for="(item, index) in timelineItems" 
        :key="index"
        class="timeline-item"
        :class="{ 'completed': item.completed, 'active': item.active }"
      >
        <div class="timeline-marker">
          <div class="marker-dot"></div>
          <div class="marker-line" v-if="index < timelineItems.length - 1"></div>
        </div>
        
        <div class="timeline-content">
          <h4 class="timeline-title">{{ item.title }}</h4>
          <p class="timeline-description">{{ item.description }}</p>
          <span class="timeline-date">{{ item.date }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Timer } from '@element-plus/icons-vue'

const timelineItems = [
  {
    title: '项目启动',
    description: '确定技术栈和项目架构',
    date: '2026-03-01',
    completed: true,
    active: false
  },
  {
    title: '后端开发',
    description: 'Flask API 与数据库设计',
    date: '2026-03-15',
    completed: true,
    active: false
  },
  {
    title: '前端实现',
    description: 'Vue 3 组件与毛玻璃 UI',
    date: '2026-03-30',
    completed: true,
    active: true
  },
  {
    title: '功能完善',
    description: '动画优化与响应式适配',
    date: '2026-04-10',
    completed: false,
    active: false
  },
  {
    title: '正式上线',
    description: '部署上线与性能优化',
    date: '2026-04-20',
    completed: false,
    active: false
  }
]
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.timeline-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: 1.5rem;
    margin-bottom: var(--spacing-lg);
    color: var(--text-primary);
  }
}

.timeline {
  position: relative;
  padding-left: var(--spacing-lg);
}

.timeline-item {
  position: relative;
  padding-bottom: var(--spacing-lg);
  
  &.completed {
    .marker-dot {
      background: var(--primary-color);
      box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.2);
    }
  }
  
  &.active {
    .marker-dot {
      background: var(--secondary-pink);
      box-shadow: 0 0 0 4px rgba(236, 72, 153, 0.2);
      animation: pulse 2s infinite;
    }
  }
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0;
  
  .marker-dot {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--text-muted);
    position: relative;
    z-index: 1;
    transition: var(--transition-fast);
  }
  
  .marker-line {
    position: absolute;
    left: 50%;
    top: 16px;
    width: 2px;
    height: calc(100% + var(--spacing-lg) - 16px);
    background: linear-gradient(180deg, var(--primary-color), transparent);
    transform: translateX(-50%);
  }
}

.timeline-content {
  padding: var(--spacing-md);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: var(--glass-border);
  border-radius: var(--radius-card);
  transition: var(--transition-smooth);
  
  &:hover {
    transform: translateX(5px);
    border-color: rgba(168, 85, 247, 0.3);
  }
}

.timeline-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.timeline-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.timeline-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}
</style>
