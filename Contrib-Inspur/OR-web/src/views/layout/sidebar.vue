<template>
  <a-layout-sider
    :trigger="null"
    collapsible
    v-model="collapsed"
    width="200"
    >
    <a-menu theme="dark" mode="inline"
      :openKeys="openKeys"
      @openChange="onOpenChange"
      >
      <a-menu-item key="inventory" :disabled="fwUpdateState">
        <router-link to="system-info"><a-icon type="appstore" />
          <span>{{$t('message.common.inventory')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="fru" :disabled="fwUpdateState">
        <router-link to="fru-info"><a-icon type="profile" />
          <span>{{$t('message.common.fruInfo')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="nodeInfo" :disabled="fwUpdateState">
        <router-link to="node-info"><a-icon type="hdd" />
          <span>{{$t('message.common.nodeInfo')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="sensor" :disabled="fwUpdateState">
        <router-link to="sensor"><a-icon type="bars" />
          <span>{{$t('message.common.sensorInfo')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="psu" :disabled="fwUpdateState">
        <router-link to="psu"><a-icon type="api" />
          <span>{{$t('message.common.psuInfo')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="fanCtrl" :disabled="fwUpdateState">
        <router-link to="fan-controller"><span class="iconfont icon-fan" />
          <span>{{$t('message.common.fan_controller')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="fwUpdate" :disabled="fwUpdateState">
        <router-link to="firmware-update"><a-icon type="upload" />
          <span>{{$t('message.common.firmware_update')}}</span>
        </router-link>
      </a-menu-item>
      <a-menu-item key="redfish" :disabled="fwUpdateState">
        <router-link to="redfish"><span class="iconfont icon-Fish" />
          <span>Redfish</span>
        </router-link>
      </a-menu-item>
    </a-menu>
  </a-layout-sider>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'sidebar',
  props: ['collapsed'],
  data () {
    return {
      rootSubmenuKeys: ['info', 'fan_cool', 'log', 'fault_diagnose', 'settings', 'remote-control'],
      openKeys: []
    }
  },
  computed: {
    ...mapGetters({
      fwUpdateState: 'getFwUpdateState'
    })
  },
  methods: {
    /* 同时只展开一个父级菜单 */
    onOpenChange (openKeys) {
      console.log(openKeys)
      const latestOpenKey = openKeys.find(key => this.openKeys.indexOf(key) === -1)
      console.log(latestOpenKey)
      if (this.rootSubmenuKeys.indexOf(latestOpenKey) === -1) {
        this.openKeys = openKeys
      } else {
        this.openKeys = latestOpenKey ? [latestOpenKey] : []
      }
    }
  }
}
</script>

<style scoped lang="less">
.ant-layout-sider {
  z-index: 2;
  color: #fff;
  overflow: auto;
  height: 100vh;
  left: 0;
}

.ant-menu {
  height: 100%;
}

.iconfont {
  margin-right: 8px;
}

.ant-menu-item .iconfont + span, .ant-menu-submenu-title .iconfont + span {
  -webkit-transition: opacity 0.3s;
  transition: opacity 0.3s;
  -webkit-transition-timing-function: cubic-bezier(0.645, 0.045, 0.355, 1), cubic-bezier(0.645, 0.045, 0.355, 1);
  transition-timing-function: cubic-bezier(0.645, 0.045, 0.355, 1), cubic-bezier(0.645, 0.045, 0.355, 1);
  opacity: 1;
}

.ant-menu-inline-collapsed > .ant-menu-item .iconfont + span,
.ant-menu-inline-collapsed > .ant-menu-submenu > .ant-menu-submenu-title .iconfont + span {
  max-width: 0;
  display: inline-block;
  opacity: 0;
}

</style>
