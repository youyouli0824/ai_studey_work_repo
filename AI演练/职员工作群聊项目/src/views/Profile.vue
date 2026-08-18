<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左: 头像与身份 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="info-card">
          <div class="avatar-wrap">
            <el-avatar :size="96" :src="authState.user?.avatar || undefined" class="big-avatar">
              {{ (authState.user?.name || '?').charAt(0) }}
            </el-avatar>
            <div class="name">{{ authState.user?.name }}</div>
            <el-tag :type="roleTagType" effect="light" round>{{ roleLabel }}</el-tag>
          </div>

          <el-descriptions :column="1" class="profile-desc">
            <el-descriptions-item label="部门">
              {{ departmentLabel(authState.user?.DEPARTMENT_ID) || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="职位">
              {{ jobLabel(authState.user?.JOB_ID) || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="员工编号">
              {{ authState.user?.EMPLOYEE_ID }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="upload-avatar">
            <el-upload
              :show-file-list="false"
              accept="image/png,image/jpeg,image/gif,image/webp"
              :http-request="handleAvatarUpload"
            >
              <el-button type="primary" plain :icon="Picture" :loading="avatarLoading">
                上传头像
              </el-button>
            </el-upload>
            <div class="avatar-tip">支持 JPG / PNG / GIF / WebP，不超过 5MB</div>
          </div>
        </el-card>
      </el-col>

      <!-- 右: 基本信息 + 修改密码 -->
      <el-col :xs="24" :md="16">
        <el-card shadow="never" header="基本信息">
          <el-form
            ref="infoFormRef"
            :model="infoForm"
            :rules="infoRules"
            label-width="90px"
            class="form-card"
          >
            <el-form-item label="邮箱" prop="EMAIL">
              <el-input v-model="infoForm.EMAIL" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="联系电话" prop="PHONE_NUMBER">
              <el-input v-model="infoForm.PHONE_NUMBER" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="infoLoading" @click="saveInfo">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
          <el-alert type="info" :closable="false" show-icon class="info-alert">
            姓名（登录账号）、角色、部门由系统管理，不可自行修改。
          </el-alert>
        </el-card>

        <el-card shadow="never" header="修改密码" class="pwd-card">
          <el-form
            ref="pwdFormRef"
            :model="pwdForm"
            :rules="pwdRules"
            label-width="90px"
            class="form-card"
          >
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
              <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="请再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="pwdLoading" @click="changePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { profileApi, authApi } from '@/api'
import { authState, updateUser, ROLE_LABELS } from '@/store/auth'
import { departmentLabel, jobLabel } from '@/utils/labels'

const roleLabel = computed(() => ROLE_LABELS[authState.user?.role] || '')
const roleTagType = computed(() => {
  const map = { STAFF: 'info', MANAGER: 'warning', PRESIDENT: 'danger' }
  return map[authState.user?.role] || 'info'
})

/* ---------- 头像上传 ---------- */
const avatarLoading = ref(false)
async function handleAvatarUpload(options) {
  avatarLoading.value = true
  try {
    const data = await profileApi.uploadAvatar(options.file)
    updateUser({ ...authState.user, avatar: data.avatar })
    ElMessage.success('头像上传成功')
  } catch (e) {
    ElMessage.error(e.message || '头像上传失败')
  } finally {
    avatarLoading.value = false
  }
}

/* ---------- 基本信息 ---------- */
const infoFormRef = ref()
const infoLoading = ref(false)
const infoForm = reactive({
  EMAIL: authState.user?.EMAIL || '',
  PHONE_NUMBER: authState.user?.PHONE_NUMBER || ''
})
const infoRules = {
  EMAIL: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}

async function saveInfo() {
  const valid = await infoFormRef.value.validate().catch(() => false)
  if (!valid) return
  infoLoading.value = true
  try {
    const me = await profileApi.update({
      EMAIL: infoForm.EMAIL,
      PHONE_NUMBER: infoForm.PHONE_NUMBER
    })
    updateUser(me)
    ElMessage.success('个人信息已更新')
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    infoLoading.value = false
  }
}

/* ---------- 修改密码 ---------- */
const pwdFormRef = ref()
const pwdLoading = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm: ''
})
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度 6~50 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.new_password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

async function changePassword() {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  pwdLoading.value = true
  try {
    await profileApi.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
    // 让最新 user 信息从后端刷新一次
    const me = await authApi.me()
    updateUser(me)
  } catch (e) {
    ElMessage.error(e.message || '修改密码失败')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.avatar-wrap {
  text-align: center;
  margin-bottom: 18px;
}

.big-avatar {
  background: #2563eb;
  color: #fff;
  font-size: 36px;
  font-weight: 600;
}

.name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 12px 0 6px;
}

.profile-desc {
  margin-bottom: 14px;
}

.upload-avatar {
  text-align: center;
  padding-top: 14px;
  border-top: 1px dashed #e2e8f0;
}

.avatar-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.form-card {
  max-width: 460px;
}

.pwd-card {
  margin-top: 20px;
}

.info-alert {
  margin-top: 4px;
}
</style>
