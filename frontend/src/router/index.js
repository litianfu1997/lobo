import { createRouter, createWebHistory } from 'vue-router'
import ListView from '../views/ListView.vue'
import DetailView from '../views/DetailView.vue'
import SubmitView from '../views/SubmitView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: ListView },
    { path: '/analysis/:id', component: DetailView },
    { path: '/submit', component: SubmitView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
