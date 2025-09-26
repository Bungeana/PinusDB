import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // FastAPI 后端服务地址
  timeout: 10000,
})

// 查询蛋白信息
export function fetchProteinById(proteinId) {
  return api.get(`/protein/${proteinId}`)
}

// 模糊搜索候选
export function fetchProteinSuggestions(query) {
  return api.get(`/protein/suggest?q=${query}`)
}

// 执行 Blast 搜索
export function runBlastSearch(query) {
  return api.post('/blast', query )
}

// 获取表达量
export function fetchExpression(proteinId, dataset) {
  return api.get(`/expression?protein_id=${proteinId}&dataset=${dataset}`)
}

// 获取JBrowse Embed URL
export function getJBrowseEmbedUrl(species) {
  return api.get(`/jbrowse/embed?species=${species}`)
}