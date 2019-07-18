import axios from 'axios'

// 创建axios的一个实例
let http = axios.create({
  timeout: 10000
})

// 请求拦截器
http.interceptors.request.use(function (config) {
  if (config.url !== '/redfish/v1/SessionService/Sessions') {
    config.headers['x-auth-token'] = localStorage.getItem('token')
  }
  // console.log(config.headers)
  return config
}, function (error) {
  return Promise.reject(error)
})

// 响应拦截器
http.interceptors.response.use(function (response) {
  if (response.headers['x-auth-token']) {
    localStorage.setItem('token', response.headers['x-auth-token'])
  }

  return response
}, function (error) {
  return Promise.reject(error)
})

export default function (method, url, data = null) {
  method = method.toLowerCase()
  if (method === 'post') {
    return http.post(url, data)
  } else if (method === 'get') {
    return http.get(url, {
      params: data
    })
  } else if (method === 'delete') {
    return http.delete(url, {
      params: data
    })
  } else if (method === 'put') {
    return http.put(url, data)
  } else {
    console.error('未知的method' + method)
    return false
  }
}
