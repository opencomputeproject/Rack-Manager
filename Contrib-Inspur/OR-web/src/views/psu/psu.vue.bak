<template>
  <view-content message="psu" @refresh="refresh">
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
    <a-row class="item-row">
      <a-col :span="3">{{$t('message.psu.vendor')}}</a-col>
      <a-col :span="10">{{currentPsuInfo.vendor}}</a-col>
    </a-row>
    <a-row class="item-row">
      <a-col :span="3">{{$t('message.psu.model')}}</a-col>
      <a-col :span="10">{{currentPsuInfo.model}}</a-col>
    </a-row>
    <a-row class="item-row">
      <a-col :span="3">{{$t('message.psu.sn')}}</a-col>
      <a-col :span="10">{{currentPsuInfo.sn}}</a-col>
    </a-row>
    <a-row class="item-row">
      <a-col :span="3">{{$t('message.psu.pn')}}</a-col>
      <a-col :span="10">{{currentPsuInfo.pn}}</a-col>
    </a-row>
    <a-row class="item-row">
      <a-col :span="3">{{$t('message.psu.fw')}}</a-col>
      <a-col :span="10">{{currentPsuInfo.fw}}</a-col>
    </a-row>
  </view-content >
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo } from '@/service/api'

export default {
  name: 'psu',
  data () {
    return {
      node: undefined,
      nodeList: [],
      chassisReqs: {},
      currentPsuInfo: {}
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
        this.node = this.nodeList[0]
        let resPower = await http('get', this.chassisReqs[this.node])
        this.currentPsuInfo = this.parseData(resPower.data.PowerSupplies)
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
        this.node = val
        let resPower = await http('get', this.chassisReqs[this.node])
        this.currentPsuInfo = this.parseData(resPower.data.PowerSupplies)
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    parseData (content) {
      return {
        vendor: content[0].Manufacturer,
        model: content[0].Model,
        sn: content[0].SerialNumber,
        pn: content[0].PartNumber,
        fw: content[0].FirmwareVersion
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
