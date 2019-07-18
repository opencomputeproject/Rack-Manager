<template>
  <view-content message="fru" @refresh="refresh">
    <a-tabs tabPosition="left">
      <a-tab-pane tab="Rack" key="rack">
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.name')}}</a-col>
          <a-col :span="10">{{rackFruInfo.name}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.model')}}</a-col>
          <a-col :span="10">{{rackFruInfo.model}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.vendor')}}</a-col>
          <a-col :span="10">{{rackFruInfo.vendor}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.fw_version')}}</a-col>
          <a-col :span="10">{{rackFruInfo.fwVersion}}</a-col>
        </a-row>
      </a-tab-pane>
      <a-tab-pane :tab="$t('message.fru.node')" key="node">
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
          <a-col :span="3">{{$t('message.fru.name')}}</a-col>
          <a-col :span="10">{{parsedData.name}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.type')}}</a-col>
          <a-col :span="10">{{parsedData.type}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.vendor')}}</a-col>
          <a-col :span="10">{{parsedData.vendor}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">{{$t('message.fru.model')}}</a-col>
          <a-col :span="10">{{parsedData.model}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">PN:</a-col>
          <a-col :span="10">{{parsedData.pn}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">SN:</a-col>
          <a-col :span="10">{{parsedData.sn}}</a-col>
        </a-row>
        <a-row class="item-row">
          <a-col :span="3">SKU:</a-col>
          <a-col :span="10">{{parsedData.sku}}</a-col>
        </a-row>
      </a-tab-pane>
    </a-tabs>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo, getRmcFru } from '@/service/api'

export default {
  name: 'fru',
  data () {
    return {
      node: undefined,
      nodeList: [],
      chassisReqs: {},
      currentChassisInfo: {},
      parsedData: {},
      rackFruInfo: {}
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag']),
    async refresh () {
      this.nodeList = []
      this.chassisReqs = {}
      try {
        let resRack = await getRmcFru()
        this.rackFruInfo = this.parseRackData(resRack.data)
        let resChassis = await getChassisInfo()
        resChassis.data.Members.forEach((item) => {
          let tmps = item['@odata.id'].split('/')
          let name = tmps[tmps.length - 1]
          this.nodeList.push(name)
        })
        this.node = this.nodeList[0]
        this.chassisReq = `/redfish/v1/Chassis/${this.node}`
        let resCurrentChassis = await http('get', this.chassisReq)
        this.parsedData = this.parseData(resCurrentChassis.data)
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    parseData (content) {
      return {
        name: content.Name,
        type: content.ChassisType,
        vendor: content.Manufacturer,
        model: content.Model,
        pn: content.PartNumber,
        sn: content.SerialNumber,
        sku: content.SKU
      }
    },

    parseRackData (content) {
      return {
        name: content.Name,
        model: content.Model,
        vendor: 'Inspur',
        fwVersion: content.FirmwareVersion
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
<style scoped lang="less">
.item-row {
  margin-bottom: 15px;
  /* border-bottom: 1px solid grey; */
}

.content-label, label {
  color: #666;
  font-weight: 700;
  font-size: 1em;
  margin-bottom: 0;
}

.courier-bold {
  font-family: "Courier New", Helvetica, arial, sans-serif;
  font-weight: 700;
  margin-top: 10px;
  color: black
}
</style>
