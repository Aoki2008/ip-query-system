<template>
  <div class="faq-container">
    <div class="container">
      <GlassContainer variant="card" class="page-header">
        <h1>❓ 常见问题</h1>
        <p>常见问题解答，帮助您解决使用过程中遇到的问题</p>
      </GlassContainer>

      <div class="faq-content">
        <GlassContainer variant="card" class="faq-item" v-for="(faq, index) in faqs" :key="index">
          <h3 class="faq-question">{{ faq.question }}</h3>
          <div class="faq-answer" v-html="faq.answer"></div>
        </GlassContainer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import GlassContainer from '../components/GlassContainer.vue'

const faqs = ref([
  {
    question: '查询结果为什么显示"未知"？',
    answer: `
      <p>可能的原因包括：</p>
      <ul>
        <li>该IP地址是私有IP地址（如192.168.x.x、10.x.x.x等）</li>
        <li>IP地址未被收录在我们的数据库中</li>
        <li>该IP地址的地理位置信息不完整</li>
        <li>网络连接问题导致查询失败</li>
      </ul>
    `
  },
  {
    question: '能否查询本机IP地址？',
    answer: `
      <p>可以！有以下几种方式：</p>
      <ul>
        <li>首页会自动显示您当前设备的公网IP地址信息</li>
        <li>在查询框中输入您的公网IP地址进行查询</li>
        <li>注意：私有IP地址（如192.168.1.1）无法查询到地理位置信息</li>
      </ul>
    `
  },
  {
    question: '支持哪些IP地址格式？',
    answer: `
      <p>目前支持以下格式：</p>
      <ul>
        <li><strong>IPv4地址</strong>：如8.8.8.8、114.114.114.114</li>
        <li><strong>标准格式</strong>：四个0-255之间的数字，用点分隔</li>
        <li><strong>批量格式</strong>：每行一个IP地址，最多100个</li>
      </ul>
      <p><strong>注意</strong>：暂不支持IPv6地址格式。</p>
    `
  },
  {
    question: '⚡ 批量查询有什么限制？',
    answer: `
      <ul>
        <li><strong>数量限制</strong>：最多支持100个IP地址同时查询</li>
        <li><strong>格式要求</strong>：每行一个IP地址</li>
        <li><strong>文件支持</strong>：支持.txt和.csv格式文件导入</li>
        <li><strong>查询速度</strong>：采用并发查询，提高查询效率</li>
      </ul>
    `
  },
  {
    question: '💾 查询历史如何管理？',
    answer: `
      <ul>
        <li><strong>自动保存</strong>：查询记录会自动保存到本地</li>
        <li><strong>记录数量</strong>：最多保存最近100条查询记录</li>
        <li><strong>搜索功能</strong>：支持按IP地址或位置信息搜索</li>
        <li><strong>导出功能</strong>：可以导出历史记录为CSV或JSON格式</li>
        <li><strong>清空记录</strong>：可以一键清空所有历史记录</li>
      </ul>
    `
  },
  {
    question: '🎨 如何切换主题？',
    answer: `
      <p>点击页面右上角的主题切换按钮：</p>
      <ul>
        <li><strong>🌙 深色主题</strong>：适合夜间使用，保护眼睛</li>
        <li><strong>☀️ 浅色主题</strong>：适合白天使用，界面清爽</li>
        <li><strong>自动保存</strong>：您的主题选择会被自动保存</li>
      </ul>
    `
  }
])
</script>

<style scoped>
.faq-container {
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

.faq-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.faq-item {
  transition: all 0.3s ease;
}

.faq-item:hover {
  transform: translateY(-2px);
}

.faq-question {
  color: var(--text-primary);
  margin-bottom: var(--space-md);
  font-size: 1.2rem;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--space-sm);
}

.faq-answer {
  color: var(--text-secondary);
  line-height: 1.6;
}

.faq-answer :deep(p) {
  margin-bottom: var(--space-sm);
}

.faq-answer :deep(ul) {
  margin-left: var(--space-lg);
  margin-bottom: var(--space-sm);
}

.faq-answer :deep(li) {
  margin-bottom: var(--space-xs);
}

.faq-answer :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}
</style>
