<template>
  <div class="navbar-root">
    <nav class="navbar">
    <div class="navbar-container">
      <!-- 左侧：博客名称 -->
      <div class="brand-area">
        <span class="brand-name" @click="goHome">沛心的博客</span>
      </div>

      <!-- 桌面端菜单 -->
      <div class="navbar-menu">
        <router-link to="/" class="nav-link" active-class="active">首页</router-link>
        <router-link to="/articles" class="nav-link" active-class="active">文章</router-link>
        <router-link to="/about" class="nav-link" active-class="active">关于</router-link>
        <router-link to="/more" class="nav-link" active-class="active">了解更多</router-link>

        <!-- 音乐按钮 -->
        <button class="music-btn" @click="togglePlayer" :aria-label="playerOpen ? '关闭播放' : '听音乐'">
          <svg class="music-icon" :class="{ spinning: isPlaying }" viewBox="0 0 24 24" width="20" height="20" fill="none">
            <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="6" cy="18" r="3" fill="currentColor" opacity="0.85"/>
            <circle cx="18" cy="16" r="3" fill="currentColor" opacity="0.85"/>
          </svg>
          <span class="music-label">{{ playerOpen ? '关闭播放' : '听音乐' }}</span>
        </button>
      </div>

      <!-- 移动端汉堡菜单 -->
      <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen" :class="{ active: mobileMenuOpen }">
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
      </button>
    </div>

    <!-- 移动端菜单面板 -->
    <transition name="mobile-menu-fade">
      <div v-if="mobileMenuOpen" class="mobile-menu">
        <router-link to="/" class="mobile-link" active-class="active" @click="mobileMenuOpen = false">首页</router-link>
        <router-link to="/articles" class="mobile-link" active-class="active" @click="mobileMenuOpen = false">文章</router-link>
        <router-link to="/about" class="mobile-link" active-class="active" @click="mobileMenuOpen = false">关于</router-link>
        <router-link to="/more" class="mobile-link" active-class="active" @click="mobileMenuOpen = false">了解更多</router-link>
        <button class="mobile-music-btn" @click="togglePlayer">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none">
            <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="6" cy="18" r="3" fill="currentColor" opacity="0.85"/>
            <circle cx="18" cy="16" r="3" fill="currentColor" opacity="0.85"/>
          </svg>
          {{ playerOpen ? '关闭播放' : '听音乐' }}
        </button>
      </div>
    </transition>
  </nav>

  <!-- 音乐播放器弹窗 -->
  <Teleport to="body">
    <transition name="player-fade">
      <div v-if="playerOpen" class="music-player-popup">
      <div class="player-card glass-card">
        <button class="player-close-btn" @click="closePlayer" aria-label="关闭播放" title="关闭播放">×</button>
        <!-- 歌曲信息 -->
        <div class="player-song-info">
          <div class="song-cover">
            <img v-if="currentSong.cover" :src="currentSong.cover" :alt="currentSong.name" />
            <div v-else class="song-cover-placeholder">
              <svg viewBox="0 0 24 24" width="32" height="32" fill="none">
                <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="6" cy="18" r="3" fill="currentColor" opacity="0.85"/>
                <circle cx="18" cy="16" r="3" fill="currentColor" opacity="0.85"/>
              </svg>
            </div>
          </div>
          <div class="song-details">
            <h4 class="song-name">{{ currentSong.name }}</h4>
            <p class="song-artist">{{ currentSong.artist }}</p>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="player-progress">
          <div class="progress-bar" @click="seekTo">
            <div class="progress-track" :style="{ width: progressPercent + '%' }"></div>
            <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
          </div>
          <div class="progress-time">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="player-controls">
          <button class="control-btn" @click="prevSong" title="上一首">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
              <path d="M19 20L9 12l10-8v16z" fill="currentColor"/>
              <rect x="5" y="4" width="3" height="16" rx="1" fill="currentColor"/>
            </svg>
          </button>
          <button class="control-btn play-btn" @click="togglePlay" :title="isPlaying ? '暂停' : '播放'">
            <svg v-if="isPlaying" viewBox="0 0 24 24" width="28" height="28" fill="none">
              <rect x="6" y="4" width="4" height="16" rx="1" fill="currentColor"/>
              <rect x="14" y="4" width="4" height="16" rx="1" fill="currentColor"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" width="28" height="28" fill="none">
              <path d="M8 5v14l11-7L8 5z" fill="currentColor"/>
            </svg>
          </button>
          <button class="control-btn" @click="nextSong" title="下一首">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
              <path d="M5 4l10 8-10 8V4z" fill="currentColor"/>
              <rect x="16" y="4" width="3" height="16" rx="1" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    </transition>
  </Teleport>

  <!-- 音频元素 -->
  <audio ref="audioEl" preload="metadata"></audio>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request';

