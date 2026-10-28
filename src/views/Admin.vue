<template>
  <div class="admin-page">
    <div v-if="checking" class="admin-login-wrap" role="status">正在检查登录状态…</div>
    <div v-else-if="!adminSession.authenticated" class="admin-login-wrap">
      <form class="admin-login" @submit.prevent="login">
        <div class="login-mark" aria-hidden="true">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M4 4h11l5 5v11H4V4Zm10 0v6h6M8 14h8M8 17h5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" /></svg>
        </div>
        <h1>后台登录</h1>
        <p class="login-description">管理你的文章、页面文案和媒体内容。</p>
        <label for="admin-password">管理员密码</label>
        <div class="password-field">
          <input id="admin-password" v-model="loginPassword" :type="passwordVisible ? 'text' : 'password'" required autocomplete="current-password" class="form-input" maxlength="256" placeholder="请输入管理员密码" :aria-invalid="Boolean(loginError)" :aria-describedby="loginError ? 'admin-login-error' : undefined" :disabled="loggingIn" @input="loginError = ''" />
          <button type="button" class="password-toggle" :aria-label="passwordVisible ? '隐藏密码' : '显示密码'" :title="passwordVisible ? '隐藏密码' : '显示密码'" :aria-pressed="passwordVisible" :disabled="loggingIn" @click="passwordVisible = !passwordVisible">
            <svg v-if="!passwordVisible" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" stroke="currentColor" stroke-width="1.7" /><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.7" /></svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m3 3 18 18M10.6 5.1 12 5c6.5 0 10 7 10 7a19 19 0 0 1-3.2 4M6.1 6.1A20 20 0 0 0 2 12s3.5 7 10 7a12 12 0 0 0 5.9-1.7M10 10a3 3 0 0 0 4 4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" /></svg>
          </button>
        </div>
        <p v-if="loginError" id="admin-login-error" class="login-error" role="alert">{{ loginError }}</p>
        <div class="login-actions">
          <button class="btn btn-primary" :disabled="loggingIn">{{ loggingIn ? '登录中…' : '登录' }}</button>
          <router-link to="/" class="btn btn-ghost">返回首页</router-link>
        </div>
      </form>
    </div>
    <div v-else class="admin-workspace">
      <div class="admin-header">
        <div class="admin-title-area">
          <h1 class="admin-title">后台管理</h1>
          <p class="admin-subtitle">管理文章、页面文案、个人简介和媒体文件</p>
        </div>
        <div class="admin-header-actions">
        <button class="btn btn-ghost" @click="goBack">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回首页
        </button>
        <button class="btn btn-ghost" @click="logout">退出登录</button>
        </div>
      </div>

      <div class="admin-body">
      <nav class="admin-tabs" aria-label="后台模块">
        <div v-for="group in navigationGroups" :key="group.label" class="admin-nav-group">
          <p class="admin-nav-label">{{ group.label }}</p>
        <button
          v-for="tab in tabs.filter(item => group.keys.includes(item.key))"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          :aria-current="activeTab === tab.key ? 'page' : undefined"
          @click="selectTab(tab.key)"
        >
          {{ tab.label }}
        </button>
        </div>
      </nav>

      <section class="admin-main" aria-label="内容编辑区">
      <div v-if="!['articles', 'pages'].includes(activeTab)" class="admin-section-heading">
        <h2>{{ tabs.find(tab => tab.key === activeTab)?.label }}</h2>
        <p>{{ sectionDescriptions[activeTab] }}</p>
      </div>

      <!-- 上传区域（非卡片和关于页面时显示） -->
      <div v-if="['background','audio'].includes(activeTab)" class="upload-zone" role="button" tabindex="0" aria-label="选择文件上传，也可以拖拽文件" @click="triggerFileInput" @keydown.enter.self.prevent="triggerFileInput" @keydown.space.self.prevent="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
        <input
          type="file"
          ref="fileInput"
          :accept="acceptTypes[activeTab]"
          multiple
          style="display: none"
          @change="handleFileSelect"
        />
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>点击或拖拽文件到此处上传</p>
        <p class="upload-hint">支持: {{ acceptExtensions[activeTab] }}</p>
      </div>

      <!-- 文件列表 -->
      <div class="file-list" :aria-busy="loading">
        <p v-if="loading" class="form-hint" role="status">正在加载内容…</p>
        <AdminArticles ref="articleEditor" v-if="activeTab === 'articles'" />
        <AdminPages ref="pageEditor" v-if="activeTab === 'pages'" />
        <!-- 背景文件列表（图片+视频） -->
        <div v-if="activeTab === 'background'" class="file-grid">
          <div v-for="item in fileList" :key="item.filename" class="file-card glass-card">
            <div class="file-preview" :class="item.isVideo ? 'video-preview' : 'image-preview'">
              <video v-if="item.isVideo" :src="item.url" muted loop playsinline preload="metadata" @click="$event.target.paused ? $event.target.play() : $event.target.pause()"></video>
              <img v-else :src="item.url" :alt="item.filename" @error="handleImageError" />
              <div v-if="item.isVideo" class="play-overlay">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="white">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
              </div>
            </div>
            <div class="file-info">
              <p class="file-name" :title="item.filename">{{ item.filename }}</p>
            </div>
            <div class="file-actions">
              <button class="action-btn danger" @click="deleteFile(item, 'background')" title="删除" aria-label="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <!-- 空状态 -->
          <div v-if="fileList.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" opacity="0.4">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="13 2 13 9 20 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>暂无文件</p>
          </div>
        </div>

        <!-- 音频列表 -->
        <div v-if="activeTab === 'audio'" class="file-list-view">
          <div v-for="item in fileList" :key="item.filename" class="file-list-item glass-card">
            <div class="file-icon audio-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="6" cy="18" r="3" fill="currentColor"/>
                <circle cx="18" cy="16" r="3" fill="currentColor"/>
              </svg>
            </div>
            <div class="file-info">
              <p class="file-name">{{ item.name }}</p>
              <p class="file-artist">{{ item.artist }}</p>
            </div>
            <div class="file-actions">
              <button class="action-btn danger" @click="deleteFile(item, 'audio')" title="删除" aria-label="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 卡片管理 -->
        <div v-if="activeTab === 'cards'" class="cards-admin">
          <!-- 添加卡片表单 -->
          <div class="card-form glass-card">
            <h4 class="form-title">添加新卡片</h4>
            <div class="form-row">
              <div class="form-group">
                <label for="card-title">标题</label>
                <input id="card-title" v-model="cardForm.title" type="text" class="form-input" placeholder="卡片标题" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="card-description">描述（可选）</label>
                <input id="card-description" v-model="cardForm.description" type="text" class="form-input" placeholder="卡片描述" />
              </div>
              <div class="form-group">
                <label for="card-link">链接（可选）</label>
                <input id="card-link" v-model="cardForm.link" type="text" class="form-input" placeholder="https://..." />
              </div>
            </div>
            <button class="btn btn-primary" @click="addCard" :disabled="!cardForm.title">
              添加卡片
            </button>
          </div>

          <!-- 网站卡片列表 -->
          <div class="cards-section">
            <div class="cards-section-header">
              <h4 class="cards-section-title">网站卡片</h4>
              <span class="cards-count">共 {{ introCards.length + skillCards.length + tagCards.length }} 个</span>
            </div>
            <div class="cards-list" v-if="introCards.length + skillCards.length + tagCards.length > 0">
              <div v-for="card in [...introCards, ...skillCards, ...tagCards]" :key="card.id" class="card-item glass-card">
                <div class="card-info">
                  <p class="card-title">{{ card.title }}</p>
                  <p class="card-desc">{{ card.description || '暂无描述' }}</p>
                </div>
                <div class="card-actions">
                  <span v-if="card.link" class="card-link-badge">有链接</span>
                  <button class="action-btn" @click="openEditDialog(card)" title="编辑" aria-label="编辑">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  <button class="action-btn danger" @click="deleteCard(card)" title="删除" aria-label="删除">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>暂无网站卡片</p>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && fileList.length === 0 && activeTab === 'audio'" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" opacity="0.4">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="13 2 13 9 20 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p>暂无文件</p>
        </div>

        <!-- 关于页面内容管理 -->
        <div v-if="activeTab === 'about'" class="about-admin">
          <h4 class="form-title">关于页面内容管理</h4>

          <!-- 个人简介 -->
          <div class="about-section">
            <h5 class="about-section-title">个人简介</h5>
            <div class="form-group">
              <label for="about-name">姓名</label>
              <input id="about-name" v-model="aboutForm.intro.name" type="text" class="form-input" placeholder="姓名" />
            </div>
            <div class="form-group">
              <label for="about-subtitle">副标题</label>
              <input id="about-subtitle" v-model="aboutForm.intro.subtitle" type="text" class="form-input" placeholder="例如：全栈开发者 / 赛博美学探索者" />
            </div>
            <div class="form-group">
              <label for="about-bio">个人简介</label>
              <textarea id="about-bio" v-model="aboutForm.intro.bio" class="form-input" rows="4" placeholder="个人简介内容"></textarea>
            </div>
          </div>

          <!-- 技能标签 -->
          <div class="about-section">
            <h5 class="about-section-title">技能标签 <span class="section-hint">（显示在个人简介卡片上）</span></h5>
            <div class="tag-list" v-if="aboutForm.tags.length > 0">
              <div v-for="(tag, index) in aboutForm.tags" :key="index" class="tag-item glass-card">
                <input v-model="aboutForm.tags[index]" type="text" class="tag-input" placeholder="标签名" :aria-label="`标签 ${index + 1}`" />
                <button class="action-btn danger" @click="removeAboutItem('tags', index)" title="删除" aria-label="删除">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
            <button class="btn btn-ghost" @click="addAboutItem('tags')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              添加标签
            </button>
          </div>

          <!-- 技能树 -->
          <div class="about-section">
            <h5 class="about-section-title">技能树 <span class="section-hint">（详细技能展示）</span></h5>
            <div class="tag-list" v-if="aboutForm.skills.length > 0">
              <div v-for="(skill, index) in aboutForm.skills" :key="index" class="tag-item glass-card">
                <input v-model="aboutForm.skills[index]" type="text" class="tag-input" placeholder="技能名称" :aria-label="`技能 ${index + 1}`" />
                <button class="action-btn danger" @click="removeAboutItem('skills', index)" title="删除" aria-label="删除">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
            <button class="btn btn-ghost" @click="addAboutItem('skills')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              添加技能
            </button>
          </div>

          <!-- 联系方式 -->
          <div class="about-section">
            <h5 class="about-section-title">联系方式</h5>
            <div class="form-group">
              <label for="about-email">邮箱</label>
              <input id="about-email" v-model="aboutForm.contact.email" type="email" class="form-input" placeholder="邮箱地址" />
            </div>
            <div class="form-group">
              <label for="about-github">GitHub 链接</label>
              <input id="about-github" v-model="aboutForm.contact.github" type="url" class="form-input" placeholder="https://github.com/..." />
            </div>
          </div>

          <button class="btn btn-primary" @click="saveAboutContent" :disabled="savingAbout">
            {{ savingAbout ? '保存中...' : '保存更改' }}
          </button>
        </div>
      </div>
      </section>
      </div>
    </div>

    <!-- 上传进度提示 -->
    <transition name="toast-fade">
      <div v-if="uploadToast.show" class="upload-toast" :class="uploadToast.type">
        {{ uploadToast.message }}
      </div>
    </transition>

    <!-- 编辑卡片弹窗 -->
    <transition name="modal-fade">
      <div v-if="showEditDialog" class="modal-overlay" @click.self="closeEditDialog">
        <div class="modal-dialog glass-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <h3>编辑卡片</h3>
            <button class="modal-close" aria-label="关闭弹窗" @click="closeEditDialog">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>标题</label>
              <input v-model="editForm.title" type="text" class="form-input" placeholder="卡片标题" />
            </div>
            <div class="form-group">
              <label>描述（可选）</label>
              <input v-model="editForm.description" type="text" class="form-input" placeholder="卡片描述" />
            </div>
            <div class="form-group">
              <label>链接（可选）</label>
              <input v-model="editForm.link" type="text" class="form-input" placeholder="https://..." />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="closeEditDialog">取消</button>
            <button class="btn btn-primary" @click="saveEdit" :disabled="!editForm.title">保存</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 删除确认弹窗 -->
    <transition name="modal-fade">
      <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal-dialog glass-card" role="dialog" aria-modal="true">
          <div class="modal-header">
            <h3>确认删除</h3>
            <button class="modal-close" aria-label="关闭弹窗" @click="cancelDelete">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <p class="confirm-text" v-if="deleteTarget?.type === 'file'">
              确定要删除文件 "<strong>{{ deleteTarget?.item?.filename }}</strong>" 吗？此操作无法撤销。
            </p>
            <p class="confirm-text" v-else-if="deleteTarget?.type === 'card'">
              确定要删除卡片 "<strong>{{ deleteTarget?.title }}</strong>" 吗？此操作无法撤销。
            </p>
            <p class="confirm-text" v-else-if="deleteTarget?.type === 'about'">
              确定要删除 "<strong>{{ deleteTarget?.value }}</strong>" 吗？此操作无法撤销。
            </p>
            <p class="confirm-text" v-else>
              确定要删除吗？此操作无法撤销。
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="cancelDelete">取消</button>
            <button class="btn btn-danger" @click="confirmDelete">确认删除</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { onBeforeRouteLeave } from 'vue-router';
