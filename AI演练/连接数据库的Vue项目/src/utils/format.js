/**
 * 通用格式化工具
 */

/** 薪资：千分位 + ¥ 前缀，空值显示 "-" */
export function formatSalary(value) {
  if (value === null || value === undefined || value === '') return '-'
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return `¥ ${num.toLocaleString('zh-CN')}`
}

/** 提成比例：小数转百分比（0.25 → 25%） */
export function formatCommission(value) {
  if (value === null || value === undefined || value === '') return '-'
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return `${(num * 100).toFixed(0)}%`
}

/** 空值统一显示 "-" */
export function formatEmpty(value) {
  if (value === null || value === undefined || value === '') return '-'
  return String(value)
}

/** 数字格式化为中文千分位（图表 tooltip 等场景） */
export function formatNumber(value) {
  if (value === null || value === undefined || value === '') return '-'
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return num.toLocaleString('zh-CN')
}
