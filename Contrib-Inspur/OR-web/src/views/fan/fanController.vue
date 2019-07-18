<template>
  <view-content message="fanCtrl" @refresh="refresh">
    <a-row style="margin-bottom: 20px">
      <a-form>
        <a-col :span="24">
          <a-form-item :label="$t('message.common.select_node')" :labelCol="{ span: 3 }" :wrapperCol="{ span: 4 }">
            <a-select v-model="node" @change="onChassisChange">
              <a-select-option v-for="(item, index) in nodeList" :key="index" :value="item">{{'node ' + index}}</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-form>
    </a-row>
    <a-table :columns="columns" :dataSource="currentFanInfo" rowKey='id' size="small">
      <span slot="action" slot-scope="record">
        <a-button-group>
          <a-button >25%</a-button>
          <a-button >50%</a-button>
          <a-button >75%</a-button>
          <a-button >100%</a-button>
        </a-button-group>
      </span>
    </a-table>
    <a-row style="margin-bottom: 20px;">
      <a-col :span="2">
        <a-icon type="check-circle" style="color: green;font-size: 1.2em;margin-right: 10px"/>在位
      </a-col>
      <a-col :span="2">
        <a-icon type="close-circle" style="color: grey;font-size: 1.2em;margin-right: 10px"/>不在位
      </a-col>
    </a-row>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo } from '@/service/api'

export default {
  name: 'fanController',
  data () {
    return {
      node: undefined,
      nodeList: [],
      chassisReqs: {},
      currentFanInfo: [],
      columns: [
        { title: 'No.', dataIndex: 'id' },
        { title: this.$t('message.fanCtrl.thead_name'), dataIndex: 'name', align: 'center' },
        { title: this.$t('message.fanCtrl.thead_status'), dataIndex: 'health', align: 'center', scopedSlots: { customRender: 'status' } },
        { title: this.$t('message.fanCtrl.thead_rpm'), dataIndex: 'rpm', align: 'center' },
        { title: this.$t('message.fanCtrl.thead_action'), align: 'center', scopedSlots: { customRender: 'action' } }
      ]
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag']),
    async refresh () {
      this.nodeList = []
      this.chassisReqs = {}
      try {
        let resChassis = await getChassisInfo()
        resChassis.data.Members.forEach((item) => {
          let tmps = item['@odata.id'].split('/')
          let name = tmps[tmps.length - 1]
          this.nodeList.push(name)
          this.chassisReqs[name] = `/redfish/v1/Chassis/${name}/Thermal`
        })
        this.node = this.nodeList[0]
        let resThermal = await http('get', this.chassisReqs[this.node])
        this.parseData(resThermal.data.Fans)
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    // chassis变化回调函数
    async onChassisChange (val) {
      this.currentFanInfo = []
      // this.setRefreshFlag({ refreshFlag: true })

      try {
        this.node = val
        let resThermal = await http('get', this.chassisReqs[this.node])
        // console.log(resThermal.data.Fans)
        this.parseData(resThermal.data.Fans)
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    parseData (content) {
      content.forEach((fan) => {
        this.currentFanInfo.push({
          id: fan['@odata.id'].split('/').pop(),
          name: fan.Name,
          rpm: fan.Reading,
          health: fan.Status.Health
        })
      })
    },

    setRpm (id, duty) {
      console.log(id + ', ' + duty)
    }
  },
  components: {
    ViewContent
  }
}
</script>

<style scoped>

</style>
