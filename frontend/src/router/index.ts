import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView        from '../views/HomeView.vue'
import UploadView      from '../views/UploadView.vue'
import ReportsView     from '../views/ReportsView.vue'
import RecordsView     from '../views/RecordsView.vue'
import HealthSearchView from '../views/HealthSearchView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/',        component: HomeView },
    { path: '/upload',  component: UploadView },
    { path: '/reports', component: ReportsView },
    { path: '/records', component: RecordsView },
    { path: '/search',  component: HealthSearchView },
  ]
})

export default router
