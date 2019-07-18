import http from './http'
import axios from 'axios'

// 获取固件版本
export let getFwVersion = () => http('get', '/xyz/openbmc_project/software/enumerate')

// 从本地上传镜像文件
export let uploadImageFile = (data) => {
  return axios({
    url: '/upload/image/lsnImage',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'application/octet-stream'
    },
    withCredentials: true
  })
}

// non-ubi固件升级： 更新前的重启操作
export let prepareForUpdate = () => http('post', '/org/openbmc/control/flash/bmc/action/prepareForUpdate', { data: [] })

// non-ubi固件升级： 从tftp服务器下载镜像
export let downloadFromTftp = (data) => http('post', '/org/openbmc/control/flash/bmc/action/updateViaTftp', data)

// non-ubi固件升级：获取更新进度和状态
export let getStatusAndProgress = () => http('post', '/org/openbmc/control/flash/bmc/action/GetUpdateProgress', { data: [] })

// non-ubi固件升级：query the progress of the download and image verification
export let getFlashStatusNonUbi = () => http('get', '/org/openbmc/control/flash/bmc')

// non-ubi固件升级：执行刷新
export let applyImage = () => http('post', '/org/openbmc/control/flash/bmc/action/Apply', { data: [] })

// non-ubi固件升级：刷新成功后重启BMC
export let rebootBmc = () => http('post', '/org/openbmc/control/bmc0/action/warmReset', { data: [] })
