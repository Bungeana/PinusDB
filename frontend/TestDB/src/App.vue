<template>
  <div class="flex flex-col min-h-screen bg-gray-50 text-gray-800">
    <Navbar />
    
    <main class="flex-grow">
      <RouterView />
    </main>

    <footer class="bg-white border-t border-gray-200">
      <div class="container mx-auto py-4 px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
        <p>&copy; 2025 PinusDB Protein Database</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import { RouterView } from 'vue-router';
</script>