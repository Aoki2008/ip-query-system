<template>
  <div class="guide-container">
    <div class="container">
      <GlassContainer variant="card" class="page-header">
        <h1>📖 使用指南</h1>
        <p>详细的使用教程，帮助您快速掌握IP查询工具的各项功能</p>
      </GlassContainer>

      <div class="guide-content">
        <GlassContainer variant="card" class="guide-section">
          <h2>🚀 快速开始</h2>
          <p>欢迎使用IP查询工具！本工具提供专业的IP地址查询服务，帮助您快速获取IP地址的详细信息。</p>
          
          <h3>基本功能</h3>
          <ul>
            <li><strong>单个查询</strong>：输入单个IP地址进行查询</li>
            <li><strong>批量查询</strong>：同时查询多个IP地址</li>
            <li><strong>查询历史</strong>：查看和管理历史查询记录</li>
          </ul>
        </GlassContainer>

        <GlassContainer variant="card" class="guide-section">
          <h2>🔍 如何使用IP查询功能</h2>
          
          <h3>单个IP查询</h3>
          <ol>
            <li>访问首页或点击"工具箱 → IP查询"</li>
            <li>在输入框中输入要查询的IP地址（如：8.8.8.8）</li>
            <li>点击"查询"按钮</li>
            <li>查看详细的查询结果</li>
          </ol>

          <h3>批量IP查询</h3>
          <ol>
            <li>在首页选择"批量查询"标签</li>
            <li>在文本框中输入多个IP地址，每行一个</li>
            <li>或者点击"导入文件"上传包含IP地址的文件</li>
            <li>点击"批量查询"按钮开始查询</li>
            <li>查看批量查询结果，支持导出为多种格式</li>
          </ol>
        </GlassContainer>

        <GlassContainer variant="card" class="guide-section">
          <h2>📊 查询结果说明</h2>
          <p>查询结果包含以下信息：</p>
          <ul>
            <li><strong>IP地址</strong>：查询的目标IP地址</li>
            <li><strong>地理位置</strong>：国家、省份、城市信息</li>
            <li><strong>ISP信息</strong>：互联网服务提供商</li>
            <li><strong>时区</strong>：所在时区信息</li>
            <li><strong>坐标</strong>：经纬度坐标（如果可用）</li>
          </ul>
        </GlassContainer>

        <GlassContainer variant="card" class="guide-section">
          <h2>🎨 界面功能</h2>
          
          <h3>主题切换</h3>
          <p>点击右上角的主题切换按钮（🌙/☀️）可以在深色和浅色主题之间切换。</p>
          
          <h3>响应式设计</h3>
          <p>本工具支持各种设备，包括桌面电脑、平板和手机，界面会自动适配不同屏幕尺寸。</p>
        </GlassContainer>

        <GlassContainer variant="card" class="guide-section">
          <h2>💡 使用技巧</h2>
          <ul>
            <li>支持IPv4地址格式，如：192.168.1.1、8.8.8.8等</li>
            <li>批量查询最多支持100个IP地址</li>
            <li>查询历史会自动保存最近的查询记录</li>
            <li>可以使用示例IP功能快速体验查询效果</li>
            <li>支持拖拽文件到批量查询区域进行导入</li>
          </ul>
        </GlassContainer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import GlassContainer from '../components/GlassContainer.vue'
</script>

<style scoped>
.guide-container {
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1024px; /* 与导航栏保持一致 */
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.guide-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.guide-section h2 {
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  font-size: 1.5rem;
  font-weight: 600;
}

.guide-section h3 {
  color: var(--text-primary);
  margin: var(--space-md) 0 var(--space-sm) 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.guide-section p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-sm);
}

.guide-section ul, 
.guide-section ol {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-left: var(--space-lg);
  margin-bottom: var(--space-sm);
}

.guide-section li {
  margin-bottom: var(--space-xs);
}

.guide-section strong {
  color: var(--text-primary);
  font-weight: 600;
}
</style>