import request from '@/utils/request';
import { adminSession, updateSession } from '@/utils/adminSession';
import { useAboutStore } from '@/stores/about';
import AdminArticles from '@/components/admin/AdminArticles.vue';
import AdminPages from '@/components/admin/AdminPages.vue';

const router = useRouter();

const tabs = [
  { key: 'articles', label: '文章与文档' },
  { key: 'pages', label: '页面文案' },
  { key: 'background', label: '背景文件' },
  { key: 'audio', label: '音频文件' },
  { key: 'cards', label: '网站卡片' },
  { key: 'about', label: '关于页面' }
];

const navigationGroups = [
  { label: '内容管理', keys: ['articles', 'pages', 'cards', 'about'] },
  { label: '媒体资源', keys: ['background', 'audio'] }
];
const sectionDescriptions = {
  background: '上传图片或视频，作为博客的背景素材。',
  audio: '整理网站音乐列表，上传或删除音频文件。',
  cards: '整理网站展示的项目介绍、技能和标签卡片。',
  about: '更新个人简介、技能标签和联系方式。'
};

const activeTab = ref('articles');
const articleEditor = ref(null);
const pageEditor = ref(null);
function selectTab(tab) {
  if (tab === activeTab.value) return;
  if (!canLeaveEditor()) return;
  activeTab.value = tab;
}

