<template>
  <view-content message="redfish" @refresh="refresh">
    <a-row :gutter="32">
      <a-col :span="6">
        <ul id="demo">
          <item
            class="item"
            :model="treeData"
            >
          </item>
        </ul>
      </a-col>
      <a-col :span="18" style="border-left: 1px solid black">
        <a-tabs defaultActiveKey="1">
          <a-tab-pane tab="Body" key="1">
            <a-row v-if="!loadingFlag">
              <a-col :span="12">
                <vue-json-pretty
                  :path="'res'"
                  :data="redfishBody"
                ></vue-json-pretty>
              </a-col>
            </a-row>
            <a-row justify="center" v-else>
              <a-col :span="4">
                <half-circle-spinner
                  :animation-duration="1000"
                  :size="65"
                  color="#90A4AE"
                />
              </a-col>
            </a-row>
          </a-tab-pane>
          <a-tab-pane tab="Header" key="2">
            <a-row>
              <a-col :span="8"><h3>Key</h3></a-col>
              <a-col :span="8"><h3>Value</h3></a-col>
            </a-row>
            <hr/>
            <a-row v-for="(key, index) in headerKeys" :key="index" style="margin-top: 10px">
              <a-col :span="8">{{key}}</a-col>
              <a-col :span="8">{{redfishHeader[key]}}</a-col>
            </a-row>
          </a-tab-pane>
        </a-tabs>
      </a-col>
    </a-row>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations, mapGetters } from 'vuex'
import VueJsonPretty from 'vue-json-pretty'
import { HalfCircleSpinner } from 'epic-spinners'
import Item from './item'

export default {
  name: 'redfish',
  data () {
    return {
      tabActive: null,
      tabTitles: ['Body', 'Header'],
      method: 'GET',
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      treeData: {
        name: 'Root API', // name为url列表树的展示题目
        path: '/redfish/v1' // path为实际的url
      }
    }
  },
  computed: {
    ...mapGetters({
      currentUrl: 'getURL',
      redfishBody: 'getRedfishBody',
      redfishHeader: 'getRedfishHeader',
      loadingFlag: 'getLoadingFlag'
    }),
    headerKeys () { // 头信息的Key值数组
      return Object.keys(this.redfishHeader)
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag']),
    refresh () {
      this.setRefreshFlag({ refreshFlag: false })
    }
  },
  components: {
    ViewContent,
    Item,
    VueJsonPretty,
    HalfCircleSpinner
  }
}
</script>
<style scoped>
.item {
  cursor: pointer;
}
</style>
