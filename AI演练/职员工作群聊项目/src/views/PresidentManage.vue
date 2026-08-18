<template>
  <div class="page">
    <div class="page-header">
      <h2>总裁管理</h2>
      <el-button type="primary" :icon="Plus" @click="openDialog">授予管理权限</el-button>
    </div>

    <el-card shadow="never">
      <div class="desc">
        <el-alert type="info" :closable="false" show-icon>
          管理部门职员拥有员工管理、信息面板、禁言等管理功能。总裁可在此授予 / 撤销管理权限。
        </el-alert>
      </div>
      <el-table :data="managers" v-loading="loading" empty-text="暂无管理部门职员">
        <el-table-column prop="name" label="姓名" min-width="180" />
        <el-table-column label="角色" min-width="140">
          <template #default="{ row }">
            <el-tag :type="row.role === 'PRESIDENT' ? 'danger' : 'warning'" effect="light">
              {{ row.role === 'PRESIDENT' ? '总裁' : '管理部门职员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="所属部门" min-width="160">
          <template #default="{ row }">
            {{ departmentLabel(row.DEPARTMENT_ID) || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.role === 'MANAGER'"
              type="danger"
              link
              @click="revoke(row)"
            >
              撤销权限
            </el-button>
            <span v-else class="president-tag">总裁不可操作</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 授予管理权限弹窗 -->
    <el-dialog v-model="dialogVisible" title="授予管理权限" width="460px">
      <el-form label-width="90px">
        <el-form-item label="职员">
          <el-select v-model="selectedId" placeholder="请选择要提升的普通职员" filterable style="width: 100%">
            <el-option
              v-for="c in staffCandidates"
              :key="c.EMPLOYEE_ID"
              :label="c.name"
              :value="c.EMPLOYEE_ID"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="grant">确定授予</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { managerApi, chatApi } from '@/api'
import { departmentLabel } from '@/utils/labels'

const loading = ref(false)
const managers = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const selectedId = ref(null)
const contacts = ref([])

const staffCandidates = computed(() => contacts.value.filter((c) => c.role === 'STAFF'))

async function loadManagers() {
  loading.value = true
  try {
    managers.value = await managerApi.list()
  } catch (e) {
    ElMessage.error(e.message || '加载管理层名单失败')
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
  selectedId.value = null
  dialogVisible.value = true
}

async function grant() {
  if (!selectedId.value) {
    ElMessage.warning('请选择要提升的职员')
    return
  }
  submitting.value = true
  try {
    const res = await managerApi.grant(selectedId.value)
    ElMessage.success(res.message || '授予成功')
    dialogVisible.value = false
    loadManagers()
  } catch (e) {
    ElMessage.error(e.message || '授予失败')
  } finally {
    submitting.value = false
  }
}

async function revoke(row) {
  await ElMessageBox.confirm(
    `确定撤销 ${row.name} 的管理权限吗？撤销后将失去所有管理功能。`,
    '提示',
    { type: 'warning' }
  ).catch(() => Promise.reject())
  try {
    const res = await managerApi.revoke(row.EMPLOYEE_ID)
    ElMessage.success(res.message || '已撤销')
    loadManagers()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
}

onMounted(() => {
  loadManagers()
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

.desc {
  margin-bottom: 14px;
}

.president-tag {
  color: #94a3b8;
  font-size: 13px;
}
</style>
