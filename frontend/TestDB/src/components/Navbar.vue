<template>
  <nav class="bg-white shadow-md border-b border-green-100 sticky top-0 z-50 transition-all duration-300 ease-in-out">
    <div class="container mx-auto flex items-center justify-between px-6 py-3">
      <h1 class="text-3xl font-bold text-green-800 tracking-wide transform hover:scale-105 transition-transform duration-300">
        <span class="text-green-700">Pinus</span><span class="text-gray-700">DB</span>
      </h1>
      
      <ul class="hidden md:flex space-x-8 text-gray-700 font-medium">
        <li v-for="link in navLinks" :key="link.to">
          <router-link 
            :to="link.to" 
            class="relative hover:text-green-600 transition-colors duration-300 py-2 group"
            active-class="text-green-600"
          >
            {{ link.name }}
            <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-green-600 transition-all duration-300 group-hover:w-full"></span>
          </router-link>
        </li>
      </ul>

      <button 
        class="md:hidden text-gray-700 hover:text-green-600 focus:outline-none" 
        @click="isMobileMenuOpen = !isMobileMenuOpen"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="isMobileMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'" />
        </svg>
      </button>
    </div>
    
    <div v-if="isMobileMenuOpen" class="md:hidden bg-white border-t border-gray-100 animate-fadeIn">
      <ul class="px-2 pt-2 pb-3 space-y-1">
        <li v-for="link in navLinks" :key="link.to">
          <router-link 
            :to="link.to" 
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-green-600 hover:bg-green-50 transition-colors duration-200"
            active-class="bg-green-50 text-green-600"
            @click="isMobileMenuOpen = false"
          >
            {{ link.name }}
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Home', to: '/' },
  { name: 'Protein Search', to: '/protein-search' },
  { name: 'BLAST', to: '/blast' },
  { name: 'JBrowse', to: '/jbrowse' },
  { name: 'Expression', to: '/expression' }
]
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>