<template>
  <img
    :src="logoSrc"
    alt="Reflection"
    class="logo-image"
    :style="{ width: width, height: height }"
  />
</template>

<script setup>
import logoSrc from '@/assets/logo.png';

// Define props for flexibility
const props = defineProps({
  width: {
    type: [String, Number],
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: 'auto'
  }
});
</script>

<style scoped>
.logo-image {
  display: block;
  object-fit: contain;
  animation: fadeIn 1.5s ease-in-out forwards;
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
</style>
