import http from './http'

export let getRedfish = (path) => http('get', path)