function canLeaveEditor() {
  const editor = activeTab.value === 'articles' ? articleEditor.value : activeTab.value === 'pages' ? pageEditor.value : null;
  return !editor?.discardChanges || editor.discardChanges();
}
onBeforeRouteLeave(() => canLeaveEditor());

const fileList = ref([]);
const loading = ref(false);
const fileInput = ref(null);

// 卡片相关状态
const introCards = ref([]);
const skillCards = ref([]);
const tagCards = ref([]);
const cardForm = ref({
  card_type: 'intro',
  title: '',
  description: '',
  link: ''
});

// 编辑弹窗状态
const showEditDialog = ref(false);
const editForm = ref({
  id: null,
  card_type: 'intro',
  title: '',
  description: '',
  link: ''
});

// 删除确认弹窗状态
const showDeleteConfirm = ref(false);
const deleteTarget = ref(null);

// 关于页面状态
const aboutForm = ref({
  intro: { name: '', subtitle: '', bio: '' },
  tags: [],
  skills: [],
  contact: { email: '', github: '' }
});
const savingAbout = ref(false);

const acceptTypes = reactive({
  background: 'image/*,video/*',
  audio: 'audio/*'
});

const acceptExtensions = reactive({
  background: 'PNG, JPG, WEBP, GIF, MP4, WEBM, MOV',
  audio: 'MP3, WAV, OGG, M4A'
});

