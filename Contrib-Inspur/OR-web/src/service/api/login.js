import http from './http'

export let LOGIN = (data) => http('post', '/redfish/v1/SessionService/Sessions', data)
