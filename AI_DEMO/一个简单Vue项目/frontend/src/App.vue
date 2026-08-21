<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Reading, User, PriceTag, Refresh } from '@element-plus/icons-vue'

const books = ref([])
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')

// 卡片封面的渐变配色（循环使用）
const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
]

const fetchBooks = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/books')
    const data = await res.json()
    if (data.code === 200) {
      books.value = data.data
    } else {
      error.value = data.message || '加载图书失败'
    }
  } catch (e) {
    error.value = '无法连接服务器，请确认后端已启动（http://localhost:8000）'
  } finally {
    loading.value = false
  }
}

// 按标题或作者搜索
const filteredBooks = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return books.value
  return books.value.filter(
    (b) =>
      b.title.toLowerCase().includes(keyword) ||
      b.author.toLowerCase().includes(keyword)
  )
})

// 每本图书对应一个固定的渐变背景
const coverStyle = (book) => gradients[(book.id - 1) % gradients.length]
</script>

<template>
  <div class="page">
    <!-- 顶部横幅 -->
    <header class="hero">
      <div class="hero-inner">
        <h1 class="hero-title">📚 图书管理系统</h1>
        <p class="hero-subtitle">发现好书，探索知识的世界</p>

        <el-input
          v-model="searchKeyword"
          class="search-input"
          size="large"
          placeholder="搜索图书名称或作者..."
          :prefix-icon="Search"
          clearable
        />
      </div>
    </header>

    <main class="container">
      <!-- 工具栏：统计 + 刷新 -->
      <div class="toolbar">
        <div class="stats">
          <span class="stat-item">
            <el-icon><Reading /></el-icon>
            共 <b>{{ books.length }}</b> 本图书
          </span>
          <span v-if="searchKeyword.trim()" class="stat-item stat-muted">
            搜索到 <b>{{ filteredBooks.length }}</b> 本
          </span>
        </div>
        <el-button :icon="Refresh" @click="fetchBooks" circle title="刷新" />
      </div>

      <!-- 加载中骨架屏 -->
      <div v-if="loading" class="book-grid">
        <el-card v-for="n in 6" :key="n" class="book-card" shadow="hover">
          <el-skeleton animated :rows="4" />
        </el-card>
      </div>

      <!-- 加载失败 -->
      <el-result
        v-else-if="error"
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="fetchBooks">重新加载</el-button>
        </template>
      </el-result>

      <!-- 无搜索结果 -->
      <el-empty
        v-else-if="filteredBooks.length === 0"
        :description="searchKeyword.trim() ? `没有找到与「${searchKeyword}」相关的图书` : '暂无图书数据'"
      >
        <el-button v-if="searchKeyword.trim()" @click="searchKeyword = ''">
          清除搜索
        </el-button>
      </el-empty>

      <!-- 图书卡片网格 -->
      <div v-else class="book-grid">
        <el-card
          v-for="book in filteredBooks"
          :key="book.id"
          class="book-card"
          shadow="hover"
        >
          <!-- 封面占位区 -->
          <div class="cover" :style="{ background: coverStyle(book) }">
            <span class="cover-char">{{ book.title.charAt(0) }}</span>
            <span class="cover-deco cover-deco-1"></span>
            <span class="cover-deco cover-deco-2"></span>
          </div>

          <div class="book-body">
            <h3 class="book-title" :title="book.title">{{ book.title }}</h3>
            <p class="book-author">
              <el-icon><User /></el-icon>
              <span>{{ book.author }}</span>
            </p>
            <div class="book-footer">
              <span class="book-price">
                <el-icon><PriceTag /></el-icon>
                ¥{{ book.price }}
              </span>
              <el-tag size="small" effect="light" round>ID: {{ book.id }}</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </main>

    <footer class="footer">FastAPI + Vue 3 + Element Plus</footer>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f5f7fa 0%, #eef1f6 100%);
}

/* ===== 顶部横幅 ===== */
.hero {
  background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
  padding: 56px 24px 64px;
  color: #fff;
  text-align: center;
}
.hero-title {
  margin: 0 0 8px;
  font-size: 34px;
  letter-spacing: 2px;
}
.hero-subtitle {
  margin: 0 0 28px;
  font-size: 15px;
  opacity: 0.85;
}
.search-input {
  max-width: 520px;
  margin: 0 auto;
  border-radius: 24px;
}
.search-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 4px 20px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
}

/* ===== 主体 ===== */
.container {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 24px 48px;
  transform: translateY(-32px);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}
.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.stat-item b {
  color: #4e4376;
}
.stat-muted {
  color: #909399;
}

/* ===== 卡片网格 ===== */
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}
.book-card {
  border: none;
  border-radius: 14px;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.book-card:hover {
  transform: translateY(-6px);
}
.book-card :deep(.el-card__body) {
  padding: 0;
}

.cover {
  position: relative;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.cover-char {
  font-size: 64px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  z-index: 1;
}
.cover-deco {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}
.cover-deco-1 {
  width: 120px;
  height: 120px;
  top: -40px;
  right: -30px;
}
.cover-deco-2 {
  width: 80px;
  height: 80px;
  bottom: -30px;
  left: -20px;
}

.book-body {
  padding: 16px 18px 18px;
}
.book-title {
  margin: 0 0 8px;
  font-size: 16px;
  line-height: 1.4;
  color: #303133;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 45px;
}
.book-author {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 14px;
  font-size: 13px;
  color: #909399;
}
.book-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.book-price {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 19px;
  font-weight: 700;
  color: #e54d42;
}

/* ===== 页脚 ===== */
.footer {
  text-align: center;
  padding: 18px;
  font-size: 13px;
  color: #909399;
}
</style>
