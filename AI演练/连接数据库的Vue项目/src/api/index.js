import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

// 统一解包数据、统一处理错误
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.message || error.message || '请求失败，请稍后再试'
    return Promise.reject(new Error(message))
  }
)

/** 员工相关接口 */
export const employeeApi = {
  /** 组合条件查询 + 分页 */
  search(params) {
    return request.get('/employees/search', { params })
  },
  /** 查询所有员工（skip/limit 分页） */
  getAll(params) {
    return request.get('/employees', { params })
  },
  /** 根据 ID 查询单个员工 */
  getById(id) {
    return request.get(`/employees/${id}`)
  },
  /** 新增员工 */
  create(data) {
    return request.post('/employees', data)
  },
  /** 更新员工 */
  update(id, data) {
    return request.put(`/employees/${id}`, data)
  },
  /** 删除员工 */
  remove(id) {
    return request.delete(`/employees/${id}`)
  },
  /** 姓名模糊查找 */
  findByName(name) {
    return request.get(`/find/${encodeURIComponent(name)}`)
  }
}

/** 字典 / 统计相关接口 */
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

export default { employeeApi, dictionaryApi }
