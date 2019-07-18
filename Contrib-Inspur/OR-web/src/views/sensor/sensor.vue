<template>
  <view-content message="sensor" @refresh="refresh">
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
    <a-row style="margin-bottom: 20px">
      <a-col :span="24">
        <a-table :columns="columns" :dataSource="parsedData" size="small" rowKey='name'>
          <div slot="filterDropdown" slot-scope="{ setSelectedKeys, selectedKeys, confirm, clearFilters }" class='custom-filter-dropdown'>
            <a-input
              v-ant-ref="c => searchInput = c"
              :placeholder="$t('message.sensor.search_placeholder')"
              :value="selectedKeys[0]"
              @change="e => setSelectedKeys(e.target.value ? [e.target.value] : [])"
              @pressEnter="() => handleSearch(selectedKeys, confirm)"
              style="width: 188px; margin-bottom: 8px; display: block;"
            />
            <a-button
              type='primary'
              @click="() => handleSearch(selectedKeys, confirm)"
              icon="search"
              size="small"
              style="width: 90px; margin-right: 8px"
            >{{$t('message.common.search')}}</a-button>
            <a-button
              @click="() => handleReset(clearFilters)"
              size="small"
              style="width: 90px"
            >{{$t('message.common.reset')}}</a-button>
          </div>
          <a-icon slot="filterIcon" slot-scope="filtered" type='search' :style="{ color: filtered ? '#108ee9' : undefined }" />
          <template slot="searchTitle" slot-scope="text">
            <span v-if="searchText">
              <template v-for="(fragment, i) in text.toString().split(new RegExp(`(?<=${searchText})|(?=${searchText})`, 'i'))">
                <mark v-if="fragment.toLowerCase() === searchText.toLowerCase()" :key="i" class="highlight">{{fragment}}</mark>
                <template v-else>{{fragment}}</template>
              </template>
            </span>
            <template v-else>{{text}}</template>
          </template>
          <span slot="status" slot-scope="status">
            <a-icon v-if="status == 'OK'" type="check-circle" style="color: green;font-size: 1.2em;"/>
            <a-icon v-else-if="status == 'warning'" type="warning" style="color: orange;font-size: 1.2em;"/>
            <span v-else class="iconfont icon-radioactive" style="color: red;font-size: 1.2em;"/>
          </span>
          <!-- eslint-disable-next-line vue/no-parsing-error -->
          <div v-for="(item, index) in scaleList" :key="index" :slot="item" slot-scope="value, record">
            <span v-if="record.type == 'temperature'">
              {{value + ' ℃'}}
            </span>
            <span v-else-if="record.type == 'voltage'">
              {{value + ' V'}}
            </span>
            <span v-else-if="record.type == 'RPM'">
              {{value + ' rpm'}}
            </span>
            <span v-else-if="record.type == 'watts'">
              {{value + ' W'}}
            </span>
            <span v-else-if="record.type == 'amperes'">
              {{value + ' A'}}
            </span>
          </div>
        </a-table>
      </a-col>
    </a-row>
    <a-row>
      <a-col :span="2">
        <a-icon type="check-circle" style="color: green;font-size: 1.2em;margin-right: 10px"/>{{$t('message.sensor.normal')}}
      </a-col>
      <a-col :span="2">
        <a-icon type="warning" style="color: orange;font-size: 1.2em;margin-right: 10px"/>{{$t('message.sensor.warning')}}
      </a-col>
      <a-col :span="2">
        <span class="iconfont icon-radioactive" style="color: red;font-size: 1.2em;margin-right: 10px"/>{{$t('message.sensor.critical')}}
      </a-col>
    </a-row>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import http from '@/service/api/http'
import errorHandler, { getChassisInfo } from '@/service/api'
// import { parseSensorData } from '@/service/utils/'

