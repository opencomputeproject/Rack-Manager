import http from './http'

let getChassisInfo = () => http('get', 'xyz/openbmc_project/inventory/system/chassis/motherboard/chassis')
let getBoardInfo = () => http('get', 'xyz/openbmc_project/inventory/system/chassis/motherboard/board')
let getProductInfo = () => http('get', 'xyz/openbmc_project/inventory/system/chassis/motherboard/product')

export let getFruInfo = () => {
  return Promise.all([
    getChassisInfo(),
    getBoardInfo(),
    getProductInfo()
  ])
}

export let getRmcFru = () => http('get', '/redfish/v1/Managers/rmc')
