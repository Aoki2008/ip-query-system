<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>IP查询工具</h3>
          <p>快速、准确、专业的IP地址查询服务</p>
        </div>
        
        <div class="footer-section">
          <h4>快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/ip-lookup">IP查询</router-link></li>
            <li><router-link to="/guide">使用指南</router-link></li>
            <li><router-link to="/about">关于我们</router-link></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>技术支持</h4>
          <ul class="footer-links">
            <li><router-link to="/faq">常见问题</router-link></li>
            <li><a href="mailto:support@example.com">技术支持</a></li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="footer-legal">
          <p>&copy; 2025 IP查询工具. 保留所有权利.</p>
          <p>
            <a 
              href="https://beian.miit.gov.cn/" 
              target="_blank" 
              rel="noopener noreferrer"
              class="beian-link"
            >
              京ICP备12345678号-1
            </a>
          </p>
        </div>
        <div class="footer-tech">
          <p>基于 MaxMind GeoLite2 数据库</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  margin-top: auto;
  padding: var(--space-xl) 0 var(--space-lg);
}

.footer-container {
  max-width: 1024px; /* 与导航栏保持一致的宽度 */
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: var(--space-xl);
  margin-bottom: var(--space-xl);
}

.footer-section h3 {
  color: var(--primary-color);
  margin-bottom: var(--space-md);
  font-size: 1.25rem;
}

.footer-section h4 {
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  font-size: 1rem;
}

.footer-section p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: var(--space-sm);
}

.footer-links a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: var(--primary-color);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-lg);
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.footer-legal p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

.beian-link {
  color: var(--text-muted) !important;
  text-decoration: none;
  transition: color 0.2s ease;
}

.beian-link:hover {
  color: var(--primary-color) !important;
}

.footer-tech p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: var(--space-sm);
  }
  
  .footer {
    padding: var(--space-lg) 0;
  }
}

@media (max-width: 480px) {
  .footer-container {
    padding: 0 var(--space-md);
  }
  
  .footer-content {
    gap: var(--space-md);
  }
}
</style>
