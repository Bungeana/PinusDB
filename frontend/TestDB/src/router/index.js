import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ProteinSearch from '../views/ProteinSearch.vue'
import Blast from '../views/Blast.vue'
import JBrowse from '../views/JBrowse.vue'
import Expression from '../views/Expression.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/protein-search', name: 'ProteinSearch', component: ProteinSearch },
  { path: '/blast', name: 'Blast', component: Blast },
  { path: '/jbrowse', name: 'JBrowse', component: JBrowse },
  { path: '/expression', name: 'Expression', component: Expression },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
