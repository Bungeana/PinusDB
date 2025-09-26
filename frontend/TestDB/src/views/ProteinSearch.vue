<template>
  <div class="protein-search-page container mx-auto p-4 md:p-6 min-h-screen">
    <el-card class="mb-6 border-l-4 border-green-500">
      <div class="flex flex-col sm:flex-row items-center justify-center p-4">
        <h2 class="text-2xl font-bold text-green-800 mb-4 sm:mb-0 sm:mr-6 flex items-center">
          <svg class="w-6 h-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Protein Search
        </h2>
        <div class="flex items-center">
          <el-autocomplete
            v-model="searchText"
            :fetch-suggestions="querySearch"
            placeholder="Please input protein ID"
            @select="handleSelect"
            @clear="handleClear"
            clearable
            @keyup.enter.native="handleSearch"
          />
          <el-button
            type="success"
            :disabled="!selectedProtein || !searchText"
            @click="handleSearch"
            class="ml-4 hover:scale-105"
          >
            Search
          </el-button>
        </div>
      </div>
    </el-card>


    <el-card v-if="error" class="mb-6 bg-red-50 border border-red-300 text-red-700 p-4 text-center">
      <p class="font-medium">{{ error }}</p>
    </el-card>

    <el-card v-if="protein" class="p-4 md:p-6">
      <div class="result-header flex flex-col md:flex-row justify-between items-start md:items-center mb-6 pb-4 border-b border-green-100">
        <h3 class="text-2xl font-semibold text-green-800 mb-2 md:mb-0 flex items-center">
          <svg class="w-5 h-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Search Result
        </h3>
        <el-button
          type="success"
          @click="copySequence"
          :disabled="!protein.sequence"
          class="hover:scale-105"
        >
          <i class="el-icon-document-copy mr-2"></i> Copy Sequence
        </el-button>
      </div>

      <div class="protein-info mb-6 text-center md:text-left">
        <h4 class="text-xl font-bold text-green-800 mb-2">{{ protein.protein_id }}</h4>
        <div class="info-row">
          <span class="info-item text-gray-600"><strong>Length:</strong> {{ protein.length }} amino acids</span>
        </div>
      </div>

      <div v-if="protein.sequence" class="sequence-display text-left">
        <div class="sequence-header flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
          <h5 class="text-lg font-medium text-green-800 mb-2 sm:mb-0 flex items-center">
          <svg class="w-5 h-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Sequence
        </h5>
          <el-select v-model="sequenceFormat" placeholder="Format" size="small" @change="formatSequence" class="w-64 p-2">
            <el-option label="Default" value="default"></el-option>
            <el-option label="60 per line" value="60"></el-option>
            <el-option label="80 per line" value="80"></el-option>
          </el-select>
        </div>
        
        <div class="scrollable-sequence-container h-72 overflow-y-auto border rounded-lg bg-gray-50 p-4 hover:border-green-600 transition-colors">
          <pre class="font-mono text-sm text-green-900 leading-relaxed whitespace-pre-wrap break-words">{{ formattedSequence }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { fetchProteinById, fetchProteinSuggestions } from '../api'
import { ElMessage } from 'element-plus'

const searchText = ref('')
const selectedProtein = ref(null)
const protein = ref(null)
const loading = ref(false)
const error = ref(null)
const sequenceFormat = ref('60')

const formattedSequence = computed(() => {
  if (!protein.value?.sequence) return ''
  const seq = protein.value.sequence
  if (sequenceFormat.value === 'default') return seq
  const lineLength = parseInt(sequenceFormat.value)
  const lines = []
  for (let i = 0; i < seq.length; i += lineLength) {
    lines.push(seq.substring(i, i + lineLength))
  }
  return lines.join('\n')
})

const querySearch = async (queryString, cb) => {
  if (!queryString) return cb([])
  try {
    const res = await fetchProteinSuggestions(queryString)
    cb(res.data.map(item => ({ value: item })))
  } catch (err) {
    cb([])
  }
}

const handleSelect = (item) => {
  selectedProtein.value = item.value
}

const handleClear = () => {
  selectedProtein.value = null
}

const handleSearch = () => {
  if (!selectedProtein.value) return
  loading.value = true
  error.value = null
  protein.value = null

  fetchProteinById(selectedProtein.value)
    .then((res) => { protein.value = res.data })
    .catch(() => { error.value = 'Protein not found!' })
    .finally(() => { loading.value = false })
}

const copySequence = () => {
  if (protein.value?.sequence) {
    navigator.clipboard.writeText(protein.value.sequence)
      .then(() => ElMessage.success('Sequence copied to clipboard!'))
      .catch(() => ElMessage.error('Failed to copy sequence'))
  }
}

const formatSequence = () => {
  // Computed property handles the update automatically
}
</script>