const uploadToast = ref({ show: false, message: '', type: 'info' });

function showToast(message, type = 'info') {
  uploadToast.value = { show: true, message, type };
  setTimeout(() => {
    uploadToast.value.show = false;
  }, 3000);
}

function goBack() {
  router.push('/');
}

function triggerFileInput() {
  fileInput.value?.click();
}

async function handleFileSelect(event) {
  const files = event.target.files;
  if (files.length > 0) {
    await uploadFiles(Array.from(files));
  }
  event.target.value = '';
}

async function handleDrop(event) {
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    await uploadFiles(Array.from(files));
  }
}

async function uploadFiles(files) {
  if (files.length === 0) return;

  const subdirMap = { background: 'tupian', audio: 'assets' };
  const subdir = subdirMap[activeTab.value];
  const formData = new FormData();

  files.forEach(file => {
    formData.append('files', file);
  });
  formData.append('subdir', subdir);

  try {
    loading.value = true;

    const result = await request.post('/api/admin/upload', formData, { timeout: 120000 });
    const rejected = (result.rejected || []).map(item => `${item.filename}: ${item.reason}`).join('；');
    showToast(`成功上传 ${result.count} 个文件${rejected ? '；未上传：' + rejected : ''}`, rejected ? 'error' : 'success');
    await loadFiles();
  } catch (err) {
    console.error('上传失败:', err);
    showToast('上传失败: ' + (err.message || '未知错误'), 'error');
  } finally {
    loading.value = false;
  }
}

