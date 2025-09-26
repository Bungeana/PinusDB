<template>
  <div class="expression-page container mx-auto p-4 md:p-6 min-h-screen">
    <el-card class="mb-6 border-l-4 border-green-500">
      <div class="flex flex-col sm:flex-row items-center justify-center p-4">
        <h2 class="text-2xl font-bold text-green-800 mb-4 sm:mb-0 sm:mr-6 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="w-6 h-6 mr-2 text-green-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
          </svg>    
          Protein Expression
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
            :loading="loading"
          >
            Search
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card v-if="error" class="mb-6 bg-red-50 border border-red-300 text-red-700 p-4 text-center">
      <p class="font-medium">{{ error }}</p>
    </el-card>

    <el-card v-if="expressionData" class="p-4 md:p-6">
      <div class="result-header flex flex-col md:flex-row justify-between items-start md:items-center mb-6 pb-4 border-b border-green-100">
        <h3 class="text-2xl font-semibold text-green-800 mb-2 md:mb-0 flex items-center">
          <svg class="w-6 h-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
          </svg>
          Expression Result
        </h3>
        <div class="flex items-center space-x-3 bg-gray-50 px-4 py-2 rounded-lg border border-gray-100 shadow-sm">
            <span class="text-gray-700 font-medium whitespace-nowrap">Dataset:</span>
            <el-select 
                v-model="selectedDataset" 
                placeholder="Select Dataset" 
                @change="handleSearch"
                size="default"
                class="min-w-[180px] max-w-[220px]"
                style="--el-select-bg-color: #ffffff; --el-border-color: #e5e7eb; --el-select-focus-border-color: #059669; --el-select-hover-border-color: #8FBC8F;"
            >
                <el-option 
                    label="E-GEOD-38612" 
                    value="E-GEOD-38612"
                    class="py-2"
                ></el-option>
            </el-select>
        </div>
      </div>

      <div class="protein-info mb-6 text-center md:text-left">
        <h4 class="text-xl font-bold text-green-800 mb-2">{{ expressionData.protein_id }}</h4>
        <div class="info-row">
          <span class="info-item text-gray-600"><strong>Gene Name:</strong> {{ expressionData.gene_name }}</span>
        </div>
      </div>

      <div ref="chartContainer" class="w-full h-[400px] md:h-[500px] mt-4 rounded-lg shadow-sm border border-gray-100"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { fetchProteinSuggestions, fetchExpression } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const searchText = ref('')
const selectedProtein = ref(null)
const expressionData = ref(null)
const loading = ref(false)
const error = ref(null)
const selectedDataset = ref('E-GEOD-38612') // 默认数据集

const chartContainer = ref(null)
let chartInstance = null

// 监听 expressionData 的变化，当数据更新时重新渲染图表
watch(expressionData, (newData) => {
  if (newData) {
    // 使用 nextTick 确保 DOM 已经更新
    nextTick(() => {
      initChart()
    })
  }
})

// 初始化并渲染 ECharts 图表
const initChart = () => {
  if (!chartContainer.value || !expressionData.value) return

  // 计算每个样本的平均表达量
  const expression = expressionData.value.expression
  const sampleNames = Object.keys(expression)
  const averageValues = Object.values(expression).map(arr => {
    if (!arr || arr.length === 0) return 0
    const sum = arr.reduce((a, b) => a + b, 0)
    return (sum / arr.length).toFixed(2) // 保留两位小数
  })

  // 销毁旧实例（如果存在）
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartContainer.value)

  const option = {
    backgroundColor: '#ffffff',
    title: {
      text: `Expression of ${expressionData.value.gene_name} (${expressionData.value.protein_id})`,
      subtext: `Dataset: ${expressionData.value.dataset}`,
      left: 'center',
      top: 10,
      textStyle: {
        fontWeight: 'bold',
        color: '#1f2937'
      },
      subtextStyle: {
        color: '#6b7280'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      formatter: function(params) {
        const dataIndex = params[0].dataIndex;
        const sampleName = sampleNames[dataIndex];
        const tpmValue = averageValues[dataIndex];
        return `${sampleName}<br/>Expression Level: <strong style="color: #059669;">${tpmValue} TPM</strong>`;
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: {
        color: '#374151'
      }
    },
    xAxis: {
      type: 'category',
      data: sampleNames,
      axisLabel: {
        interval: 0,
        rotate: 45,
        color: '#6b7280',
        fontWeight: '500',
        fontSize: 14
      },
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: 'TPM(Transcripts Per Million)',
      nameTextStyle: {
        color: '#6b7280',
        fontWeight: '500',
        padding: [0, 0, 10, 60]
      },
      axisLabel: {
        color: '#6b7280'
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#f3f4f6',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        data: averageValues,
        type: 'bar',
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(180, 180, 180, 0.1)'
        },
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ]),
          borderRadius: [4, 4, 0, 0],
          shadowBlur: 8,
          shadowColor: 'rgba(16, 185, 129, 0.2)',
          shadowOffsetY: 4
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#059669' },
              { offset: 1, color: '#047857' }
            ]),
            shadowBlur: 12,
            shadowColor: 'rgba(16, 185, 129, 0.3)'
          }
        },
        animationDuration: 1000,
        animationEasing: 'cubicOut',
        animationDelay: function(idx) {
          return idx * 50; // 每个柱子错开动画
        }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%', // 增加底部边距以容纳旋转的标签
      top: '15%',
      containLabel: true
    },
    dataZoom: [ // 添加缩放功能
      {
        type: 'slider',
        start: 0,
        end: sampleNames.length > 20 ? 50 : 100,
        height: 30,
        bottom: 10,
        backgroundColor: '#f9fafb',
        borderColor: '#e5e7eb',
        fillerColor: 'rgba(16, 185, 129, 0.2)',
        handleStyle: {
          color: '#059669'
        },
        textStyle: {
          color: '#6b7280'
        }
      }
    ]
  }

  chartInstance.setOption(option)
  
  // 监听窗口大小变化以实现图表自适应
  window.addEventListener('resize', () => {
      if(chartInstance) {
          chartInstance.resize()
      }
  })
}

// 获取蛋白 ID 搜索建议
const querySearch = async (queryString, cb) => {
  if (!queryString) return cb([])
  try {
    const res = await fetchProteinSuggestions(queryString)
    cb(res.data.map(item => ({ value: item })))
  } catch (err) {
    console.error("Failed to fetch suggestions:", err)
    cb([])
  }
}

// 处理从建议列表中选择
const handleSelect = (item) => {
  selectedProtein.value = item.value
}

// 清除搜索框
const handleClear = () => {
  selectedProtein.value = null
  expressionData.value = null
  error.value = null
}

// 执行搜索
const handleSearch = () => {
  if (!selectedProtein.value) {
    ElMessage.warning('Please select a protein ID from the suggestions.')
    return
  }
  loading.value = true
  error.value = null
  expressionData.value = null // 清空旧数据

  fetchExpression(selectedProtein.value, selectedDataset.value)
    .then((res) => {
      expressionData.value = res.data
    })
    .catch((err) => {
      error.value = `Protein expression data not found for ${selectedProtein.value}.`
      console.error(err)
    })
    .finally(() => {
      loading.value = false
    })
}
</script>
