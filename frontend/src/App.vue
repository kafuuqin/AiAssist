<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <RouterView />
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: radial-gradient(circle at 10% 20%, #f5f7ff 0, #eef2ff 30%, #fdfbff 65%, #ffffff 100%);
}
</style>
