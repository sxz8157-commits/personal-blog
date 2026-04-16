<template>
  <div class="admin-page">
    <div class="hollow-window">
      <div class="admin-header">
        <div class="admin-title-area">
          <h1 class="admin-title gradient-text">后台管理</h1>
          <p class="admin-subtitle">管理 public 文件夹中的图片、音频和文档</p>
        </div>
        <button class="btn btn-ghost" @click="goBack">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回首页
        </button>
      </div>

      <!-- Tab 切换 -->
      <div class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 上传区域（非卡片和关于页面时显示） -->
      <div v-if="activeTab !== 'cards' && activeTab !== 'about'" class="upload-zone" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
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
      <div class="file-list" v-loading="loading">
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
              <button class="action-btn danger" @click="deleteFile(item, 'background')" title="删除">
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
              <button class="action-btn danger" @click="deleteFile(item, 'audio')" title="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 文档列表 -->
        <div v-if="activeTab === 'docs'" class="file-list-view">
          <div v-for="item in fileList" :key="item.filename" class="file-list-item glass-card">
            <div class="file-icon doc-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="file-info">
              <p class="file-name">{{ item.title || item.filename }}</p>
              <p class="file-meta">{{ item.file_type?.toUpperCase() }} · {{ formatDate(item.created_at) }}</p>
            </div>
            <div class="file-actions">
              <button class="action-btn danger" @click="deleteFile(item, 'docs')" title="删除">
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
                <label>标题</label>
                <input v-model="cardForm.title" type="text" class="form-input" placeholder="卡片标题" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>描述（可选）</label>
                <input v-model="cardForm.description" type="text" class="form-input" placeholder="卡片描述" />
              </div>
              <div class="form-group">
                <label>链接（可选）</label>
                <input v-model="cardForm.link" type="text" class="form-input" placeholder="https://..." />
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
              <span class="cards-count">共 {{ introCards.length + skillCards.length }} 个</span>
            </div>
            <div class="cards-list" v-if="introCards.length > 0 || skillCards.length > 0">
              <div v-for="card in [...introCards, ...skillCards]" :key="card.id" class="card-item glass-card">
                <div class="card-info">
                  <p class="card-title">{{ card.title }}</p>
                  <p class="card-desc">{{ card.description || '暂无描述' }}</p>
                </div>
                <div class="card-actions">
                  <span v-if="card.link" class="card-link-badge">有链接</span>
                  <button class="action-btn" @click="openEditDialog(card)" title="编辑">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  <button class="action-btn danger" @click="deleteCard(card)" title="删除">
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
        <div v-if="!loading && fileList.length === 0 && activeTab !== 'background' && activeTab !== 'cards' && activeTab !== 'about'" class="empty-state">
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
              <label>姓名</label>
              <input v-model="aboutForm.intro.name" type="text" class="form-input" placeholder="姓名" />
            </div>
            <div class="form-group">
              <label>副标题</label>
              <input v-model="aboutForm.intro.subtitle" type="text" class="form-input" placeholder="例如：全栈开发者 / 赛博美学探索者" />
            </div>
            <div class="form-group">
              <label>个人简介</label>
              <textarea v-model="aboutForm.intro.bio" class="form-input" rows="4" placeholder="个人简介内容"></textarea>
            </div>
          </div>

          <!-- 技能标签 -->
          <div class="about-section">
            <h5 class="about-section-title">技能标签 <span class="section-hint">（显示在个人简介卡片上）</span></h5>
            <div class="tag-list" v-if="aboutForm.tags.length > 0">
              <div v-for="(tag, index) in aboutForm.tags" :key="index" class="tag-item glass-card">
                <input v-model="aboutForm.tags[index]" type="text" class="tag-input" placeholder="标签名" />
                <button class="action-btn danger" @click="removeAboutItem('tags', index)" title="删除">
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
                <input v-model="aboutForm.skills[index]" type="text" class="tag-input" placeholder="技能名称" />
                <button class="action-btn danger" @click="removeAboutItem('skills', index)" title="删除">
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
              <label>邮箱</label>
              <input v-model="aboutForm.contact.email" type="email" class="form-input" placeholder="邮箱地址" />
            </div>
            <div class="form-group">
              <label>GitHub 链接</label>
              <input v-model="aboutForm.contact.github" type="url" class="form-input" placeholder="https://github.com/..." />
            </div>
          </div>

          <button class="btn btn-primary" @click="saveAboutContent" :disabled="savingAbout">
            {{ savingAbout ? '保存中...' : '保存更改' }}
          </button>
        </div>
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
        <div class="modal-dialog glass-card">
          <div class="modal-header">
            <h3>编辑卡片</h3>
            <button class="modal-close" @click="closeEditDialog">
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
        <div class="modal-dialog glass-card">
          <div class="modal-header">
            <h3>确认删除</h3>
            <button class="modal-close" @click="cancelDelete">
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
import { ref, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';

const router = useRouter();

const tabs = [
  { key: 'background', label: '背景文件' },
  { key: 'audio', label: '音频文件' },
  { key: 'docs', label: '文档文件' },
  { key: 'cards', label: '网站卡片' },
  { key: 'about', label: '关于页面' }
];

const activeTab = ref('background');
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

const acceptTypes = {
  background: 'image/*,video/*',
  audio: 'audio/*',
  docs: '.md,.pdf,.txt,.docx,.pptx,.xlsx,.xmind'
};

const acceptExtensions = {
  background: 'PNG, JPG, WEBP, GIF, MP4, WEBM, MOV',
  audio: 'MP3, WAV, OGG, M4A',
  docs: 'MD, PDF, TXT, DOCX, PPTX, XLSX, XMIND'
};

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

  const subdirMap = { background: 'tupian', audio: 'assets', docs: 'wenz' };
  const subdir = subdirMap[activeTab.value];
  const formData = new FormData();

  files.forEach(file => {
    formData.append('files', file);
  });
  formData.append('subdir', subdir);

  try {
    loading.value = true;
    await request.post('/api/admin/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    showToast(`成功上传 ${files.length} 个文件`, 'success');
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
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" fill="%23ddd"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999">图片加载失败</text></svg>';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return dateStr.split(' ')[0] || dateStr;
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
      const subdirMap = { background: 'tupian', audio: 'assets', docs: 'wenz' };
      await request.delete(`/api/admin/file/${subdirMap[fileType]}/${item.filename}`);
      showToast('删除成功', 'success');
      await loadFiles();
    } else if (deleteTarget.value.type === 'card') {
      // 删除卡片
      await request.delete(`/api/cards/${deleteTarget.value.id}`);
      showToast('删除成功', 'success');
      await loadCards();
    } else if (deleteTarget.value.type === 'about') {
      // 删除关于页面项目
      const { aboutType, index } = deleteTarget.value;
      if (aboutType === 'tags') {
        aboutForm.value.tags.splice(index, 1);
      } else if (aboutType === 'skills') {
        aboutForm.value.skills.splice(index, 1);
      }
    }

    showDeleteConfirm.value = false;
    deleteTarget.value = null;
  } catch (err) {
    console.error('删除失败:', err);
    showToast('删除失���: ' + (err.message || '未知错误'), 'error');
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
    console.log('后台加载关于页面 API 返回数据:', data);

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
    // 先删除旧数据
    const sections = ['intro', 'tags', 'skills', 'contact'];
    for (const section of sections) {
      const existing = await request.get(`/api/about/${section}`);
      for (const item of existing) {
        await request.delete(`/api/about/${item.id}`);
      }
    }

    // 添加新数据
    // 个人简介
    await request.post('/api/about', { section: 'intro', key: 'name', value: aboutForm.value.intro.name, sort_order: 1 });
    await request.post('/api/about', { section: 'intro', key: 'subtitle', value: aboutForm.value.intro.subtitle, sort_order: 2 });
    await request.post('/api/about', { section: 'intro', key: 'bio', value: aboutForm.value.intro.bio, sort_order: 3 });

    // 技能标签
    for (let i = 0; i < aboutForm.value.tags.length; i++) {
      const tag = aboutForm.value.tags[i];
      if (tag.trim()) {
        await request.post('/api/about', { section: 'tags', key: 'tag', value: tag, sort_order: i + 1 });
      }
    }

    // 技能树
    for (let i = 0; i < aboutForm.value.skills.length; i++) {
      const skill = aboutForm.value.skills[i];
      if (skill.trim()) {
        await request.post('/api/about', { section: 'skills', key: 'skill', value: skill, sort_order: i + 1 });
      }
    }

    // 联系方式
    if (aboutForm.value.contact.email) {
      await request.post('/api/about', { section: 'contact', key: 'email', value: aboutForm.value.contact.email, sort_order: 1 });
    }
    if (aboutForm.value.contact.github) {
      await request.post('/api/about', { section: 'contact', key: 'github', value: aboutForm.value.contact.github, sort_order: 2 });
    }

    showToast('保存成功', 'success');
  } catch (err) {
    console.error('保存关于页面内容失败:', err);
    showToast('保存失败', 'error');
  } finally {
    savingAbout.value = false;
  }
}

