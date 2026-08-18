<template>
  <div class="page" v-loading="loading">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :xs="12" :sm="8" :md="4" v-for="kpi in kpis" :key="kpi.label">
        <div class="app-card kpi-card">
          <div class="kpi-icon" :style="{ color: kpi.color, background: kpi.bg }">
            <el-icon :size="22"><component :is="kpi.icon" /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value">{{ kpi.value }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">各部门人数分布</span>
            <span class="card-sub">按部门统计在职员工数</span>
          </div>
          <ChartBox :option="deptCountOption" height="300px" />
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">各部门平均薪资</span>
            <span class="card-sub">各部门人均月薪（元）</span>
          </div>
          <ChartBox :option="deptSalaryOption" height="300px" />
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">各职位人数分布</span>
            <span class="card-sub">前五职位占比及汇总</span>
          </div>
          <ChartBox :option="jobPieOption" height="300px" />
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">入职人数趋势</span>
            <span class="card-sub">1987–2000 年历年入职人数</span>
          </div>
          <ChartBox :option="yearTrendOption" height="300px" />
        </div>
      </el-col>
    </el-row>

    <!-- 最近入职员工 -->
    <div class="app-card table-card">
      <div class="card-head">
        <span class="card-title">最近入职员工</span>
        <el-button text type="primary" @click="$router.push('/employees')">
          查看全部员工 →
        </el-button>
      </div>
      <el-table :data="recentEmployees" stripe style="width: 100%">
        <el-table-column prop="EMPLOYEE_ID" label="员工编号" width="90" />
        <el-table-column label="姓名" min-width="150">
          <template #default="{ row }">
            {{ row.FIRST_NAME }} {{ row.LAST_NAME }}
          </template>
        </el-table-column>
        <el-table-column label="部门" min-width="130">
          <template #default="{ row }">
            <el-tag size="small" type="primary" effect="light">
              {{ deptName(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="职位" min-width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info" effect="light">
              {{ jobName(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="HIRE_DATE" label="入职日期" width="120" />
        <el-table-column label="薪资" width="130">
          <template #default="{ row }">{{ formatSalary(row.SALARY) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { dictionaryApi, employeeApi } from '@/api'
import ChartBox from '@/components/ChartBox.vue'
import { formatSalary, formatNumber } from '@/utils/format'
import { departmentLabel, jobLabel } from '@/utils/labels'

const loading = ref(true)
const overview = ref(null)
const recentEmployees = ref([])

/* ---------- 图表配色(来自 dataviz 已验证色板) ---------- */
const BLUE = '#2a78d6'
const ORANGE = '#eb6834'
const CATEGORY_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']
const OTHER_COLOR = '#898781'
const AXIS_LABEL = '#52514e'
const GRID_LINE = '#e1e0d9'

/* ---------- 统计卡片 ---------- */
const kpis = computed(() => {
  const o = overview.value
  if (!o) return []
  return [
    { label: '员工总数', value: o.total_employees, icon: 'User', color: '#2a78d6', bg: 'rgba(42,120,214,.12)' },
    { label: '部门总数', value: o.total_departments, icon: 'OfficeBuilding', color: '#1baf7a', bg: 'rgba(27,175,122,.12)' },
    { label: '职位总数', value: o.total_jobs, icon: 'Briefcase', color: '#eb6834', bg: 'rgba(235,104,52,.12)' },
    { label: '平均薪资', value: formatSalary(o.avg_salary), icon: 'Money', color: '#4a3aa7', bg: 'rgba(74,58,167,.12)' },
    { label: '最高薪资', value: formatSalary(o.max_salary), icon: 'TrendCharts', color: '#008300', bg: 'rgba(0,131,0,.12)' },
    { label: '最低薪资', value: formatSalary(o.min_salary), icon: 'Bottom', color: '#e87ba4', bg: 'rgba(232,123,164,.12)' }
  ]
})

/* ---------- 部门名 / 职位名(中文优先,回退英文) ---------- */
function deptName(row) {
  const cn = departmentLabel(row.DEPARTMENT_ID)
  return cn || row.DEPARTMENT_NAME || formatNumber(row.DEPARTMENT_ID)
}
function jobName(row) {
  const cn = jobLabel(row.JOB_ID)
  return cn || row.JOB_TITLE || row.JOB_ID
}

/* ---------- 各部门人数分布(水平条形图) ---------- */
const deptCountOption = computed(() => {
  const stats = overview.value?.department_stats || []
  const sorted = [...stats].sort((a, b) => a.count - b.count)
  return {
    grid: { left: 110, right: 40, top: 10, bottom: 10 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/><b style="color:${BLUE}">${p.value}</b> 人`
      }
    },
    xAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 },
      splitLine: { lineStyle: { color: GRID_LINE } }
    },
    yAxis: {
      type: 'category',
      data: sorted.map((d) => departmentLabel(d.department_id) || d.department_name),
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisTick: { show: false },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((d) => d.count),
        barWidth: 12,
        itemStyle: { color: BLUE, borderRadius: [0, 6, 6, 0] },
        label: { show: true, position: 'right', color: AXIS_LABEL, fontSize: 11, formatter: '{c}' }
      }
    ]
  }
})

/* ---------- 各部门平均薪资(水平条形图,橙色=第二顺序语境) ---------- */
const deptSalaryOption = computed(() => {
  const stats = overview.value?.department_stats || []
  const sorted = [...stats].sort((a, b) => a.avg_salary - b.avg_salary)
  return {
    grid: { left: 110, right: 40, top: 10, bottom: 10 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/><b style="color:${ORANGE}">¥ ${formatNumber(p.value)}</b>`
      }
    },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 },
      splitLine: { lineStyle: { color: GRID_LINE } }
    },
    yAxis: {
      type: 'category',
      data: sorted.map((d) => departmentLabel(d.department_id) || d.department_name),
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisTick: { show: false },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((d) => d.avg_salary),
        barWidth: 12,
        itemStyle: { color: ORANGE, borderRadius: [0, 6, 6, 0] },
        label: { show: true, position: 'right', color: AXIS_LABEL, fontSize: 11, formatter: '{c}' }
      }
    ]
  }
})

/* ---------- 各职位人数分布(环形图:前5 + 其他) ---------- */
const jobPieOption = computed(() => {
  const stats = overview.value?.job_stats || []
  const sorted = [...stats].sort((a, b) => b.count - a.count)
  const top = sorted.slice(0, 5)
  const rest = sorted.slice(5)
  const restCount = rest.reduce((s, j) => s + j.count, 0)
  const items = top.map((j, i) => ({
    name: jobLabel(j.job_id) || j.job_title,
    value: j.count
  }))
  if (restCount > 0) {
    items.push({ name: '其他职位', value: restCount })
  }
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>{c} 人 · {d}%'
    },
    legend: {
      bottom: 0,
      textStyle: { color: AXIS_LABEL, fontSize: 11 },
      icon: 'circle',
      itemWidth: 9,
      itemHeight: 9
    },
    color: [...CATEGORY_COLORS, OTHER_COLOR].slice(0, items.length),
    series: [
      {
        type: 'pie',
        radius: ['48%', '72%'],
        center: ['50%', '46%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}人', color: AXIS_LABEL, fontSize: 11, lineHeight: 16 },
        labelLine: { length: 8, length2: 6 },
        emphasis: {
          label: { fontSize: 12, fontWeight: 600 },
          itemStyle: { shadowBlur: 12, shadowColor: 'rgba(0,0,0,.18)' }
        },
        data: items
      }
    ]
  }
})

