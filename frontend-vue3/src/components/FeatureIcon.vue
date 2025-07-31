<template>
  <div class="feature-icon-wrapper">
    <!-- 精准查询图标 - 搜索定位 -->
    <svg v-if="type === 'search'" viewBox="0 0 24 24" class="feature-svg-icon">
      <defs>
        <linearGradient id="searchGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
      </defs>
      <circle cx="11" cy="11" r="8" fill="none" stroke="url(#searchGradient)" stroke-width="2"/>
      <path d="m21 21-4.35-4.35" stroke="url(#searchGradient)" stroke-width="2" stroke-linecap="round"/>
      <circle cx="11" cy="11" r="3" fill="url(#searchGradient)" opacity="0.3"/>
      <circle cx="9" cy="9" r="1" fill="url(#searchGradient)"/>
    </svg>

    <!-- 批量处理图标 - 多层文档 -->
    <svg v-else-if="type === 'batch'" viewBox="0 0 24 24" class="feature-svg-icon">
      <defs>
        <linearGradient id="batchGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#f093fb;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#f5576c;stop-opacity:1" />
        </linearGradient>
      </defs>
      <!-- 后层文档 -->
      <rect x="6" y="4" width="12" height="14" rx="2" fill="url(#batchGradient)" opacity="0.4"/>
      <!-- 中层文档 -->
      <rect x="4" y="6" width="12" height="14" rx="2" fill="url(#batchGradient)" opacity="0.6"/>
      <!-- 前层文档 -->
      <rect x="2" y="8" width="12" height="14" rx="2" fill="none" stroke="url(#batchGradient)" stroke-width="2"/>
      <!-- 文档内容线条 -->
      <line x1="5" y1="12" x2="11" y2="12" stroke="url(#batchGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="5" y1="15" x2="9" y2="15" stroke="url(#batchGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="5" y1="18" x2="10" y2="18" stroke="url(#batchGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <!-- 处理指示器 -->
      <circle cx="18" cy="10" r="3" fill="url(#batchGradient)"/>
      <path d="M16.5 10l1 1 2-2" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>

    <!-- 数据导出图标 - 下载箭头 -->
    <svg v-else-if="type === 'export'" viewBox="0 0 24 24" class="feature-svg-icon">
      <defs>
        <linearGradient id="exportGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#4facfe;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:1" />
        </linearGradient>
      </defs>
      <!-- 文档背景 -->
      <rect x="4" y="2" width="12" height="16" rx="2" fill="none" stroke="url(#exportGradient)" stroke-width="2"/>
      <!-- 文档内容 -->
      <line x1="7" y1="6" x2="13" y2="6" stroke="url(#exportGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="7" y1="9" x2="11" y2="9" stroke="url(#exportGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="7" y1="12" x2="12" y2="12" stroke="url(#exportGradient)" stroke-width="1.5" stroke-linecap="round"/>
      <!-- 下载箭头 -->
      <path d="M12 15v6" stroke="url(#exportGradient)" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M9 18l3 3 3-3" stroke="url(#exportGradient)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <!-- 底部平台 -->
      <line x1="6" y1="22" x2="18" y2="22" stroke="url(#exportGradient)" stroke-width="2" stroke-linecap="round"/>
    </svg>

    <!-- 默认图标 -->
    <div v-else class="default-icon">●</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type: 'search' | 'batch' | 'export' | 'default'
}

defineProps<Props>()
</script>

<style scoped>
.feature-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 4rem;
  height: 4rem;
  margin: 0 auto var(--space-md);
}

.feature-svg-icon {
  width: 100%;
  height: 100%;
  transition: all 0.3s ease;
}

.feature-svg-icon:hover {
  transform: scale(1.1);
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.default-icon {
  font-size: 3rem;
  color: var(--text-secondary);
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .feature-svg-icon {
    filter: brightness(1.1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-icon-wrapper {
    width: 3rem;
    height: 3rem;
  }
}
</style>
