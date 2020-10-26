<!--
 * @Author: your name
 * @Date: 2020-02-29 18:14:51
 * @LastEditTime: 2020-03-01 21:22:47
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /bmcweb/home/mengyaohui/work/openbmc/openbmc/build/workspace/sources/phosphor-webui/src/views/psu/psu.vue
 -->
<template>
  <view-content message="psu" @refresh="refresh">
    <a-table :columns="columns" :dataSource="data" size="small" rowKey='name'>
      <span slot="status" slot-scope="status">
          <a-icon v-if="status == 'enable'" type="check-circle" style="color: green;font-size: 1.2em;"/>
          <a-icon v-else type="close-circle" style="color: orange;font-size: 1.2em;"/>
      </span>
    </a-table>
    <a-row style="margin-bottom: 20px;">
      <a-col :span="2">
        <a-icon type="check-circle" style="color: green;font-size: 1.2em;margin-right: 10px"/>{{$t('message.psu.enable')}}
      </a-col>
      <a-col :span="2">
        <a-icon type="close-circle" style="color: grey;font-size: 1.2em;margin-right: 10px"/>{{$t('message.psu.disable')}}
      </a-col>
    </a-row>
  </view-content >
</template>

<script>
//import reqwest from 'reqwest';
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo } from '@/service/api'

export default {
  name: 'psu',
  data () {
    return {
      columns: [
        { title: 'No.', dataIndex: 'id', width: '5%'  },
        { title: this.$t('message.psu.status'), dataIndex: 'status', width: '10%' , align: 'center', scopedSlots: { customRender: 'status' }},
        { title: this.$t('message.psu.vendor'), dataIndex: 'vendor', width: '10%' },
        { title: this.$t('message.psu.model'),  dataIndex: 'model',  width: '20%' },
        { title: this.$t('message.psu.sn'),     dataIndex: 'sn',     width: '20%' },
        { title: this.$t('message.psu.pn'),     dataIndex: 'pn',     width: '20%' },
        { title: this.$t('message.psu.fw'),     dataIndex: 'fw' },
      ],
      node: undefined,
      nodeList: [],
      chassisReqs: {},
      currentPsuInfo: {},
      data: []
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
          this.chassisReqs[name] = `/redfish/v1/Chassis/${name}/Power`
        })
        //this.node = this.nodeList[0]
        let resPower = await http('get',`/redfish/v1/Chassis/chassis1/Power`)
        resPower.data.PowerSupplies.forEach((power, index) => {
          this.data.push(this.parseData(power, index))
        })
        //this.currentPsuInfo = this.parseData(resPower.data.PowerSupplies)
        //this.data.push(this.currentPsuInfo)
        
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    // chassis变化回调函数
    async onChassisChange (val) {
      this.currentPsuInfo = {}
      // this.setRefreshFlag({ refreshFlag: true })

      try {
        //this.node = val
        //let resPower = await http('get', this.chassisReqs[this.node])
        //this.currentPsuInfo = this.parseData(resPower.data.PowerSupplies)
        //this.data.push(this.currentPsuInfo)

        let resPower = await http('get',`/redfish/v1/Chassis/chassis1/Power`)
        console.log('resPower:', resPower)
        resPower.data.PowerSupplies.forEach((power, index) => {
          console.log('power:', power)
          this.data.push(this.parseData(power, index))
        })
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    parseData (content, index) {
      return {
        id:     index,
        status: content.Status.State,
        vendor: content.Manufacturer,
        model:  content.Model,
        sn:     content.SerialNumber,
        pn:     content.PartNumber,
        fw:     content.FirmwareVersion
      }
    }
  },
  components: {
    ViewContent
  }
}
</script>
<style lang="less" scoped>
.item-row {
  margin-bottom: 15px;
  /* border-bottom: 1px solid grey; */
}
</style>
