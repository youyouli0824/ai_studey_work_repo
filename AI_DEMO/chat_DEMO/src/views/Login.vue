<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <el-icon :size="40" color="#fff"><OfficeBuilding /></el-icon>
        <h1>职员各部门工作交流系统</h1>
        <p>员工沟通 · 部门协作 · 高效办公</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入姓名或员工编号"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码（默认 123456）"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tip">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            账号为职员姓名（英文不区分大小写）或员工编号；初始密码为 123456
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { setAuth } from '@/store/auth'

const router = useRouter()
const route = useRoute()

// 便利功能: 支持 /login?username=xxx 预填账号(不绕过密码)
onMounted(() => {
  const u = route.query.username
  if (u) form.username = String(u)
})
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const data = await authApi.login({
      username: form.username.trim(),
      password: form.password
    })
    setAuth(data.token, data.user)
    ElMessage.success(`欢迎回来，${data.user.name}`)
    // 按角色进入各自首页
    router.push(data.user.role === 'STAFF' ? '/groups' : '/dashboard')
  } catch (e) {
    ElMessage.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a8a 0%, #111827 60%, #0f172a 100%);
}

.login-card {
  width: 400px;
  padding: 36px 36px 24px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
}

.login-brand {
  text-align: center;
  margin-bottom: 26px;
}

.login-brand .el-icon {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  border-radius: 14px;
  padding: 12px;
  box-sizing: content-box;
}

.login-brand h1 {
  font-size: 20px;
  margin: 14px 0 6px;
  color: #1e293b;
}

.login-brand p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.login-btn {
  width: 100%;
}

.login-tip {
  margin-top: 10px;
  text-align: left;
}
</style>
