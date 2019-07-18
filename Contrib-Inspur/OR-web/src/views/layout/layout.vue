<template>
  <div>
    <a-layout style="height: 100vh">
      <sidebar
        :collapsed="collapsed"
      ></sidebar>
      <a-layout>
        <topbar
          @toggleCollapse="onToggleCollapse"
        ></topbar>
        <a-spin :spinning="spinning" :tip="$t('message.common.loading')" size="large">
          <a-layout-content >
            <transition
              name="custom-classes-transition"
              enter-active-class="animated fadeIn"
            >
              <a-locale-provider :locale="locale">
                <router-view :key="$route.fullPath"></router-view>
              </a-locale-provider>
            </transition>
          </a-layout-content>
        </a-spin>
      </a-layout>
    </a-layout>
  </div>
</template>

<script>
import zhCN from 'ant-design-vue/lib/locale-provider/zh_CN'
import enUS from 'ant-design-vue/lib/locale-provider/en_US'
import { mapGetters } from 'vuex'

import Sidebar from './sidebar'
import Topbar from './topbar'

const minHeight = window.innerHeight - 64 - 20

export default {
  name: 'layout',
  created () {
  },
  data () {
    return {
      collapsed: false,
      spinning: false,
      minHeight: minHeight + 'px'
    }
  },
  computed: {
    ...mapGetters({
      refreshFlag: 'getRefreshFlag',
      lang: 'getLang'
    }),
    locale () {
      if (this.lang === 'zh') return zhCN
      else return enUS
    }
  },
  watch: {
    refreshFlag (val) {
      this.spinning = val
    }
  },
  methods: {
    onToggleCollapse (collapse) {
      this.collapsed = collapse
    }
  },
  components: {
    Sidebar,
    Topbar
  }
}
</script>

<style scoped lang="less">
.ant-layout-content {
  padding: 20px 20px 20px 20px;
  // overflow: 'auto';
  // min-height: 100%;
}
</style>
