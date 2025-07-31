<template>
  <div class="app-logo" :class="{ 'logo-small': size === 'small', 'logo-large': size === 'large' }">
    <!-- IP查询系统Logo - 网络节点设计 -->
    <svg viewBox="0 0 48 48" class="logo-svg">
      <defs>
        <!-- 主要渐变 - 蓝色到紫色 -->
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
          <stop offset="50%" style="stop-color:#7c3aed;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#2563eb;stop-opacity:1" />
        </linearGradient>
        
        <!-- 辅助渐变 - 青色高光 -->
        <linearGradient id="logoAccent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:0.8" />
          <stop offset="100%" style="stop-color:#0891b2;stop-opacity:0.6" />
        </linearGradient>
        
        <!-- 发光效果 -->
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- 外圈 - 代表全球网络 -->
      <circle cx="24" cy="24" r="20" fill="none" stroke="url(#logoGradient)" stroke-width="2" opacity="0.6"/>
      
      <!-- 中心节点 - 代表查询核心 -->
      <circle cx="24" cy="24" r="6" fill="url(#logoGradient)" filter="url(#glow)"/>
      
      <!-- 网络连接线 -->
      <g stroke="url(#logoGradient)" stroke-width="1.5" opacity="0.7">
        <!-- 主要连接线 -->
        <line x1="24" y1="18" x2="24" y2="8" stroke-linecap="round"/>
        <line x1="24" y1="30" x2="24" y2="40" stroke-linecap="round"/>
        <line x1="18" y1="24" x2="8" y2="24" stroke-linecap="round"/>
        <line x1="30" y1="24" x2="40" y2="24" stroke-linecap="round"/>
        
        <!-- 对角连接线 -->
        <line x1="19.8" y1="19.8" x2="13.8" y2="13.8" stroke-linecap="round"/>
        <line x1="28.2" y1="28.2" x2="34.2" y2="34.2" stroke-linecap="round"/>
        <line x1="28.2" y1="19.8" x2="34.2" y2="13.8" stroke-linecap="round"/>
        <line x1="19.8" y1="28.2" x2="13.8" y2="34.2" stroke-linecap="round"/>
      </g>
      
      <!-- 外围节点 - 代表IP地址 -->
      <g fill="url(#logoAccent)">
        <circle cx="24" cy="8" r="2"/>
        <circle cx="24" cy="40" r="2"/>
        <circle cx="8" cy="24" r="2"/>
        <circle cx="40" cy="24" r="2"/>
        <circle cx="13.8" cy="13.8" r="1.5"/>
        <circle cx="34.2" cy="34.2" r="1.5"/>
        <circle cx="34.2" cy="13.8" r="1.5"/>
        <circle cx="13.8" cy="34.2" r="1.5"/>
      </g>
      
      <!-- 数据流动效果 -->
      <g class="data-flow">
        <circle cx="24" cy="12" r="1" fill="url(#logoAccent)" opacity="0.8">
          <animate attributeName="cy" values="12;36;12" dur="3s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.8;0.3;0.8" dur="3s" repeatCount="indefinite"/>
        </circle>
        <circle cx="16" cy="24" r="1" fill="url(#logoAccent)" opacity="0.8">
          <animate attributeName="cx" values="16;32;16" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2.5s" repeatCount="indefinite"/>
        </circle>
      </g>
      
      <!-- 中心高光 -->
      <circle cx="21" cy="21" r="2" fill="url(#logoAccent)" opacity="0.4"/>
    </svg>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'small' | 'normal' | 'large'
}

withDefaults(defineProps<Props>(), {
  size: 'normal'
})
</script>

<style scoped>
.app-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.logo-svg {
  width: 2.5rem;
  height: 2.5rem;
  transition: all 0.3s ease;
}

.logo-small .logo-svg {
  width: 1.5rem;
  height: 1.5rem;
}

.logo-large .logo-svg {
  width: 4rem;
  height: 4rem;
}

.app-logo:hover .logo-svg {
  transform: scale(1.05);
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .logo-svg {
    filter: brightness(1.1);
  }
}

/* 数据流动动画在移动设备上禁用以节省性能 */
@media (max-width: 768px) {
  .data-flow {
    display: none;
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .logo-svg {
    width: 2rem;
    height: 2rem;
  }
  
  .logo-large .logo-svg {
    width: 3rem;
    height: 3rem;
  }
}
</style>
