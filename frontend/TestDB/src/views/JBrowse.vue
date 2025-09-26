<template>
  <div class="genome-browser container mx-auto p-4 md:p-6 flex flex-col h-full min-h-screen">
    <div class="controls mb-4 flex items-center space-x-3 bg-gray-50 p-4 rounded-md border border-gray-200 shadow-lg">
      <label for="species" class="text-lg font-medium text-green-800 flex items-center">
        <svg class="w-6 h-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        Select Species:
      </label>
      <el-select 
        v-model="selectedSpecies" 
        placeholder="Select Species"
        @change="loadSession"
        size="default"
        class="min-w-[180px] max-w-[220px]"
        style="--el-select-bg-color: #ffffff; --el-border-color: #e5e7eb; --el-select-focus-border-color: #059669; --el-select-hover-border-color: #8FBC8F;"
      >
        <el-option 
          label="Arabidopsis thaliana" 
          value="arabidopsis thaliana"
          class="py-2"
        ></el-option>
        <el-option 
          label="Human (hg38)" 
          value="hg38"
          class="py-2"
        ></el-option>
        <el-option 
          label="Pinus" 
          value="pine"
          class="py-2"
        ></el-option>
      </el-select>
    </div>

    <div class="flex-grow">
      <iframe
        v-if="iframeSrc"
        :src="iframeSrc"
        class="w-full h-[85vh] border border-gray-300 rounded-lg shadow-md"
        frameborder="0"
      ></iframe>
      <div v-else class="w-full h-[85vh] border border-gray-300 rounded-lg shadow-md flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center justify-center">
          <svg class="w-10 h-10 text-green-500 animate-spin mb-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-green-700">Loading Genome Browser...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getJBrowseEmbedUrl } from "../api";

export default {
  name: "GenomeBrowser",
  data() {
    return {
      selectedSpecies: "arabidopsis thaliana", // Default species
      iframeSrc: null,
    };
  },
  methods: {
    async loadSession() {
      this.iframeSrc = null; // Show loading state
      try {
        const res = await getJBrowseEmbedUrl(this.selectedSpecies);
        this.iframeSrc = res.data.url;
        console.log("JBrowse URL:", this.iframeSrc);  
      } catch (err) {
        console.error("Failed to load session:", err);
        // Optionally, show an error message to the user
      }
    },
  },
  mounted() {
    this.loadSession();
  },
};
</script>