<template>
  <el-container class="layout">
    <!-- 左侧导航 -->
    <el-aside width="220px" class="layout-aside">
      <div class="brand">
        <el-icon :size="26" color="#fff"><OfficeBuilding /></el-icon>
        <div class="brand-text">
          <div class="brand-title">职员各部门<br />工作交流系统</div>
          <div class="brand-sub">Staff Communication</div>
        </div>
      </div>

      <el-menu
        class="side-menu"
        :default-active="activeMenu"
        router
        background-color="transparent"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
      >
        <el-menu-item v-for="item in visibleItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
          <span v-if="item.path === '/private' && unreadState.total > 0" class="menu-dot">
            {{ unreadState.total > 99 ? '99+' : unreadState.total }}
          </span>
        </el-menu-item>
      </el-menu>

      <div class="aside-footer">
        <span>MySQL · FastAPI · Vue3</span>
      </div>
    </el-aside>

    <!-- 主区域 -->
    <el-container class="layout-main">
      <el-header height="60px" class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: userHome }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="user?.avatar || undefined" class="user-avatar">
                {{ (user?.name || '?').charAt(0) }}
              </el-avatar>
              <span class="user-name">{{ user?.name }}</span>
              <el-tag size="small" :type="roleTagType" effect="plain" round>
                {{ roleLabel }}
              </el-tag>
              <el-icon class="user-caret"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile" :icon="UserFilled">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" :icon="SwitchButton" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <span class="header-date">{{ today }}</span>
        </div>
      </el-header>

      <el-main class="layout-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { authApi, chatApi } from '@/api'
import { authState, clearAuth, ROLE_LABELS } from '@/store/auth'
import { unreadState } from '@/store/unread'

const route = useRoute()
const router = useRouter()

const user = computed(() => authState.user)
const roleLabel = computed(() => ROLE_LABELS[user.value?.role] || user.value?.role || '')
const roleTagType = computed(() => {
  const map = { STAFF: 'info', MANAGER: 'warning', PRESIDENT: 'danger' }
  return map[user.value?.role] || 'info'
})
const userHome = computed(() => (user.value?.role === 'STAFF' ? '/groups' : '/dashboard'))

/** 菜单配置: roles 为空表示所有角色可见 */
const menuItems = [
  { path: '/dashboard', icon: 'Odometer', label: '信息面板', roles: ['MANAGER', 'PRESIDENT'] },
  { path: '/employees', icon: 'User', label: '员工管理', roles: ['MANAGER', 'PRESIDENT'] },
  { path: '/stats', icon: 'PieChart', label: '分类统计', roles: ['MANAGER', 'PRESIDENT'] },
  { path: '/profile', icon: 'UserFilled', label: '个人中心', roles: null },
  { path: '/groups', icon: 'ChatDotRound', label: '群聊', roles: null },
  { path: '/private', icon: 'ChatLineRound', label: '私聊', roles: null },
  { path: '/mutes', icon: 'Microphone', label: '禁言管理', roles: ['MANAGER', 'PRESIDENT'] },
  { path: '/president', icon: 'Star', label: '总裁管理', roles: ['PRESIDENT'] }
]

const visibleItems = computed(() =>
  menuItems.filter((m) => !m.roles || m.roles.includes(user.value?.role))
)

const activeMenu = computed(() => route.path)

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

function handleCommand(command) {
  if (command === 'logout') handleLogout()
  else if (command === 'profile') router.push('/profile')
}

/* ---------- 未读私聊轮询(侧边栏红点) ---------- */
let unreadTimer = null
async function refreshUnread() {
  try {
    const data = await chatApi.unreadTotal()
    unreadState.total = data.total
  } catch (_) {
    /* 静默,下一轮重试 */
  }
}

onMounted(() => {
  refreshUnread()
  unreadTimer = setInterval(refreshUnread, 5000)
})

onBeforeUnmount(() => {
  if (unreadTimer) clearInterval(unreadTimer)
})

async function handleLogout() {
  try {
    await authApi.logout()
  } catch (_) {
    /* token 失效等场景忽略 */
  }
  clearAuth()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100%;
}

/* ========== 侧边栏 ========== */
.layout-aside {
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #1e3a8a 0%, #111827 100%);
  color: #fff;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  line-height: 1.35;
  white-space: nowrap; /* 配合模板中的 <br> 手动换行,避免在宽度内自行折行 */
}

.brand-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 2px;
  letter-spacing: 0.5px;
}

.side-menu {
  flex: 1;
  border-right: none;
  padding-top: 10px;
}

.side-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 10px;
  border-radius: 10px;
  font-size: 14px;
}

.side-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

.side-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.14) !important;
  font-weight: 600;
  box-shadow: inset 3px 0 0 #60a5fa;
}

/* 「私聊」菜单未读红点 */
.menu-dot {
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  padding: 0 5px;
  margin-left: auto;
  border-radius: 9px;
  background: #f56c6c;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  text-align: center;
}

.aside-footer {
  padding: 14px 20px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
}

/* ========== 顶部与内容 ========== */
.layout-main {
  min-width: 0;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  position: relative;
  z-index: 5;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.user-avatar {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}

.user-caret {
  color: #94a3b8;
  font-size: 12px;
}

.header-date {
  font-size: 13px;
  color: var(--app-text-sub);
}

.layout-content {
  padding: 0;
  overflow-y: auto;
  background: var(--app-bg);
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.22s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
