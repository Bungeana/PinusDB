<template>
  <div class="home bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-10">
      
      <div class="hero bg-emerald-500 text-white p-10 md:p-16 rounded-2xl shadow-lg text-center mb-12 border-2 border-green-100">
        <h2 class="text-4xl md:text-5xl font-bold mb-4">Welcome to PinusDB</h2>
        <p class="text-lg md:text-xl opacity-90 mb-4">
          Plant Genome Database Platform
        </p>  
      </div>


      <el-card v-if="error" class="mb-8 p-6 text-center bg-red-50 border border-red-200">
        <span class="text-red-600 font-medium">{{ error }}</span>
      </el-card>

      <div class="grid md:grid-cols-3 md:gap-8">
        
        <div class="md:col-span-2">
          <el-card v-if="data" class="p-4">
            <template #header>
              <div class="text-xl font-semibold text-green-800">Genome Database Overview</div>
            </template>
            <div class="space-y-4 text-base text-gray-700">
              <p><b>Total proteins:</b> {{ data.total_proteins }}</p>
              <p><b>Total species:</b> {{ data.total_species }}</p>
              <p><b>Genome version:</b> {{ data.genome_version }}</p>
            </div>
          </el-card>
        </div>

        <div class="md:col-span-1 mt-8 md:mt-0">
          <el-card class="p-4">
            <template #header>
              <div class="relative">
                <h3 class="text-xl font-semibold text-green-800">Latest Updates</h3>
              </div>
            </template>
            <p class="text-gray-600 leading-relaxed">
              PinusDB is constantly updated with new data and features. Check back regularly for the latest additions.
            </p>
          </el-card>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const data = ref({
  total_proteins: 123456,
  total_species: 20,
  genome_version: 'v1.0'
})
const error = ref(null)


</script>