const router = useRouter();
const mobileMenuOpen = ref(false);
const isPlaying = ref(false);
const playerOpen = ref(false);

// 播放状态
const currentTime = ref(0);
const duration = ref(0);
const progressPercent = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

// 播放列表 - 从后端动态获取
const playlist = ref([]);

async function fetchAudioPlaylist() {
  try {
    const data = await request.get('/api/audio-files');
    const list = Array.isArray(data?.audios) ? data.audios : [];
    if (!list.length) return;

    const normalized = list
      .map(item => ({
        name: String(item?.name || '').trim(),
        artist: String(item?.artist || '未知艺术家').trim(),
        src: String(item?.src || '').trim(),
        cover: ''
      }))
      .filter(item => item.name && item.src);

    if (normalized.length) {
      playlist.value = normalized;
    }
  } catch (err) {
    console.error('加载音频列表失败，使用内置播放列表:', err);
  }
}

const currentSongIndex = ref(-1); // -1 表示还未播放过
const currentSong = computed(() => {
  if (currentSongIndex.value === -1) {
    return { name: '暂无播放', artist: '点击播放开始', cover: '' };
  }
  return playlist.value[currentSongIndex.value] || { name: '暂无播放', artist: '点击播放开始', cover: '' };
});

const audioEl = ref(null);
const handleTimeUpdate = () => {
  if (!audioEl.value) return;
  currentTime.value = audioEl.value.currentTime;
  duration.value = audioEl.value.duration || 0;
};
const handleEnded = () => {
  nextSong();
};
const handleAudioError = (e) => {
  console.error('音频加载失败:', e);
  if (playlist.value.length > 1) {
    nextSong();
  } else {
    isPlaying.value = false;
  }
};

function buildPublicAssetPath(relativePath) {
  const normalized = String(relativePath || '').replace(/^\/+/, '')
  const base = import.meta.env.BASE_URL || '/'
  return new URL(normalized, window.location.origin + base).toString()
}

function goHome() {
  router.push('/');
}



function normalizeIndex(index) {
  const len = playlist.value.length;
  if (!len) return -1;
  return ((index % len) + len) % len;
}

function goToSong(index) {
  const normalized = normalizeIndex(index);
  if (normalized === -1) return;
  currentSongIndex.value = normalized;
  playSong(normalized);
}

// 随机播放歌曲
function playRandomSong(excludeIndex = -1) {
  if (playlist.value.length === 0) return;
  let newIndex;
  if (playlist.value.length === 1) {
    newIndex = 0;
  } else {
    do {
      newIndex = Math.floor(Math.random() * playlist.value.length);
    } while (newIndex === excludeIndex && playlist.value.length > 1);
  }
  goToSong(newIndex);
}

// 播放指定歌曲
function playSong(index) {
  if (!audioEl.value || index < 0 || index >= playlist.value.length) return;
  const song = playlist.value[index];
  audioEl.value.src = song.src;
  
  audioEl.value.play().then(() => {
    isPlaying.value = true;
  }).catch(err => {
    console.error('播放失败:', err);
  });
}

