<template>
  <button 
    class="theme-toggle" 
    @click="toggleTheme"
    :aria-label="isDark ? '切换到浅色主题' : '切换到深色主题'"
  >
    <span>{{ isDark ? '☀️' : '🌙' }}</span>
  </button>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isDark = ref(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  // 从localStorage读取主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
    document.documentElement.setAttribute('data-theme', savedTheme)
  } else {
    // 默认使用深色主题
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<style scoped>
/* 主题切换按钮样式已在全局样式中定义 */
</style>
