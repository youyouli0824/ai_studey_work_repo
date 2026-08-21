<template>
  <div class="page">
    <div class="page-header">
      <h2>禁言管理</h2>
      <el-button type="primary" :icon="Microphone" @click="openDialog">禁言职员</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="mutes" v-loading="loading" empty-text="当前没有禁言中的职员">
        <el-table-column prop="employee_name" label="被禁言职员" min-width="160" />
        <el-table-column label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag v-if="isPermanent(row)" type="danger" effect="dark">永久禁言</el-tag>
            <el-tag v-else type="warning">限时禁言</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="剩余 / 截止时间" min-width="160">
          <template #default="{ row }">
            {{ row.mute_until ? `至 ${row.mute_until}` : '永久' }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="禁言原因" min-width="160" show-overflow-tooltip />
        <el-table-column prop="operator_name" label="操作人" min-width="140" />
        <el-table-column prop="created_at" label="禁言时间" min-width="160" />
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link @click="removeMute(row)">解除禁言</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增禁言弹窗 -->
    <el-dialog v-model="dialogVisible" title="禁言职员" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="职员" prop="employee_id">
          <el-select v-model="form.employee_id" placeholder="请选择要禁言的职员" filterable style="width: 100%">
            <el-option
              v-for="c in muteCandidates"
              :key="c.EMPLOYEE_ID"
              :label="c.name"
              :value="c.EMPLOYEE_ID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="禁言时长" prop="mute_minutes">
          <el-radio-group v-model="durationType">
            <el-radio label="forever">永久</el-radio>
            <el-radio label="timed">指定时长</el-radio>
          </el-radio-group>
          <el-input-number
            v-if="durationType === 'timed'"
            v-model="form.mute_minutes"
            :min="1"
            :max="43200"
            placeholder="分钟"
          />
          <span v-if="durationType === 'timed'" class="unit">分钟</span>
        </el-form-item>
        <el-form-item label="原因" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="2"
            maxlength="200"
            show-word-limit
            placeholder="请输入禁言原因（必填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitMute">确定禁言</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Microphone } from '@element-plus/icons-vue'
import { muteApi, chatApi } from '@/api'
import { hasRole } from '@/store/auth'

const loading = ref(false)
const mutes = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const contacts = ref([])
const durationType = ref('forever')

const formRef = ref()
const form = reactive({
  employee_id: null,
  reason: '',
  mute_minutes: 60
})

const rules = {
  employee_id: [{ required: true, message: '请选择要禁言的职员', trigger: 'change' }],
  reason: [{ required: true, message: '请输入禁言原因', trigger: 'blur' }],
  mute_minutes: [
    {
      validator: (r, v, cb) => {
        if (durationType.value === 'timed' && (!v || v < 1)) cb(new Error('请输入有效时长'))
        else cb()
      },
      trigger: 'change'
    }
  ]
}

/** 可禁言对象: 管理部门仅可禁言普通职员,总裁还可禁言管理部门职员(不含总裁与本人) */
const muteCandidates = computed(() => {
  const allowed = hasRole('PRESIDENT') ? ['STAFF', 'MANAGER'] : ['STAFF']
  return contacts.value.filter((c) => allowed.includes(c.role))
})

function isPermanent(row) {
  return !row.mute_until
}

async function loadMutes() {
  loading.value = true
  try {
    mutes.value = await muteApi.list()
  } catch (e) {
    ElMessage.error(e.message || '加载禁言列表失败')
  } finally {
    loading.value = false
  }
}

async function loadContacts() {
  try {
    contacts.value = await chatApi.contacts()
  } catch (_) {
    /* 忽略 */
  }
}

function openDialog() {
  form.employee_id = null
  form.reason = ''
  form.mute_minutes = 60
  durationType.value = 'forever'
  dialogVisible.value = true
}

async function submitMute() {
  await formRef.value.validate().catch(() => Promise.reject())
  submitting.value = true
  try {
    const payload = {
      employee_id: form.employee_id,
      reason: form.reason,
      mute_minutes: durationType.value === 'timed' ? form.mute_minutes : null
    }
    const res = await muteApi.create(payload)
    ElMessage.success(res.message || '禁言成功')
    dialogVisible.value = false
    loadMutes()
  } catch (e) {
    ElMessage.error(e.message || '禁言失败')
  } finally {
    submitting.value = false
  }
}

async function removeMute(row) {
  await ElMessageBox.confirm(`确定解除 ${row.employee_name} 的禁言吗？`, '提示', {
    type: 'warning'
  }).catch(() => Promise.reject())
  try {
    await muteApi.remove(row.mute_id)
    ElMessage.success('已解除禁言')
    loadMutes()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
}

onMounted(() => {
  loadMutes()
  loadContacts()
})
</script>

<style scoped>
.page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h2 {
  font-size: 18px;
  color: #1e293b;
  margin: 0;
}

.unit {
  margin-left: 8px;
  color: #94a3b8;
}
</style>
