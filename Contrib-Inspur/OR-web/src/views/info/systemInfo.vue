<template>
  <view-content message="sysInfo" @refresh="refresh">
    <a-row style="margin-bottom: 20px">
      <a-form>
        <a-col :span="24">
          <a-form-item :label="$t('message.common.select_node')" :labelCol="{ span: 3 }" :wrapperCol="{ span: 4 }">
            <a-select v-model="system" @change="onSystemChange">
            <a-select-option v-for="(item, index) in systemList" :key="index" :value="item">{{'node ' + index}}</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-form>
    </a-row>
    <a-tabs tabPosition="left">
      <a-tab-pane :tab="$t('message.sysInfo.cpu')" key="cpu">
        <cpu-info :cpuInfo="cpuInfo"></cpu-info>
      </a-tab-pane>
      <a-tab-pane :tab="$t('message.sysInfo.mem')" key="mem">
        <mem-info :memInfo="memInfo"></mem-info>
      </a-tab-pane>
    </a-tabs>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'
import errorHandler, { getSystemInfo, getSingleSystemInfo, getSingleData } from '@/service/api'

import CpuInfo from './components/cpuInfo'
import MemInfo from './components/memInfo'

export default {
  name: 'systemInfo',
  data () {
    return {
      cpuInfo: [],
      memInfo: [],
      systemList: [],
      systemUrls: [],
      system: undefined,
      memUrls: [],
      cpuUrls: []
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag']),

    async refresh () {
      this.cpuInfo = []
      this.memInfo = []
      this.systemList = []
      this.systemUrls = []
      this.memUrls = []
      this.cpuUrls = []
      try {
        let systemInfo = await getSystemInfo()
        this.parseSystemList(systemInfo.data)
        this.system = this.systemList[0]
        let [resMem, resCpu] = await getSingleSystemInfo(this.systemList[0])
        this.parseMemUrls(resMem.data)
        this.parseCPUUrls(resCpu.data)

        this.getAllCPU()
        this.getALLMem()
      } catch (error) {
        errorHandler(this, error, this.$t('message.sysInfo.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
    },

    // system变化回调函数
    async onSystemChange () {
      this.systemUrls = []
      this.memUrls = []
      this.cpuUrls = []
      this.cpuInfo = []
      this.memInfo = []

      try {
        let [resMem, resCpu] = await getSingleSystemInfo(this.system)
        this.parseMemUrls(resMem.data)
        this.parseCPUUrls(resCpu.data)

        this.getAllCPU()
        this.getALLMem()
      } catch (error) {
        errorHandler(this, error, this.$t('message.sysInfo.get_err_msg'))
      }
    },

    // 解析system列表
    parseSystemList (content) {
      content.Members.forEach((system, index) => {
        let tmpArr = system['@odata.id'].split('/')
        let name = tmpArr.pop()
        this.systemList.push(name)
        this.systemUrls.push(system['@odata.id'])
      })
    },

    // 解析内存请求列表
    parseMemUrls (content) {
      content.Members.forEach((mem, index) => {
        this.memUrls.push(mem['@odata.id'])
      })
    },

    // 解析CPU请求列表
    parseCPUUrls (content) {
      content.Members.forEach((cpu, index) => {
        this.cpuUrls.push(cpu['@odata.id'])
      })
    },

    // 获取cpu信息列表
    async getAllCPU () {
      let reqs = []

      this.cpuUrls.forEach((url, index) => {
        reqs.push(getSingleData(url))
      })

      let res = await Promise.all(reqs)

      res.forEach((item, index) => {
        this.cpuInfo.push({
          name: item.data['@odata.id'].split('/').pop(),
          vendor: item.data.Manufacturer,
          model: item.data.Model,
          maxSpeed: item.data.MaxSpeedMHz,
          tdp: item.data.TDPWatts,
          cores: item.data.TotalCores,
          health: item.data.Status.Health,
          enable: item.data.Status.State
        })
      })
    },

    // 获取内存信息列表
    async getALLMem () {
      let reqs = []

      this.memUrls.forEach((url, index) => {
        reqs.push(getSingleData(url))
      })

      let res = await Promise.all(reqs)
      // console.log(res.data)
      res.forEach((item, index) => {
        this.memInfo.push({
          name: item.data['@odata.id'].split('/').pop(),
          vendor: item.data.Meanufacturer,
          sn: item.data.SerialNumber,
          health: item.data.Status.Health,
          enable: item.data.Status.State,
          speed: item.data.AllowedSpeedsMHz,
          capacity: (item.data.CapacityMiB / 1024)

        })
      })
    }
  },
  components: {
    ViewContent,
    CpuInfo,
    MemInfo
  }
}
</script>