// 切换播放器显示
function togglePlayer() {
  playerOpen.value = !playerOpen.value;
  
  // 打开播放器且还没播放过，随机播放
  if (playerOpen.value && currentSongIndex.value === -1) {
    playRandomSong();
  }
}

function closePlayer() {
  playerOpen.value = false;
}

// 播放/暂停
function togglePlay() {
  if (!audioEl.value) return;
  
  // 如果还没播放过，先随机播放
  if (currentSongIndex.value === -1) {
    playRandomSong();
    return;
  }
  
  if (isPlaying.value) {
    audioEl.value.pause();
    isPlaying.value = false;
  } else {
    audioEl.value.play().then(() => {
      isPlaying.value = true;
    }).catch(() => {});
  }
}

// 上一首（如果刚进网站没有上一首，就随机播放）
function prevSong() {
  if (!audioEl.value) return;
  
  if (currentSongIndex.value === -1) {
    // 还没有播放过，先到第一首
    goToSong(0);
    return;
  }

  goToSong(currentSongIndex.value - 1);
}

// 下一首（顺序循环）
function nextSong() {
  if (!audioEl.value) return;
  if (currentSongIndex.value === -1) {
    goToSong(0);
    return;
  }
  goToSong(currentSongIndex.value + 1);
}

// 跳转到指定进度
function seekTo(event) {
  if (!audioEl.value || duration.value === 0) return;
  const rect = event.currentTarget.getBoundingClientRect();
  const percent = (event.clientX - rect.left) / rect.width;
  audioEl.value.currentTime = percent * duration.value;
}

// 格式化时间
function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

onMounted(() => {
  fetchAudioPlaylist();
  if (audioEl.value) {
    audioEl.value.addEventListener('timeupdate', handleTimeUpdate);
    audioEl.value.addEventListener('ended', handleEnded);
    audioEl.value.addEventListener('error', handleAudioError);
  }
});

onUnmounted(() => {
  if (audioEl.value) {
    audioEl.value.removeEventListener('timeupdate', handleTimeUpdate);
    audioEl.value.removeEventListener('ended', handleEnded);
    audioEl.value.removeEventListener('error', handleAudioError);
    audioEl.value.pause();
    isPlaying.value = false;
  }
});
</script>

<style scoped lang="scss">
$ease-damped: cubic-bezier(0.25, 0.8, 0.25, 1);

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.25);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.4s $ease-damped;
  will-change: transform, opacity;
}

.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 2rem;
  max-width: 1280px;
  margin: 0 auto;
}

// ===== 品牌名称 =====
.brand-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-name {
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: 0.6px;
  color: #1a1a1a;
  user-select: none;
  cursor: pointer;
  transition: all 0.4s $ease-damped;

  &:hover {
    text-shadow: 0 0 12px rgba(168, 85, 247, 0.3);
  }
}

// ===== 桌面端菜单 =====
.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  position: relative;
  color: #1a1a1a;
  font-weight: 500;
  text-decoration: none;
  padding: 6px 8px;
  border-radius: 6px;
  transition: all 0.4s $ease-damped;
  will-change: transform, opacity;

  &:hover,
  &.active {
    color: #a855f7;
    transform: translateY(-1px);
  }

  &::after {
    content: "";
    position: absolute;
    left: 6px;
    right: 6px;
    bottom: -4px;
    height: 2px;
    background: linear-gradient(90deg, #a855f7, #ec4899);
    transform-origin: left center;
    transform: scaleX(0);
    border-radius: 2px;
    transition: transform 0.36s $ease-damped;
    will-change: transform;
  }

  &:hover::after,
  &.active::after {
    transform: scaleX(1);
  }
}

