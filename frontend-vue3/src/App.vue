<script setup lang="ts">
import Navigation from './components/Navigation.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <div id="app">
    <ThemeToggle />
    <Navigation />
    <main>
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

main {
  padding: var(--space-xl) 0;
}
</style>
