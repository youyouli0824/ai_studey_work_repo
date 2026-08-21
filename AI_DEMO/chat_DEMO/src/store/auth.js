/**
 * 全局登录状态(无第三方状态库,用响应式对象 + localStorage 持久化)
 */
import { reactive } from 'vue'

const TOKEN_KEY = 'staff_chat_token'
const USER_KEY = 'staff_chat_user'

export const authState = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: JSON.parse(localStorage.getItem(USER_KEY) || 'null')
})

/** 是否已登录 */
export const isLoggedIn = () => Boolean(authState.token && authState.user)

/** 登录成功写入凭证 */
export function setAuth(token, user) {
  authState.token = token
  authState.user = user
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/** 更新当前用户信息(修改个人信息/头像后同步) */
export function updateUser(user) {
  authState.user = user
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/** 退出登录清空凭证 */
export function clearAuth() {
  authState.token = ''
  authState.user = null
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/** 角色中文名 */
export const ROLE_LABELS = {
  STAFF: '普通职员',
  MANAGER: '管理部门职员',
  PRESIDENT: '总裁'
}

/** 判断当前用户是否具备某角色(可传多个,满足其一即可) */
export function hasRole(...roles) {
  const u = authState.user
  return Boolean(u && roles.includes(u.role))
}
