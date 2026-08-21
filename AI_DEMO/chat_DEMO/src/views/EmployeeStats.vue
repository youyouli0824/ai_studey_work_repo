<template>
  <div class="page" v-loading="loading">
    <!-- 图表区 -->
    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">部门人数占比</span>
            <span class="card-sub">前六部门及汇总</span>
          </div>
          <ChartBox :option="deptPieOption" height="300px" />
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="app-card chart-card">
          <div class="card-head">
            <span class="card-title">职位人数 Top 8</span>
            <span class="card-sub">人数最多的 8 个职位</span>
          </div>
          <ChartBox :option="jobBarOption" height="300px" />
        </div>
      </el-col>
    </el-row>

    <!-- 部门统计明细 -->
    <div class="app-card table-card">
      <div class="card-head">
        <span class="card-title">部门统计明细</span>
        <span class="card-sub">共 {{ overview?.total_departments || 0 }} 个部门</span>
      </div>
      <el-table :data="deptRows" stripe style="width: 100%">
        <el-table-column label="部门名称" min-width="180">
          <template #default="{ row }">
            <span class="name-cell">{{ row.name }}</span>
            <span class="en-name">{{ row.department_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="部门ID" width="100" align="center" />
        <el-table-column label="员工数" width="220">
          <template #default="{ row }">
            <div class="count-cell">
              <el-progress
                :percentage="row.percent"
                :stroke-width="8"
                :color="BLUE"
                :show-text="false"
                class="count-bar"
              />
              <span class="count-text">{{ row.count }} 人</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="平均薪资" width="160">
          <template #default="{ row }">{{ formatSalary(row.avg_salary) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 职位统计明细 -->
    <div class="app-card table-card">
      <div class="card-head">
        <span class="card-title">职位统计明细</span>
        <span class="card-sub">共 {{ overview?.total_jobs || 0 }} 个职位</span>
      </div>
      <el-table :data="jobRows" stripe style="width: 100%">
        <el-table-column label="职位名称" min-width="180">
          <template #default="{ row }">
            <span class="name-cell">{{ row.name }}</span>
            <span class="en-name">{{ row.job_title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="job_id" label="职位ID" width="110" align="center" />
        <el-table-column label="员工数" width="220">
          <template #default="{ row }">
            <div class="count-cell">
              <el-progress
                :percentage="row.percent"
                :stroke-width="8"
                :color="ORANGE"
                :show-text="false"
                class="count-bar"
              />
              <span class="count-text">{{ row.count }} 人</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="职位薪资区间" min-width="200">
          <template #default="{ row }">
            <template v-if="row.min_salary !== null">
              ¥ {{ formatNumber(row.min_salary) }} ~ ¥ {{ formatNumber(row.max_salary) }}
            </template>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { dictionaryApi } from '@/api'
import ChartBox from '@/components/ChartBox.vue'
import { formatSalary, formatNumber } from '@/utils/format'
import { departmentLabel, jobLabel } from '@/utils/labels'

const loading = ref(true)
const overview = ref(null)
const jobs = ref([])

const BLUE = '#2a78d6'
const ORANGE = '#eb6834'
const CATEGORY_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']
const OTHER_COLOR = '#898781'
const AXIS_LABEL = '#52514e'
const GRID_LINE = '#e1e0d9'

const totalEmployees = computed(() => overview.value?.total_employees || 0)

/* ---------- 部门人数占比(环形图) ---------- */
const deptPieOption = computed(() => {
  const stats = overview.value?.department_stats || []
  const sorted = [...stats].sort((a, b) => b.count - a.count)
  const top = sorted.slice(0, 6)
  const restCount = sorted.slice(6).reduce((s, d) => s + d.count, 0)
  const items = top.map((d) => ({
    name: departmentLabel(d.department_id) || d.department_name,
    value: d.count
  }))
  if (restCount > 0) items.push({ name: '其他部门', value: restCount })
  return {
    tooltip: { trigger: 'item', formatter: '{b}<br/>{c} 人 · {d}%' },
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

/* ---------- 职位人数 Top 8(横向条形图) ---------- */
const jobBarOption = computed(() => {
  const stats = overview.value?.job_stats || []
  const sorted = [...stats].sort((a, b) => a.count - b.count).slice(-8)
  return {
    grid: { left: 130, right: 40, top: 10, bottom: 10 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = params[0]
        return `${p.name}<br/><b style="color:${ORANGE}">${p.value}</b> 人`
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
      data: sorted.map((j) => jobLabel(j.job_id) || j.job_title),
      axisLine: { lineStyle: { color: '#c3c2b7' } },
      axisTick: { show: false },
      axisLabel: { color: AXIS_LABEL, fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((j) => j.count),
        barWidth: 12,
        itemStyle: { color: ORANGE, borderRadius: [0, 6, 6, 0] },
        label: { show: true, position: 'right', color: AXIS_LABEL, fontSize: 11, formatter: '{c}' }
      }
    ]
  }
})

/* ---------- 明细表格数据 ---------- */
const deptRows = computed(() => {
  const stats = overview.value?.department_stats || []
  return [...stats]
    .sort((a, b) => b.count - a.count)
    .map((d) => ({
      ...d,
      name: departmentLabel(d.department_id) || d.department_name,
      percent: totalEmployees.value
        ? Math.round((d.count / totalEmployees.value) * 1000) / 10
        : 0
    }))
})

const jobRows = computed(() => {
  const stats = overview.value?.job_stats || []
  const jobMap = new Map(jobs.value.map((j) => [j.JOB_ID, j]))
  return [...stats]
    .sort((a, b) => b.count - a.count)
    .map((j) => {
      const meta = jobMap.get(j.job_id) || {}
      return {
        ...j,
        name: jobLabel(j.job_id) || j.job_title,
        min_salary: meta.MIN_SALARY ?? null,
        max_salary: meta.MAX_SALARY ?? null,
        percent: totalEmployees.value
          ? Math.round((j.count / totalEmployees.value) * 1000) / 10
          : 0
      }
    })
})

/* ---------- 加载数据 ---------- */
async function loadData() {
  loading.value = true
  try {
    const [ov, jobRes] = await Promise.all([
      dictionaryApi.getOverview(),
      dictionaryApi.getJobs()
    ])
    overview.value = ov
    jobs.value = jobRes
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
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

.name-cell {
  font-weight: 500;
  margin-right: 8px;
}

.en-name {
  font-size: 12px;
  color: var(--app-text-sub);
}

.count-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.count-bar {
  flex: 1;
}

.count-text {
  font-size: 13px;
  color: var(--app-text-main);
  min-width: 52px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.muted {
  color: var(--app-text-sub);
}
</style>