// ===== 音乐按钮 =====
.music-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 9999px;
  padding: 8px 16px;
  color: #1a1a1a;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.4s $ease-damped;
  will-change: transform, opacity;
  transform: translateZ(0);

  .music-icon {
    color: #a855f7;
    transition: transform 0.6s $ease-damped;

    &.spinning {
      animation: spin-note 2s linear infinite;
    }
  }

  &:hover {
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.25);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 4px 16px rgba(168, 85, 247, 0.15);
  }

  &:active {
    transform: scale(0.96);
  }
}

// ===== 音乐播放器弹窗 =====
.music-player-popup {
  position: fixed;
  top: 78px;
  right: 2rem;
  z-index: 2001;
  width: 360px;
}

.player-card {
  position: relative;
  padding: 24px;
  background: rgba(255, 255, 255, 0.65) !important;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.player-close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  color: rgba(0, 0, 0, 0.55);
  font-size: 18px;
  line-height: 28px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: #a855f7;
    background: rgba(168, 85, 247, 0.14);
  }
}

.player-song-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.song-cover {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

.song-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a855f7;
}

.song-details {
  flex: 1;
  min-width: 0;
}

.song-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-artist {
  font-size: 0.85rem;
  color: rgba(0, 0, 0, 0.5);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// 进度条
.player-progress {
  margin-bottom: 20px;
}

.progress-bar {
  position: relative;
  height: 6px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 3px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: height 0.2s ease;

  &:hover {
    height: 8px;

    .progress-thumb {
      opacity: 1;
      transform: translateX(-50%) scale(1.2);
    }
  }
}

.progress-track {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #a855f7, #ec4899);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #fff;
  border: 2px solid #a855f7;
  border-radius: 50%;
  transform: translateX(-50%) translateY(-50%) scale(1);
  opacity: 0;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(168, 85, 247, 0.3);
}

.progress-time {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.45);
}

// 控制按钮
.player-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 50%;
  color: #1a1a1a;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.25);
    color: #a855f7;
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }
}

.play-btn {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  border: none;
  color: #fff;

  &:hover {
    background: linear-gradient(135deg, #9333ea, #db2777);
    color: #fff;
    box-shadow: 0 4px 16px rgba(168, 85, 247, 0.4);
  }
}

// ===== 弹窗动画 =====
.player-fade-enter-active,
.player-fade-leave-active {
  transition: all 0.3s $ease-damped;
}

.player-fade-enter-from,
.player-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

// ===== 汉堡菜单 =====
.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;

  .hamburger-line {
    width: 24px;
    height: 2px;
    background: #1a1a1a;
    transition: all 0.4s $ease-damped;
    border-radius: 2px;
  }

  &.active {
    .hamburger-line:nth-child(1) { transform: rotate(45deg) translate(5px, 5px); }
    .hamburger-line:nth-child(2) { opacity: 0; }
    .hamburger-line:nth-child(3) { transform: rotate(-45deg) translate(5px, -5px); }
  }
}

// ===== 移动端菜单 =====
.mobile-menu {
  position: fixed;
  top: 68px;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 2rem;
  gap: 0.5rem;
  z-index: 999;
}

.mobile-link {
  color: #1a1a1a;
  font-weight: 500;
  text-decoration: none;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.4s $ease-damped;

  &:hover,
  &.active {
    color: #a855f7;
  }
}

.mobile-music-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 9999px;
  padding: 10px 20px;
  color: #e879f9;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s $ease-damped;
  margin-top: 0.5rem;

  &:hover {
    background: rgba(168, 85, 247, 0.3);
  }
}

.mobile-menu-fade-enter-active,
.mobile-menu-fade-leave-active {
  transition: all 0.3s $ease-damped;
}
.mobile-menu-fade-enter-from,
.mobile-menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes spin-note {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .navbar-menu { display: none; }
  .hamburger { display: flex; }
  .navbar-container { padding: 14px 1rem; }
  
  .music-player-popup {
    right: 1rem;
    left: 1rem;
    width: auto;
  }
}
</style>

