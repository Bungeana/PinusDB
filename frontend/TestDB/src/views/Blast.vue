<template>
  <div class="blast-container container mx-auto p-4 md:p-6 min-h-screen">
    <el-card class="p-4 md:p-6 border-l-4 border-green-500">
      <h2 class="text-2xl font-bold text-green-800 mb-6 text-center flex items-center justify-center">
        <svg class="w-6 h-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        BLAST Search
      </h2>

      <form @submit.prevent="runBlast" class="space-y-6">
        <div>
          <label for="sequence" class="block text-base font-medium text-green-700 mb-1">Type your sequence:</label>
          <textarea 
            v-model="sequence" 
            id="sequence" 
            rows="6" 
            placeholder="Enter your DNA or protein sequence"
            class="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500 transition shadow-sm hover:shadow-md"
          ></textarea>
        </div>

        <div class="space-y-2">
          <label for="program" class="block text-base font-medium text-green-700 mb-1">Select program:</label>
          <select 
            v-model="program" 
            id="program" 
            class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all shadow-sm hover:shadow-md hover:border-green-400 appearance-none bg-white cursor-pointer relative pr-10"
            style="background-image: url('data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 24 24\' stroke-width=\'1.5\' stroke=\'%23059669\' class=\'w-5 h-5\'%3E%3Cpath stroke-linecap=\'round\' stroke-linejoin=\'round\' d=\'M19.5 8.25l-7.5 7.5-7.5-7.5\'/%3E%3C/svg%3E'); background-repeat: no-repeat; background-position: right 0.75rem center; background-size: 1.5em 1.5em;"
          >
            <option value="blastn">blastn (nucleotide alignment)</option>
            <option value="blastp">blastp (protein alignment)</option>
          </select>
        </div>

        <div class="space-y-2">
          <label for="db" class="block text-base font-medium text-green-700 mb-1">Select database:</label>
          <select 
            v-model="db" 
            id="db" 
            class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all shadow-sm hover:shadow-md hover:border-green-400 appearance-none bg-white cursor-pointer relative pr-10"
            style="background-image: url('data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 24 24\' stroke-width=\'1.5\' stroke=\'%23059669\' class=\'w-5 h-5\'%3E%3Cpath stroke-linecap=\'round\' stroke-linejoin=\'round\' d=\'M19.5 8.25l-7.5 7.5-7.5-7.5\'/%3E%3C/svg%3E'); background-repeat: no-repeat; background-position: right 0.75rem center; background-size: 1.5em 1.5em;"
          >
            <option value="At_nuc">Arabidopsis thaliana nucleotide database</option>
            <option value="At_pro">Arabidopsis thaliana protein database</option>
          </select>
        </div>
        
        <div class="text-center">
            <button 
              type="submit" 
              :disabled="loading || !sequence" 
              class="w-full md:w-auto px-8 py-3 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all transform hover:scale-105"
            >
              {{ loading ? "Running..." : "Submit BLAST" }}
            </button>
        </div>
      </form>
    </el-card>

    <div v-if="parsedResults.length" class="mt-8">
      <h3 class="text-xl font-semibold text-green-800 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        BLAST Results:
      </h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-600 border border-gray-200 rounded-lg shadow-md">
          <thead class="text-xs text-green-800 uppercase bg-green-50">
            <tr>
              <th v-for="header in tableHeaders" :key="header" class="px-6 py-3 text-center whitespace-nowrap border border-gray-200">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in parsedResults" :key="index" class="bg-white border-b border-gray-200 odd:bg-white even:bg-green-50 hover:bg-green-100 transition-colors">
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.query_id }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.subject_id }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.identity }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.align_length }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.mismatches }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.gap_opens }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.q_start }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.q_end }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.s_start }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.s_end }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.evalue }}</td>
              <td class="px-6 py-4 text-center border border-gray-200">{{ row.bit_score }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-if="error" class="mt-8 p-4 bg-red-50 border border-red-300 text-red-700 rounded-lg">
      <h3 class="font-bold">Error:</h3>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { runBlastSearch } from "../api";

export default {
  name: "Blast",
  data() {
    return {
      sequence: "",
      program: "blastn",
      db: "At_nuc",
      parsedResults: [],
      error: null,
      loading: false,
      tableHeaders: ['Query ID', 'Subject ID', '% Identity', 'Align Length', 'Mismatches', 'Gap Opens', 'Q. Start', 'Q. End', 'S. Start', 'S. End', 'E-value', 'Bit Score']
    };
  },
  methods: {
    async runBlast() {
      this.parsedResults = [];
      this.error = null;
      this.loading = true;
      try {
        const response = await runBlastSearch({
          sequence: this.sequence,
          program: this.program,
          db: this.db,
        });

        if (response.data.status === "success") {
          this.parsedResults = response.data.results;
        } else {
          this.error = response.data.message || "BLAST search failed";
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>