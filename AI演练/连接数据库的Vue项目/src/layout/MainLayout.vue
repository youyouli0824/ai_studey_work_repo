<template>
  <el-container class="layout">
    <!-- 左侧导航 -->
    <el-aside width="220px" class="layout-aside">
      <div class="brand">
        <el-icon :size="26" color="#fff"><OfficeBuilding /></el-icon>
        <div class="brand-text">
          <div class="brand-title">职工信息管理系统</div>
          <div class="brand-sub">Employee System</div>
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
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/employees">
          <el-icon><User /></el-icon>
          <span>员工管理</span>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><PieChart /></el-icon>
          <span>分类统计</span>
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
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="primary" effect="plain" round>数据库已连接</el-tag>
          <span class="header-date">{{ today }}</span>
        </div>
      </el-header>

      <el-main class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => route.path)

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})
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
  white-space: nowrap;
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
  gap: 14px;
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
