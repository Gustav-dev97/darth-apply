<script setup lang="ts">
import ProfileView from "./components/ProfileView.vue";
</script>

<template>
  <main>
    <ProfileView />
  </main>
</template>

<style>
body {
  margin: 0;
  background: #f7f7f7;
  color: #111;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

main {
  min-height: 100vh;
}
</style>