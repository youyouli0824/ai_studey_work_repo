import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layout/MainLayout.vue'
import { isLoggedIn, authState } from '@/store/auth'

/** 各角色默认首页: 管理层进仪表盘, 普通职员进群聊 */
function userHome() {
  const role = authState.user?.role
  return role === 'STAFF' ? '/groups' : '/dashboard'
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '信息面板', icon: 'Odometer', roles: ['MANAGER', 'PRESIDENT'] }
      },
      {
        path: 'employees',
        name: 'EmployeeList',
        component: () => import('@/views/EmployeeList.vue'),
        meta: { title: '员工管理', icon: 'User', roles: ['MANAGER', 'PRESIDENT'] }
      },
      {
        path: 'stats',
        name: 'EmployeeStats',
        component: () => import('@/views/EmployeeStats.vue'),
        meta: { title: '分类统计', icon: 'PieChart', roles: ['MANAGER', 'PRESIDENT'] }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', icon: 'UserFilled' }
      },
      {
        path: 'groups',
        name: 'GroupChat',
        component: () => import('@/views/GroupChat.vue'),
        meta: { title: '群聊', icon: 'ChatDotRound' }
      },
      {
        path: 'private',
        name: 'PrivateChat',
        component: () => import('@/views/PrivateChat.vue'),
        meta: { title: '私聊', icon: 'ChatLineRound' }
      },
      {
        path: 'mutes',
        name: 'MuteManagement',
        component: () => import('@/views/MuteManagement.vue'),
        meta: { title: '禁言管理', icon: 'Microphone', roles: ['MANAGER', 'PRESIDENT'] }
      },
      {
        path: 'president',
        name: 'PresidentManage',
        component: () => import('@/views/PresidentManage.vue'),
        meta: { title: '总裁管理', icon: 'Star', roles: ['PRESIDENT'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const SYSTEM_NAME = '职员各部门工作交流系统'

router.beforeEach((to) => {
  const authed = isLoggedIn()

  // 已登录访问登录页 -> 回到各角色首页
  if (to.path === '/login') {
    return authed ? userHome() : true
  }
  // 未登录访问受保护页面 -> 登录页
  if (!authed) {
    return { path: '/login' }
  }
  // 根路径 -> 各角色首页
  if (to.path === '/') {
    return userHome()
  }
  // 角色权限校验
  if (to.meta.roles && !to.meta.roles.includes(authState.user.role)) {
    return userHome()
  }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} · ${SYSTEM_NAME}`
    : SYSTEM_NAME
})

export default router
