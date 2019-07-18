import CommonMsg from './common'
import SigninMsg from './signin'
import SysInfoMsg from './systemInfo'
import FruMsg from './fru'
import FanCtrlMsg from './fanCtrl'
import FwUpdateMsg from './fwUpdate'
import RedfishMsg from './redfish'
import SensorMsg from './sensor'
import NodeMsg from './node'
import PsuMsg from './psu'

export default {
  message: {
    common: CommonMsg,
    signin: SigninMsg,
    sysInfo: SysInfoMsg,
    fru: FruMsg,
    fanCtrl: FanCtrlMsg,
    fwUpdate: FwUpdateMsg,
    redfish: RedfishMsg,
    sensor: SensorMsg,
    node: NodeMsg,
    psu: PsuMsg
  }
}
