<template>
  <div class="about-container">
    <div class="container">
      <GlassContainer variant="card" class="page-header">
        <h1>ℹ️ 关于我们</h1>
        <p>了解IP查询工具的开发理念和技术特色</p>
      </GlassContainer>

      <div class="about-content">
        <GlassContainer variant="card" class="about-section">
          <h2>🌟 项目介绍</h2>
          <p>IP查询工具是一个现代化的网络工具，专注于提供快速、准确、专业的IP地址查询服务。我们致力于为用户提供最佳的查询体验和最准确的地理位置信息。</p>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>🎯 设计理念</h2>
          <ul>
            <li><strong>用户体验优先</strong>：简洁直观的界面设计，让查询变得简单高效</li>
            <li><strong>数据准确性</strong>：基于MaxMind GeoLite2数据库，确保查询结果的准确性</li>
            <li><strong>现代化设计</strong>：采用玻璃拟态设计风格，支持深色/浅色主题</li>
            <li><strong>响应式布局</strong>：完美适配各种设备，随时随地使用</li>
          </ul>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>🛠️ 技术栈</h2>
          <div class="tech-grid">
            <div class="tech-item">
              <h3>前端技术</h3>
              <ul>
                <li>Vue.js 3 + TypeScript</li>
                <li>Vite 构建工具</li>
                <li>现代CSS特性</li>
                <li>响应式设计</li>
              </ul>
            </div>
            <div class="tech-item">
              <h3>后端技术</h3>
              <ul>
                <li>Python + Flask</li>
                <li>GeoIP2 地理位置查询</li>
                <li>RESTful API设计</li>
                <li>CORS跨域支持</li>
              </ul>
            </div>
          </div>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>📊 功能特色</h2>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">🔍</div>
              <h3>精准查询</h3>
              <p>基于权威数据库，提供准确的IP地理位置信息</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">⚡</div>
              <h3>批量处理</h3>
              <p>支持最多100个IP地址同时查询，提高工作效率</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h3>数据导出</h3>
              <p>支持CSV、JSON、Excel多种格式导出</p>
            </div>

          </div>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>📈 版本历程</h2>
          <div class="version-timeline">
            <div class="version-item">
              <div class="version-number">v2.3</div>
              <div class="version-info">
                <h3>二级导航系统</h3>
                <p>实现层级化下拉菜单导航，优化用户体验</p>
              </div>
            </div>
            <div class="version-item">
              <div class="version-number">v2.2</div>
              <div class="version-info">
                <h3>UI美化升级</h3>
                <p>采用玻璃拟态设计，现代化界面风格</p>
              </div>
            </div>
            <div class="version-item">
              <div class="version-number">v2.1</div>
              <div class="version-info">
                <h3>功能完善</h3>
                <p>添加批量查询和导入导出功能</p>
              </div>
            </div>
            <div class="version-item">
              <div class="version-number">v2.0</div>
              <div class="version-info">
                <h3>架构重构</h3>
                <p>前后端分离重构，RESTful API设计</p>
              </div>
            </div>
          </div>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>📞 联系方式</h2>
          <p>如果您在使用过程中遇到问题或有改进建议，欢迎通过以下方式联系我们：</p>
          <ul>
            <li>📧 邮箱：support@ipquery.tool</li>
            <li>🐛 问题反馈：GitHub Issues</li>
            <li>💡 功能建议：GitHub Discussions</li>
          </ul>
        </GlassContainer>

        <GlassContainer variant="card" class="about-section">
          <h2>🙏 致谢</h2>
          <ul>
            <li><strong>MaxMind</strong> - 提供GeoLite2地理位置数据库</li>
            <li><strong>Vue.js</strong> - 优秀的前端框架</li>
            <li><strong>Flask</strong> - 轻量级Python Web框架</li>
            <li><strong>开源社区</strong> - 提供的各种工具和库支持</li>
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
.about-container {
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

.about-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.about-section h2 {
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  font-size: 1.5rem;
  font-weight: 600;
}

.about-section p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-sm);
}

.about-section ul {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-left: var(--space-lg);
}

.about-section li {
  margin-bottom: var(--space-xs);
}

.about-section strong {
  color: var(--text-primary);
  font-weight: 600;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-lg);
}

.tech-item h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
}

.feature-item {
  text-align: center;
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-sm);
}

.feature-item h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.version-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.version-item {
  display: flex;
  gap: var(--space-lg);
  align-items: flex-start;
}

.version-number {
  background: var(--primary-color);
  color: white;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

.version-info h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.version-info p {
  margin: 0;
}

@media (max-width: 768px) {
  .tech-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .version-item {
    flex-direction: column;
    gap: var(--space-sm);
  }
}
</style>
