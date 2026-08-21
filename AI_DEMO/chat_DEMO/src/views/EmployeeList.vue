<template>
  <div class="page">
    <!-- 查询条件栏 -->
    <div class="app-card search-card">
      <el-form :inline="true" :model="filters" class="search-form">
        <el-form-item label="姓名/邮箱关键字">
          <el-input
            v-model="filters.keyword"
            placeholder="姓名或邮箱"
            clearable
            style="width: 170px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select
            v-model="filters.departmentId"
            placeholder="全部部门"
            clearable
            style="width: 170px"
          >
            <el-option
              v-for="d in departments"
              :key="d.DEPARTMENT_ID"
              :label="deptOptionLabel(d)"
              :value="d.DEPARTMENT_ID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位">
          <el-select
            v-model="filters.jobId"
            placeholder="全部职位"
            clearable
            style="width: 170px"
          >
            <el-option
              v-for="j in jobs"
              :key="j.JOB_ID"
              :label="jobOptionLabel(j)"
              :value="j.JOB_ID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资范围">
          <el-input-number
            v-model="filters.minSalary"
            :min="0"
            :max="100000"
            :step="500"
            :precision="0"
            controls-position="right"
            placeholder="最低"
            style="width: 130px"
          />
          <span class="range-sep">—</span>
          <el-input-number
            v-model="filters.maxSalary"
            :min="0"
            :max="100000"
            :step="500"
            :precision="0"
            controls-position="right"
            placeholder="最高"
            style="width: 130px"
          />
        </el-form-item>
        <el-form-item label="入职日期">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon class="btn-icon"><Search /></el-icon>查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon class="btn-icon"><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 列表 -->
    <div class="app-card table-card">
      <div class="table-toolbar">
        <div class="table-title">
          <span class="title-main">员工列表</span>
          <el-tag type="primary" effect="plain" round size="small">
            共 {{ pager.total }} 名员工
          </el-tag>
        </div>
        <div class="table-actions">
          <el-button
            v-if="selection.length > 0"
            type="danger"
            plain
            @click="handleBatchDelete"
          >
            <el-icon class="btn-icon"><Delete /></el-icon>批量删除（{{ selection.length }}）
          </el-button>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon class="btn-icon"><Plus /></el-icon>新增员工
          </el-button>
        </div>
      </div>

      <el-table
        :data="tableData"
        v-loading="tableLoading"
        stripe
        border
        style="width: 100%"
        @selection-change="selection = $event"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="EMPLOYEE_ID" label="员工编号" width="92" sortable />
        <el-table-column label="姓名" min-width="140">
          <template #default="{ row }">
            <span class="name-cell">{{ row.FIRST_NAME }} {{ row.LAST_NAME }}</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="roleTagType(row.ROLE)" effect="light">
              {{ roleLabel(row.ROLE) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="EMAIL" label="邮箱" min-width="140" />
        <el-table-column prop="PHONE_NUMBER" label="联系电话" min-width="130" />
        <el-table-column prop="HIRE_DATE" label="入职日期" width="112" sortable />
        <el-table-column label="所属部门" min-width="120">
          <template #default="{ row }">
            <el-tag size="small" type="primary" effect="light">
              {{ deptName(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="职位" min-width="120">
          <template #default="{ row }">
            <el-tag size="small" type="warning" effect="light">
              {{ jobName(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="薪资" width="120" sortable>
          <template #default="{ row }">{{ formatSalary(row.SALARY) }}</template>
        </el-table-column>
        <el-table-column label="提成" width="86">
          <template #default="{ row }">{{ formatCommission(row.COMMISSION_PCT) }}</template>
        </el-table-column>
        <el-table-column label="直属上级" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.MANAGER_ID">{{ row.MANAGER_ID }}</span>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pager.page"
          v-model:page-size="pager.pageSize"
          :total="pager.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadList"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑员工' : '新增员工'"
      width="640px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="96px"
        status-icon
      >
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="名" prop="FIRST_NAME">
              <el-input v-model="form.FIRST_NAME" placeholder="请输入名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓" prop="LAST_NAME">
              <el-input v-model="form.LAST_NAME" placeholder="请输入姓" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="EMAIL">
              <el-input v-model="form.EMAIL" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="PHONE_NUMBER">
              <el-input v-model="form.PHONE_NUMBER" placeholder="如 515.123.4567" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="HIRE_DATE">
              <el-date-picker
                v-model="form.HIRE_DATE"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位" prop="JOB_ID">
              <el-select v-model="form.JOB_ID" placeholder="请选择职位" style="width: 100%">
                <el-option
                  v-for="j in jobs"
                  :key="j.JOB_ID"
                  :label="jobOptionLabel(j)"
                  :value="j.JOB_ID"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="薪资（元）" prop="SALARY">
              <el-input-number
                v-model="form.SALARY"
                :min="0"
                :max="1000000"
                :step="100"
                :precision="2"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="提成比例" prop="commissionPercent">
              <el-input-number
                v-model="form.commissionPercent"
                :min="0"
                :max="100"
                :step="5"
                :precision="0"
                controls-position="right"
                style="width: 100%"
              >
                <template #suffix>%</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门" prop="DEPARTMENT_ID">
              <el-select
                v-model="form.DEPARTMENT_ID"
                placeholder="请选择部门（可空）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="d in departments"
                  :key="d.DEPARTMENT_ID"
                  :label="deptOptionLabel(d)"
                  :value="d.DEPARTMENT_ID"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="直属上级" prop="MANAGER_ID">
              <el-input-number
                v-model="form.MANAGER_ID"
                :min="0"
                :step="1"
                :precision="0"
                controls-position="right"
                placeholder="上级员工编号（可空）"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { employeeApi, dictionaryApi } from '@/api'
import { formatSalary, formatCommission, formatEmpty } from '@/utils/format'
import { departmentLabel, jobLabel } from '@/utils/labels'

/* ---------- 字典数据 ---------- */
const departments = ref([])
const jobs = ref([])

function deptOptionLabel(d) {
  const cn = departmentLabel(d.DEPARTMENT_ID)
  return cn ? `${cn}（${d.DEPARTMENT_NAME}）` : d.DEPARTMENT_NAME
}
function jobOptionLabel(j) {
  const cn = jobLabel(j.JOB_ID)
  return cn ? `${cn}（${j.JOB_TITLE}）` : j.JOB_TITLE
}
function deptName(row) {
  return departmentLabel(row.DEPARTMENT_ID) || formatEmpty(row.DEPARTMENT_ID)
}
function jobName(row) {
  return jobLabel(row.JOB_ID) || formatEmpty(row.JOB_ID)
}
const ROLE_LABELS = { STAFF: '普通职员', MANAGER: '管理部门职员', PRESIDENT: '总裁' }
function roleLabel(role) {
  return ROLE_LABELS[role] || role || '—'
}
function roleTagType(role) {
  return { STAFF: 'info', MANAGER: 'warning', PRESIDENT: 'danger' }[role] || 'info'
}

/* ---------- 查询条件与分页 ---------- */
const filters = reactive({
  keyword: '',
  departmentId: null,
  jobId: null,
  minSalary: null,
  maxSalary: null,
  dateRange: null
})

const pager = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])
const tableLoading = ref(false)
const selection = ref([])

function buildParams() {
  const params = { page: pager.page, page_size: pager.pageSize }
  if (filters.keyword) params.keyword = filters.keyword.trim()
  if (filters.departmentId !== null && filters.departmentId !== '') {
    params.department_id = filters.departmentId
  }
  if (filters.jobId) params.job_id = filters.jobId
  if (filters.minSalary !== null && filters.minSalary !== '') {
    params.min_salary = filters.minSalary
  }
  if (filters.maxSalary !== null && filters.maxSalary !== '') {
    params.max_salary = filters.maxSalary
  }
  if (filters.dateRange && filters.dateRange.length === 2) {
    params.hire_date_start = filters.dateRange[0]
    params.hire_date_end = filters.dateRange[1]
  }
  return params
}

async function loadList() {
  tableLoading.value = true
  try {
    const res = await employeeApi.search(buildParams())
    tableData.value = res.items
    pager.total = res.total
  } catch (err) {
    ElMessage.error(err.message || '加载失败')
  } finally {
    tableLoading.value = false
  }
}

function handleSearch() {
  pager.page = 1
  loadList()
}

function handleReset() {
  filters.keyword = ''
  filters.departmentId = null
  filters.jobId = null
  filters.minSalary = null
  filters.maxSalary = null
  filters.dateRange = null
  handleSearch()
}

function handleSizeChange() {
  pager.page = 1
  loadList()
}

/* ---------- 新增 / 编辑 ---------- */
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const emptyForm = {
  FIRST_NAME: '',
  LAST_NAME: '',
  EMAIL: '',
  PHONE_NUMBER: '',
  HIRE_DATE: null,
  JOB_ID: '',
  SALARY: null,
  commissionPercent: null,
  MANAGER_ID: null,
  DEPARTMENT_ID: null
}
const form = reactive({ ...emptyForm })

const formRules = {
  FIRST_NAME: [{ required: true, message: '请输入名', trigger: 'blur' }],
  LAST_NAME: [{ required: true, message: '请输入姓', trigger: 'blur' }],
  EMAIL: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  PHONE_NUMBER: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  HIRE_DATE: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  JOB_ID: [{ required: true, message: '请选择职位', trigger: 'change' }],
  SALARY: [
    { required: true, message: '请输入薪资', trigger: 'blur' },
    {
      validator: (_, val, cb) => {
        if (val !== null && val !== undefined && Number(val) <= 0) {
          cb(new Error('薪资必须大于 0'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ],
  commissionPercent: [
    {
      validator: (_, val, cb) => {
        if (val !== null && val !== undefined && (val < 0 || val > 100)) {
          cb(new Error('提成比例需在 0-100 之间'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ]
}

function resetForm() {
  Object.assign(form, emptyForm)
}

const editingId = ref(null)

function openCreateDialog() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editingId.value = row.EMPLOYEE_ID
  resetForm()
  Object.assign(form, {
    FIRST_NAME: row.FIRST_NAME,
    LAST_NAME: row.LAST_NAME,
    EMAIL: row.EMAIL,
    PHONE_NUMBER: row.PHONE_NUMBER,
    HIRE_DATE: row.HIRE_DATE,
    JOB_ID: row.JOB_ID,
    SALARY: row.SALARY,
    commissionPercent:
      row.COMMISSION_PCT === null || row.COMMISSION_PCT === undefined
        ? null
        : Math.round(Number(row.COMMISSION_PCT) * 100),
    MANAGER_ID: row.MANAGER_ID,
    DEPARTMENT_ID: row.DEPARTMENT_ID
  })
  dialogVisible.value = true
}

function buildPayload() {
  const payload = {
    FIRST_NAME: form.FIRST_NAME.trim(),
    LAST_NAME: form.LAST_NAME.trim(),
    EMAIL: form.EMAIL.trim(),
    PHONE_NUMBER: form.PHONE_NUMBER.trim(),
    HIRE_DATE: form.HIRE_DATE,
    JOB_ID: form.JOB_ID,
    SALARY: form.SALARY,
    COMMISSION_PCT:
      form.commissionPercent === null || form.commissionPercent === undefined
        ? null
        : Number(form.commissionPercent) / 100,
    MANAGER_ID: form.MANAGER_ID,
    DEPARTMENT_ID: form.DEPARTMENT_ID
  }
  // 去掉空字段,交给后端(新增时后端校验必填)
  Object.keys(payload).forEach((k) => {
    if (payload[k] === null || payload[k] === undefined || payload[k] === '') {
      delete payload[k]
    }
  })
  return payload
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const payload = buildPayload()
    if (isEdit.value) {
      await employeeApi.update(editingId.value, payload)
      ElMessage.success('员工信息已更新')
    } else {
      await employeeApi.create(payload)
      ElMessage.success('员工新增成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (err) {
    ElMessage.error(err.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

/* ---------- 删除 ---------- */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工「${row.FIRST_NAME} ${row.LAST_NAME}」（编号 ${row.EMPLOYEE_ID}）吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await employeeApi.remove(row.EMPLOYEE_ID)
    ElMessage.success('删除成功')
    // 若当前页被删空则回退一页
    if (tableData.value.length === 1 && pager.page > 1) {
      pager.page -= 1
    }
    loadList()
  } catch (err) {
    if (err === 'cancel' || err === 'close') return
    ElMessage.error(err.message || '删除失败')
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selection.value.length} 名员工吗？删除后不可恢复。`,
      '批量删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await Promise.all(selection.value.map((r) => employeeApi.remove(r.EMPLOYEE_ID)))
    ElMessage.success(`已删除 ${selection.value.length} 名员工`)
    if (tableData.value.length === selection.value.length && pager.page > 1) {
      pager.page -= 1
    }
    loadList()
  } catch (err) {
    if (err === 'cancel' || err === 'close') return
    ElMessage.error(err.message || '删除失败')
  }
}

/* ---------- 初始化 ---------- */
async function loadDictionaries() {
  const [deptRes, jobRes] = await Promise.all([
    dictionaryApi.getDepartments(),
    dictionaryApi.getJobs()
  ])
  departments.value = deptRes
  jobs.value = jobRes
}

onMounted(async () => {
  await loadDictionaries()
  await loadList()
})
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 12px;
  margin-right: 12px;
}

.range-sep {
  margin: 0 6px;
  color: var(--app-text-sub);
}

.table-card {
  padding-bottom: 12px;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-main {
  font-size: 15px;
  font-weight: 600;
}

.btn-icon {
  margin-right: 4px;
}

.name-cell {
  font-weight: 500;
}

.muted {
  color: var(--app-text-sub);
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
