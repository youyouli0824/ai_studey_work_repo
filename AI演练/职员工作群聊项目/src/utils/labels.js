/**
 * 中文映射字典：
 * - 字段表头
 * - 部门 ID → 中文名（映射缺失时前端回退英文名，不丢信息）
 * - 职位 ID → 中文名
 */

/** 字段名 → 中文表头 */
export const FIELD_LABELS = {
  EMPLOYEE_ID: '员工编号',
  FIRST_NAME: '名',
  LAST_NAME: '姓',
  FULL_NAME: '姓名',
  EMAIL: '邮箱',
  PHONE_NUMBER: '联系电话',
  HIRE_DATE: '入职日期',
  JOB_ID: '职位',
  SALARY: '薪资（元）',
  COMMISSION_PCT: '提成比例',
  MANAGER_ID: '直属上级',
  DEPARTMENT_ID: '所属部门'
}

/** 部门 ID → 中文名 */
export const DEPARTMENTS_CN = {
  10: '行政管理',
  20: '市场营销',
  30: '采购部',
  40: '人力资源部',
  50: '物流运输部',
  60: '信息技术部',
  70: '公共关系部',
  80: '销售部',
  90: '高级管理层',
  100: '财务部',
  110: '会计部',
  120: '资金管理部',
  130: '企业税务部',
  140: '信贷控制部',
  150: '股东服务部',
  160: '福利管理部',
  170: '生产制造部',
  180: '建筑施工部',
  190: '合同管理部',
  200: '运营部',
  210: '信息技术支持部',
  220: '网络运营中心',
  230: 'IT 服务台',
  240: '政务销售部',
  250: '零售销售部',
  260: '招聘部',
  270: '薪酬管理部'
}

/** 职位 ID → 中文名 */
export const JOBS_CN = {
  AC_ACCOUNT: '会计师',
  AC_MGR: '会计经理',
  AD_ASST: '行政助理',
  AD_PRES: '总裁',
  AD_VP: '行政副总裁',
  FI_ACCOUNT: '财务人员',
  FI_MGR: '财务经理',
  HR_REP: '人力资源专员',
  IT_PROG: '程序员',
  MK_MAN: '市场经理',
  MK_REP: '市场专员',
  PR_REP: '公关专员',
  PU_CLERK: '采购文员',
  PU_MAN: '采购经理',
  SA_MAN: '销售经理',
  SA_REP: '销售代表',
  SH_CLERK: '物流文员',
  ST_CLERK: '库存文员',
  ST_MAN: '库存经理'
}

/** 部门 ID → 中文名（无映射返回空串，由调用方回退英文名） */
export function departmentLabel(id) {
  if (id === null || id === undefined || id === '') return ''
  return DEPARTMENTS_CN[Number(id)] || ''
}

/** 职位 ID → 中文名（无映射返回空串，由调用方回退英文名） */
export function jobLabel(jobId) {
  if (!jobId) return ''
  return JOBS_CN[jobId] || ''
}

/** 按字段名取中文表头 */
export function fieldLabel(field) {
  return FIELD_LABELS[field] || field
}
