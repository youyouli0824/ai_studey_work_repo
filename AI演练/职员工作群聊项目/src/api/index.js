import axios from 'axios'
import { authState, clearAuth } from '@/store/auth'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

// 自动携带登录 token
request.interceptors.request.use((config) => {
  if (authState.token) {
    config.headers.Authorization = `Bearer ${authState.token}`
  }
  return config
})

// 统一解包数据、统一处理错误; 401 时清空凭证并跳转登录页
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const message =
      error.response?.data?.message || error.message || '请求失败，请稍后再试'
    if (status === 401) {
      clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(new Error(message))
  }
)

/** 员工相关接口(管理层) */
export const employeeApi = {
  search(params) {
    return request.get('/employees/search', { params })
  },
  getAll(params) {
    return request.get('/employees', { params })
  },
  getById(id) {
    return request.get(`/employees/${id}`)
  },
  create(data) {
    return request.post('/employees', data)
  },
  update(id, data) {
    return request.put(`/employees/${id}`, data)
  },
  remove(id) {
    return request.delete(`/employees/${id}`)
  },
  findByName(name) {
    return request.get(`/find/${encodeURIComponent(name)}`)
  }
}

/** 字典 / 统计相关接口(管理层) */
export const dictionaryApi = {
  getDepartments() {
    return request.get('/departments')
  },
  getJobs() {
    return request.get('/jobs')
  },
  getOverview() {
    return request.get('/overview')
  }
}

/** 登录 / 认证 */
export const authApi = {
  login(data) {
    return request.post('/auth/login', data)
  },
  logout() {
    return request.post('/auth/logout')
  },
  me() {
    return request.get('/auth/me')
  }
}

/** 个人中心 */
export const profileApi = {
  update(data) {
    return request.put('/me', data)
  },
  changePassword(data) {
    return request.put('/me/password', data)
  },
  uploadAvatar(file) {
    const fd = new FormData()
    fd.append('file', file)
    return request.post('/me/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

/** 群聊 / 私聊 */
export const chatApi = {
  myGroups() {
    return request.get('/groups/my')
  },
  deptMessages(params) {
    return request.get('/groups/dept/messages', { params })
  },
  sendDept(content) {
    return request.post('/groups/dept/messages', { content })
  },
  allMessages(params) {
    return request.get('/groups/all/messages', { params })
  },
  sendAll(content) {
    return request.post('/groups/all/messages', { content })
  },
  contacts() {
    return request.get('/contacts')
  },
  privateMessages(params) {
    return request.get('/private/messages', { params })
  },
  sendPrivate(data) {
    return request.post('/private/messages', data)
  },
  /** 私聊会话列表(含未读数,按最近消息置顶) */
  conversations() {
    return request.get('/private/conversations')
  },
  /** 标记与某职员的私聊已读 */
  markRead(contactId) {
    return request.post('/private/read', { contact_id: contactId })
  },
  /** 未读私聊总数(侧边栏红点) */
  unreadTotal() {
    return request.get('/private/unread-total')
  }
}

/** 禁言管理(管理层) */
export const muteApi = {
  list() {
    return request.get('/mutes')
  },
  create(data) {
    return request.post('/mutes', data)
  },
  remove(id) {
    return request.delete(`/mutes/${id}`)
  }
}

/** 总裁管理 */
export const managerApi = {
  list() {
    return request.get('/managers')
  },
  grant(employeeId) {
    return request.post('/managers', { employee_id: employeeId })
  },
  revoke(employeeId) {
    return request.delete(`/managers/${employeeId}`)
  }
}

export default { employeeApi, dictionaryApi, authApi, profileApi, chatApi, muteApi, managerApi }
