<template>
  <view-content message="node" @refresh="refresh">

    <a-table :columns="columns" :dataSource="data" size="small" rowKey='name'
    >
      <span slot="action" slot-scope="record">
        <a-button >{{$t('message.common.power_on')}}</a-button>
        <a-button style="margin-left: 10px">{{$t('message.common.power_off')}}</a-button>
        <a-button style="margin-left: 10px">{{$t('message.common.reboot')}}</a-button>
      </span>
    </a-table>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo } from '@/service/api'

export default {
  name: 'nodeInfo',
  data () {
    return {
      columns: [
        { title: this.$t('message.node.thead_name'), dataIndex: 'name', width: '10%' },
        { title: this.$t('message.node.thead_status'), dataIndex: 'status', align: 'center' },
        { title: this.$t('message.node.thead_power'), dataIndex: 'power', align: 'center' },
        { title: this.$t('message.node.thead_ip'), dataIndex: 'ip', align: 'center' },
        { title: this.$t('message.node.thead_action'), align: 'center', width: '30%', scopedSlots: { customRender: 'action' } }
      ],
      node: undefined,
      nodeList: [],
      currentChassisInfo: {},
      parsedData: {},
      data: []
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag']),

    async refresh () {
      this.nodeList = []
      this.data = []
      try {
        let resChassis = await getChassisInfo()
        resChassis.data.Members.forEach((item) => {
          let tmps = item['@odata.id'].split('/')
          let name = tmps[tmps.length - 1]
          this.nodeList.push(name)
        })

        this.nodeList.forEach(async (node, index) => {
          let resCurrentChassis = await http('get', `/redfish/v1/Chassis/${node}`)

          this.data.push(this.parseData(resCurrentChassis.data))
        })
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    parseData (content) {
      return {
        name: content.Name,
        power: content.PowerState,
        status: content.Status.Health,
        ip: content.IpAddr,
        led: content.IndicatorLED
      }
    },

    // chassis变化回调函数
    async onChassisChange (val) {
      try {
        let resCurrentChassis = await http('get', `/redfish/v1/Chassis/${val}`)
        this.parsedData = this.parseData(resCurrentChassis.data)
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }
    }
  },
  components: {
    ViewContent
  }
}
</script>
