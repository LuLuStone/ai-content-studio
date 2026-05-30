import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/podcast',
      name: 'podcast',
      component: () => import('../views/PodcastView.vue'),
    },
    {
      path: '/podcast/:id',
      name: 'podcast-detail',
      component: () => import('../views/PodcastDetailView.vue'),
    },
    {
      path: '/audiobook',
      name: 'audiobook',
      component: () => import('../views/AudiobookView.vue'),
    },
    {
      path: '/audiobook/:id',
      name: 'audiobook-detail',
      component: () => import('../views/AudiobookDetailView.vue'),
    },
    {
      path: '/video',
      name: 'video',
      component: () => import('../views/VideoView.vue'),
    },
    {
      path: '/video/:id',
      name: 'video-detail',
      component: () => import('../views/VideoDetailView.vue'),
    },
    {
      path: '/image',
      name: 'image',
      component: () => import('../views/ImageView.vue'),
    },
    {
      path: '/creations',
      name: 'creations',
      component: () => import('../views/CreationListView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
    {
      path: '/voices',
      name: 'voices',
      component: () => import('../views/VoiceManageView.vue'),
    },
  ],
})

export default router