// 添加关于页面项目
function addAboutItem(type) {
  if (type === 'tags') {
    aboutForm.value.tags.push('');
  } else if (type === 'skills') {
    aboutForm.value.skills.push('');
  }
}

// 删除关于页面项目
function removeAboutItem(type, index) {
  const value = type === 'tags' ? aboutForm.value.tags[index] : aboutForm.value.skills[index];
  deleteTarget.value = { type: 'about', aboutType: type, index, value };
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
    } else if (activeTab.value === 'docs') {
      const data = await request.get('/api/md-articles');
      fileList.value = data?.articles || [];
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
  loadFiles();
});

onMounted(() => {
  loadFiles();
});
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.admin-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.admin-title-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.admin-title {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
}

.admin-subtitle {
  margin: 0;
  color: rgba(0, 0, 0, 0.55);
  font-size: 0.9rem;
}

.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.tab-btn {
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.6);
  transition: all 0.3s $ease-damped;

  &:hover {
    background: rgba(168, 85, 247, 0.08);
    border-color: rgba(168, 85, 247, 0.2);
    color: #a855f7;
  }

  &.active {
    background: linear-gradient(135deg, #a855f7, #ec4899);
    border-color: transparent;
    color: #fff;
  }
}

.upload-zone {
  margin: 24px;
  padding: 32px;
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s $ease-damped;
  color: rgba(0, 0, 0, 0.45);

  &:hover {
    border-color: #a855f7;
    background: rgba(168, 85, 247, 0.04);
    color: #a855f7;
  }

  svg {
    margin-bottom: 12px;
    color: currentColor;
  }

  p {
    margin: 0;
    font-size: 0.95rem;
  }
}

