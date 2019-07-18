import http from './http'

// 获取系统信息
export let getSystemInfo = () => http('get', '/redfish/v1/Systems')

// 获取一个system信息
// export let getSingleSystemInfo = (name) => http('get', `/redfish/v1/Systems/${name}`)

// 获取但前system所有内存信息
let getMemInfo = (name) => http('get', `/redfish/v1/Systems/${name}/Memory`)

// 获取当前system所有处理器信息
let getCpuInfo = (name) => http('get', `/redfish/v1/Systems/${name}/Processors`)

export let getSingleSystemInfo = (name) => {
  return Promise.all([
    getMemInfo(name),
    getCpuInfo(name)
  ])
}

// 获取单个cpu或内存信息
export let getSingleData = (url) => http('get', url)
