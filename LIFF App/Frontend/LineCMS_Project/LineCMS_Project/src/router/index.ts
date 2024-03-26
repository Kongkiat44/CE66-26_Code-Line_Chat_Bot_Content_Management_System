import { createRouter, createWebHistory } from 'vue-router'


// const groupName = ref("")

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/selectgroup'
    },
    {
      path: '/selectgroup',
      name: 'selectgroup',
      component: () => import('../views/HomeView.vue'),
      meta: {
        title: 'เลือกกลุ่ม'
      }
    },
    {
      path: '/selectmenu',
      name: 'selectmenu',
      component: () => import('../views/SelectMenu.vue'),
      meta: {
        title: 'เลือกเมนู',
      }
    },
    {
      path: '/clustersearch',
      name: 'clustersearch',
      component: () => import('../views/ClusterSearchView.vue'),
      meta: {
        title: 'ค้นหารูปภาพด้วยใบหน้า'
      }
    },
    {
      path: '/graphcreate',
      name: 'graphcreate',
      component: () => import('../views/GraphCreate.vue'),
      meta: {
        title: 'สร้างกราฟความสัมพันธ์'
      }
    },
    {
      path: '/graphcreatestatus',
      name: 'graphcreatestatus',
      component: () => import('../views/GraphCreateStatus.vue'),
      meta: {
        title: 'สร้างกราฟความสัมพันธ์'
      }
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: () => import('../views/Dashboard.vue'),
      meta: {
        title: 'แกลเลอรี่'
      }
    },
    {
      path: '/imageresult',
      name: 'imageresult',
      component: () => import('../views/ImageResult.vue'),
      meta: {
        title: 'ค้นหารูปด้วยใบหน้า'
      }
    },
    {
      path: '/managefiles',
      name: 'managefiles',
      component: () => import('../views/ManageFiles.vue'),
      meta: {
        title: 'จัดการรูปภาพและไฟล์'
      }
    },
    {
      path: '/redirectpage',
      name: 'redirectpage',
      component: () => import('../views/RedirectPageView.vue'),
      meta: {
        title: 'เกี่ยวกับ'
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  next()
  document.title = getTitle(to.meta.title)
})

function getTitle(title: string | undefined): string {
  if (title) {
    return title
  }
  return 'Default Title'
}

export default router