/* ---------- 入职年份趋势(面积图,单序列) ---------- */
const yearTrendOption = computed(() => {
  const dist = overview.value?.hire_year_distribution || []
  return {
    grid: { left: 40, right: 20, top: 24, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        return `${p.axisValue} 年<br/><b style="color:${BLUE}">${p.value}</b> 人`
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dist.map((d) => d.year),
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 },
      splitLine: { lineStyle: { color: GRID_LINE } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        data: dist.map((d) => d.count),
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { color: BLUE, width: 2.5 },
        itemStyle: { color: BLUE },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(42,120,214,.28)' },
              { offset: 1, color: 'rgba(42,120,214,.02)' }
            ]
          }
        }
      }
    ]
  }
})

/* ---------- 加载数据 ---------- */
async function loadData() {
  loading.value = true
  try {
    const [ov, list] = await Promise.all([
      dictionaryApi.getOverview(),
      employeeApi.getAll({ skip: 0, limit: 1000 })
    ])
    overview.value = ov
    // 按员工编号倒序取最近入职的 8 人
    recentEmployees.value = [...list]
      .sort((a, b) => Number(b.EMPLOYEE_ID) - Number(a.EMPLOYEE_ID))
      .slice(0, 8)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.kpi-row {
  margin-bottom: 16px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 16px;
  height: 100%;
}

.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-label {
  font-size: 12px;
  color: var(--app-text-sub);
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-main);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.chart-card,
.table-card {
  margin-bottom: 16px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-main);
}

.card-sub {
  font-size: 12px;
  color: var(--app-text-sub);
}

.table-card {
  padding-bottom: 8px;
}
</style>