export default {
  name: 'sensor',
  data () {
    return {
      node: undefined,
      nodeList: [],
      chassisReqs: {},
      currentChassisInfo: {},
      scaleList: ['reading', 'minReading', 'maxReading', 'criticalLow', 'criticalUpper'],
      searchText: '',
      searchInput: null,
      sensorData: {},
      searchParams: {
        sensor: undefined,
        severity: undefined
      },
      columns: [
        { title: this.$t('message.sensor.thead_sensor'),
          dataIndex: 'name',
          width: 250,
          scopedSlots: {
            filterDropdown: 'filterDropdown',
            filterIcon: 'filterIcon',
            customRender: 'searchTitle'
          },
          onFilter: (value, record) => record.name.toLowerCase().includes(value.toLowerCase()),
          onFilterDropdownVisibleChange: (visible) => {
            if (visible) {
              setTimeout(() => {
                this.searchInput.focus()
              }, 0)
            }
          }
        },
        { title: this.$t('message.sensor.thead_status'),
          dataIndex: 'healthStatus',
          align: 'center',
          scopedSlots: { customRender: 'status' },
          filters: [{
            text: this.$t('message.sensor.normal'),
            value: 'normal'
          }, {
            text: this.$t('message.sensor.warning'),
            value: 'warning'
          }, {
            text: this.$t('message.sensor.critical'),
            value: 'critical'
          }],
          onFilter: (value, record) => record.healthStatus.indexOf(value) === 0
        },
        { title: this.$t('message.sensor.thead_current_reading'), dataIndex: 'reading', align: 'center', scopedSlots: { customRender: 'reading' } },
        { title: this.$t('message.sensor.thead_min_reading'), dataIndex: 'minReading', align: 'center', scopedSlots: { customRender: 'minReading' } },
        { title: this.$t('message.sensor.thead_max_reading'), dataIndex: 'maxReading', align: 'center', scopedSlots: { customRender: 'maxReading' } },
        { title: this.$t('message.sensor.thead_low_critical'), dataIndex: 'criticalLow', align: 'center', scopedSlots: { customRender: 'criticalLow' } },
        { title: this.$t('message.sensor.thead_high_critical'), dataIndex: 'criticalUpper', align: 'center', scopedSlots: { customRender: 'criticalUpper' } }
      ],
      parsedData: []
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
          this.chassisReqs[name] = [`/redfish/v1/Chassis/${name}/Power`, `/redfish/v1/Chassis/${name}/Thermal`]
        })
        this.node = this.nodeList[0]
        let resSplit = await Promise.all([
          http('get', this.chassisReqs[this.node][0]),
          http('get', this.chassisReqs[this.node][1])
        ])

        this.currentChassisInfo = {
          power: resSplit[0].data,
          thermal: resSplit[1].data
        }
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.setRefreshFlag({ refreshFlag: false })
      this.parsedData = this.parseData(this.currentChassisInfo)
    },

    // chassis变化回调函数
    async onChassisChange (val) {
      try {
        this.node = val
        let resSplit = await Promise.all([
          http('get', this.chassisReqs[this.node][0]),
          http('get', this.chassisReqs[this.node][1])
        ])

        this.currentChassisInfo = {
          power: resSplit[0].data,
          thermal: resSplit[1].data
        }
      } catch (error) {
        errorHandler(this, error, this.$t('message.sensor.get_err_msg'))
      }

      this.parsedData = []
      this.parsedData = this.parseData(this.currentChassisInfo)
    },

    // 解析数据
    parseData (content) {
      let res = []

      content.power.Voltages.forEach((item) => {
        res.push({
          name: item.Name,
          healthStatus: item.Status.Health,
          enableStatus: item.Status.State,
          reading: item.ReadingVolts,
          criticalLow: item.LowerThresholdCritical || '--',
          criticalUpper: item.UpperThresholdCritical || '--',
          minReading: item.MinReadingRange || '--',
          maxReading: item.MaxReadingRange || '--',
          type: 'voltage'
        })
      })

      content.thermal.Fans.forEach((item) => {
        res.push({
          name: item.Name,
          healthStatus: item.Status.Health,
          enableStatus: item.Status.State,
          reading: item.Reading.toFixed(2),
          criticalLow: item.LowerThresholdCritical ? item.LowerThresholdCritical.toFixed(2) : '--',
          criticalUpper: item.UpperThresholdCritical ? item.UpperThresholdCritical.toFixed(2) : '--',
          minReading: item.MinReadingRange || '--',
          maxReading: item.MaxReadingRange || '--',
          type: item.ReadingUnits
        })
      })

      content.thermal.Temperatures.forEach((item) => {
        res.push({
          name: item.Name,
          healthStatus: item.Status.Health,
          enableStatus: item.Status.State,
          reading: item.ReadingCelsius.toFixed(2),
          criticalLow: item.LowerThresholdCritical ? item.LowerThresholdCritical.toFixed(2) : '--',
          criticalUpper: item.UpperThresholdCritical ? item.UpperThresholdCritical.toFixed(2) : '--',
          minReading: item.MinReadingRang || '--',
          maxReading: item.MaxReadingRange || '--',
          type: 'temperature'
        })
      })

      return res
    },

    // 搜索传感器名称
    handleSearch (selectedKeys, confirm) {
      confirm()
      this.searchText = selectedKeys[0]
    },

    // 重置搜索框
    handleReset (clearFilters) {
      clearFilters()
      this.searchText = ''
    }

  },
  components: {
    ViewContent
  }
}
</script>

<style lang="less" scoped>
.custom-filter-dropdown {
  padding: 8px;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .15);
}

.highlight {
  background-color: rgb(255, 192, 105);
  padding: 0px;
}
</style>
