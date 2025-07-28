<template>
  <div 
    class="glass-container" 
    :class="[variant, { 'fade-in': animated }]"
    @click="handleClick"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'card' | 'input' | 'button'
  animated?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

withDefaults(defineProps<Props>(), {
  variant: 'card',
  animated: true
})

const emit = defineEmits<Emits>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style scoped>
/* 组件特定样式已在全局样式中定义 */
</style>