.upload-hint {
  margin-top: 6px !important;
  font-size: 0.8rem !important;
  opacity: 0.7;
}

.file-list {
  padding: 24px;
  min-height: 200px;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.file-list-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-card {
  overflow: hidden;
  padding: 0;
}

.file-preview {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: 16px 16px 0 0;
  background: rgba(0, 0, 0, 0.04);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

.video-preview {
  position: relative;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.2);
    transition: opacity 0.3s;
  }

  &:hover::after {
    opacity: 0;
  }
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: opacity 0.3s;
  pointer-events: none;

  svg {
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  }
}

.video-preview:hover .play-overlay {
  opacity: 0.8;
}

.file-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.file-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.audio-icon {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
  color: #a855f7;
}

.doc-icon {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.15));
  color: #3b82f6;
}

.file-info {
  flex: 1;
  min-width: 0;

  .file-name {
    margin: 0 0 4px 0;
    font-weight: 600;
    font-size: 0.95rem;
    color: #1a1a1a;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-artist,
  .file-meta {
    margin: 0;
    font-size: 0.8rem;
    color: rgba(0, 0, 0, 0.45);
  }
}

.file-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  cursor: pointer;
  transition: all 0.3s ease;
  color: rgba(0, 0, 0, 0.45);

  &:hover {
    transform: scale(1.05);
  }

  &.danger:hover {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.25);
    color: #ef4444;
  }

  &:not(.danger):hover {
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.25);
    color: #a855f7;
  }
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: rgba(0, 0, 0, 0.35);

  svg {
    margin-bottom: 12px;
  }

  p {
    margin: 0;
    font-size: 0.95rem;
  }
}

