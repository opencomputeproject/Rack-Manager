import Vue from 'vue'
import Router from 'vue-router'

import LoginRoute from './views/login/route'
import InformationRoute from './views/info/route'
import FanCtrRoute from './views/fan/route'
import RedfishRoute from './views/redfish/route'
import SensorRoute from './views/sensor/route'
import FwUpdateRoute from './views/fwUpdate/route'
import NodeInfoRoute from './views/node/route'
import PsuRoute from './views/psu/route'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/', redirect: '/login' },

    ...LoginRoute,
    ...InformationRoute,
    ...FanCtrRoute,
    ...RedfishRoute,
    ...SensorRoute,
    ...FwUpdateRoute,
    ...NodeInfoRoute,
    ...PsuRoute
  ]
})