async function deleteFile(item, type) {
  deleteTarget.value = { type: 'file', item, fileType: type };
  showDeleteConfirm.value = true;
}

function handleImageError(e) {
  const PLACEHOLDER_SVG = `data:image/svg+xml;base64,${btoa('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"><rect fill="%23f0f0f0" width="200" height="150"/><text x="100" y="75" text-anchor="middle" fill="%23999" font-size="14">图片加载失败</text></svg>')}`;
  e.target.src = PLACEHOLDER_SVG;
  e.target.onerror = null;
}

// 加载卡片数据
async function loadCards() {
  try {
    const data = await request.get('/api/cards');
    introCards.value = data?.intro_cards || [];
    skillCards.value = data?.skill_cards || [];
    tagCards.value = data?.tag_cards || [];
  } catch (err) {
    console.error('加载卡片失败:', err);
  }
}

// 添加卡片
async function addCard() {
  if (!cardForm.value.title) {
    showToast('请输入标题', 'error');
    return;
  }
  try {

    await request.post('/api/cards', { ...cardForm.value });
    showToast('添加成功', 'success');
    // 重置表单
    cardForm.value = {
      card_type: cardForm.value.card_type,
      title: '',
      description: '',
      link: ''
    };
    await loadCards();
  } catch (err) {
    console.error('添加卡片失败:', err);
    showToast('添加失败: ' + (err.message || '未知错误'), 'error');
  }
}

// 删除卡片
async function deleteCard(card) {
  deleteTarget.value = { type: 'card', ...card };
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  if (!deleteTarget.value) return;

  try {
    loading.value = true;

    if (deleteTarget.value.type === 'file') {
      // 删除文件
      const { item, fileType } = deleteTarget.value;
      const subdirMap = { background: 'tupian', audio: 'assets' };

      const encodedFilename = encodeURIComponent(item.filename);
      await request.delete(`/api/admin/file/${subdirMap[fileType]}/${encodedFilename}`);
      showToast('删除成功', 'success');
      await loadFiles();
    } else if (deleteTarget.value.type === 'card') {
      // 删除卡片
      await request.delete(`/api/cards/${deleteTarget.value.id}`);
      showToast('删除成功', 'success');
      await loadCards();
    } else if (deleteTarget.value.type === 'about') {
      const { aboutType, index } = deleteTarget.value;
      aboutForm.value[aboutType].splice(index, 1);
      showToast('已移除，保存更改后生效', 'success');
    }

    showDeleteConfirm.value = false;
    deleteTarget.value = null;
  } catch (err) {
    console.error('删除失败:', err);
    showToast('删除失败: ' + (err.message || '未知错误'), 'error');
  } finally {
    loading.value = false;
  }
}

function cancelDelete() {
  showDeleteConfirm.value = false;
  deleteTarget.value = null;
}

// 加载关于页面内容
async function loadAboutContent() {
  try {
    const data = await request.get('/api/about');


    // 处理个人简介
    if (data.intro && data.intro.length > 0) {
      const intro = {};
      for (const item of data.intro) {
        intro[item.key] = item.value;
      }
      aboutForm.value.intro = {
        name: intro.name || '',
        subtitle: intro.subtitle || '',
        bio: intro.bio || ''
      };
    }

    // 处理技能标签
    if (data.tags && data.tags.length > 0) {
      aboutForm.value.tags = data.tags.map(item => item.value);
    } else {
      aboutForm.value.tags = [];
    }

    // 处理技能树
    if (data.skills && data.skills.length > 0) {
      aboutForm.value.skills = data.skills.map(item => item.value);
    } else {
      aboutForm.value.skills = [];
    }

    // 处理联系方式
    if (data.contact && data.contact.length > 0) {
      const contact = {};
      for (const item of data.contact) {
        contact[item.key] = item.value;
      }
      aboutForm.value.contact = {
        email: contact.email || '',
        github: contact.github || ''
      };
    }
  } catch (err) {
    console.error('加载关于页面内容失败:', err);
  }
}