// Toast
.cards-admin {
  padding: 24px 0;
}

// 关于页面管理
.about-admin {
  padding: 24px 0;

  .form-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(168, 85, 247, 0.2);
  }
}

.about-section {
  margin-bottom: 32px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.about-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-hint {
  font-size: 0.8rem;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.5);
}

.about-admin .form-group {
  margin-bottom: 16px;
}

.about-admin .form-input {
  width: 100%;
}

.about-admin textarea.form-input {
  resize: vertical;
  min-height: 100px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

.tag-input {
  border: none;
  background: transparent;
  font-size: 0.9rem;
  color: #7c3aed;
  font-weight: 500;
  outline: none;
  min-width: 100px;
}

.about-admin .btn {
  margin-top: 8px;
}

.card-form {
  padding: 24px;
  margin-bottom: 24px;
}

.form-title {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.65);
}

.form-input {
  padding: 10px 14px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;

  &:focus {
    border-color: #a855f7;
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.15);
  }
}

.cards-section {
  margin-bottom: 24px;
}

.cards-section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.cards-count {
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.45);
  background: rgba(0, 0, 0, 0.04);
  padding: 2px 8px;
  border-radius: 6px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
}

.tag-name {
  font-weight: 500;
  font-size: 0.9rem;
  color: #7c3aed;
  background: rgba(168, 85, 247, 0.1);
  padding: 4px 12px;
  border-radius: 9999px;
}

.tag-actions {
  display: flex;
  gap: 6px;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cards-section-title {
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 4px 0;
  font-weight: 600;
  font-size: 0.95rem;
  color: #1a1a1a;
}

.card-desc {
  margin: 0;
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.55);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-link-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: rgba(168, 85, 247, 0.1);
  color: #7c3aed;
  border-radius: 6px;
}

.confirm-text {
  text-align: center;
  font-size: 0.95rem;
  color: rgba(0, 0, 0, 0.75);
  line-height: 1.6;
  padding: 8px 0;

  strong {
    color: #ef4444;
  }
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
  }

  &:active {
    transform: scale(0.96);
  }
}

.upload-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  z-index: 10000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);

  &.success {
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff;
  }

  &.error {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: #fff;
  }

  &.info {
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
  }
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s $ease-damped;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  padding: 10px 20px;
  transition: all 0.4s $ease-damped;
  will-change: transform, opacity;
  transform: translateZ(0);
  font-family: inherit;
  text-decoration: none;
}

.btn-ghost {
  background: rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #1a1a1a;
  border-radius: 12px;

  &:hover {
    transform: translateY(-2px);
    background: rgba(168, 85, 247, 0.08);
    box-shadow: 0 4px 16px rgba(168, 85, 247, 0.15);
    border-color: rgba(168, 85, 247, 0.25);
  }

  &:active {
    transform: scale(0.96);
  }
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  border-radius: 12px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(168, 85, 247, 0.3);
  }

  &:active {
    transform: scale(0.96);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}

// 弹窗样式
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-dialog {
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);

  h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a1a;
  }
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  color: rgba(0, 0, 0, 0.45);
  transition: all 0.3s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.06);
    color: #1a1a1a;
  }
}

.modal-body {
  padding: 24px;

  .form-group {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: rgba(0, 0, 0, 0.65);
      margin-bottom: 6px;
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s $ease-damped;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;

  .modal-dialog {
    transform: scale(0.95);
  }
}

@media (max-width: 768px) {
  .admin-page {
    padding: 16px;
  }

  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;
  }

  .admin-tabs {
    padding: 12px 16px;
    overflow-x: auto;
    gap: 6px;
  }

  .upload-zone {
    margin: 16px;
    padding: 24px 16px;
  }

  .file-list {
    padding: 16px;
  }

  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .cards-list {
    grid-template-columns: 1fr;
  }
}
</style>