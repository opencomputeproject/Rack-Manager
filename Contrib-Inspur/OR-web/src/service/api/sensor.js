import http from './http'

export let getChassisInfo = () => http('get', '/redfish/v1/Chassis')