// 保存关于页面内容
async function saveAboutContent() {
  savingAbout.value = true;
  try {
    await request.put('/api/admin/about', aboutForm.value);
    await useAboutStore().loadAboutData(true);
    showToast('保存成功', 'success');
  } catch (err) { showToast('保存失败：' + err.message, 'error'); }
  finally { savingAbout.value = false; }
}

// 添加关于页面项目
function addAboutItem(type) {
  if (type === 'tags') {
    aboutForm.value.tags.push('');
  } else if (type === 'skills') {
    aboutForm.value.skills.push('');
  }
}

// 移除列表项仅修改表单，统一保存后生效。
function removeAboutItem(type, index) {
  deleteTarget.value = { type: 'about', aboutType: type, index, value: aboutForm.value[type][index] };
  showDeleteConfirm.value = true;
}

// 打开编辑弹窗
function openEditDialog(card) {
  editForm.value = {
    id: card.id,
    card_type: card.card_type,
    title: card.title,
    description: card.description || '',
    link: card.link || ''
  };
  showEditDialog.value = true;
}

// 关闭编辑弹窗
function closeEditDialog() {
  showEditDialog.value = false;
}

// 保存编辑
async function saveEdit() {
  if (!editForm.value.title) {
    showToast('请输入标题', 'error');
    return;
  }
  try {

    await request.put(`/api/cards/${editForm.value.id}`, {
      card_type: editForm.value.card_type,
      title: editForm.value.title,
      description: editForm.value.description,
      link: editForm.value.link
    });
    showToast('保存成功', 'success');
    closeEditDialog();
    await loadCards();
  } catch (err) {
    console.error('保存失败:', err);
    showToast('保存失败: ' + (err.message || '未知错误'), 'error');
  }
}

async function loadFiles() {
  loading.value = true;
  try {
    if (activeTab.value === 'background') {
      const data = await request.get('/api/background-media');
      const images = (data?.images || []).map(item => ({ ...item, isVideo: false }));
      const videos = (data?.videos || []).map(item => ({ ...item, isVideo: true }));
      fileList.value = [...images, ...videos];
    } else if (activeTab.value === 'audio') {
      const data = await request.get('/api/audio-files');
      fileList.value = data?.audios || [];
    } else if (activeTab.value === 'cards') {
      await loadCards();
    } else if (activeTab.value === 'about') {
      await loadAboutContent();
    }
  } catch (err) {
    console.error('加载文件列表失败:', err);
    fileList.value = [];
  } finally {
    loading.value = false;
  }
}

watch(activeTab, () => {
  if (adminSession.authenticated) loadFiles();
});

const checking = ref(true), loginPassword = ref(''), loginError = ref(''), loggingIn = ref(false);
const passwordVisible = ref(false);
async function loadRules() {
  const rules = await request.get('/api/admin/upload-rules');
  const mapping = { background: 'tupian', audio: 'assets' };
  for (const [tab, dir] of Object.entries(mapping)) {
    acceptTypes[tab] = rules.extensions[dir].join(',');
    acceptExtensions[tab] = rules.extensions[dir].join(', ').toUpperCase();
  }
}
async function login() {
  loggingIn.value = true; loginError.value = '';
  try {
    const data = await request.post('/api/admin/login', { password: loginPassword.value });
    loginPassword.value = ''; passwordVisible.value = false; updateSession(data); await loadRules(); await loadFiles();
  } catch (err) { loginError.value = err.message; }
  finally { loggingIn.value = false; }
}
async function logout() {
  if (!canLeaveEditor()) return;
  try { await request.post('/api/admin/logout'); passwordVisible.value = false; updateSession(null); }
  catch (err) { showToast(err.message, 'error'); }
}
onMounted(async () => {
  try { updateSession(await request.get('/api/admin/session')); await loadRules(); await loadFiles(); }
  catch (err) { if (err.status !== 401) loginError.value = err.message; }
  finally { checking.value = false; }
});
</script>

<style scoped lang="scss">
@use '../styles/admin';
</style>
