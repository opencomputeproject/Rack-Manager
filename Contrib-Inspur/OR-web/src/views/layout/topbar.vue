<template>
  <a-layout-header style="padding: 0 10px 0 20px">
    <div class="logo">
      <h1>{{$t('message.common.title')}}</h1>
      <span>
        <a-icon
          class="trigger"
          :type="collapsed ? 'menu-unfold' : 'menu-fold'"
          @click="toggleCollapse"
        />
      </span>
    </div>
    <div class="header-right">
      <span class="header-item header-refresh" @click.prevent="pageRefresh">
        <a-icon type="reload" style="margin-right: 5px"/>{{$t('message.common.refresh')}}
      </span>
      <a-dropdown class="header-item" :disabled="fwUpdateState">
        <span class="header-user" >
          <span class="iconfont icon-translate"></span>{{$t('message.common.language')}}
        </span>
        <a-menu slot="overlay">
          <a-menu-item key="zh" @click="langChange">中文</a-menu-item>
          <a-menu-item key="en" @click="langChange">English</a-menu-item>
        </a-menu>
      </a-dropdown>
      <a-dropdown class="header-item" :disabled="fwUpdateState">
        <span class="header-user" >
          <a-icon type="user" style="margin-right: 5px"/>{{userName}}
        </span>
        <a-menu slot="overlay">
          <a-menu-item key="modify"><a-icon type="edit" />{{$t('message.common.edit_profile')}}</a-menu-item>
          <a-menu-item key="signOut" @click="signOut"><a-icon type="logout" />{{$t('message.common.sign_out')}}</a-menu-item>
        </a-menu>
      </a-dropdown>
    </div>
  </a-layout-header>
</template>

<script>
import { mapGetters, mapMutations } from 'vuex'

export default {
  name: 'topbar',
  data () {
    return {
      collapsed: false,
      userName: localStorage.getItem('username')

    }
  },
  computed: {
    ...mapGetters({
      lang: 'getLang',
      fwUpdateState: 'getFwUpdateState'
    })
  },
  methods: {
    ...mapMutations(['setRefreshFlag', 'setLang']),

    /* 语言切换 */
    langChange ({ key }) {
      this.setLang(key)
      this.$i18n.locale = key
      document.title = this.$t('message.common.title')
    },

    /* 页面刷新 */
    pageRefresh () {
      if (this.fwUpdateState === true) {
      } else {
        this.setRefreshFlag({ refreshFlag: true })
      }
    },

    toggleCollapse () {
      this.collapsed = !this.collapsed
      this.$emit('toggleCollapse', this.collapsed)
    },

    /* 注销 */
    signOut (ob) {
      localStorage.clear()
      this.$router.push({ path: 'login' })
    }
  }
}
</script>

<style scoped lang="less">
.iconfont {
  margin-right: 5px;
  font-size: 14px;
}

.header-right {
  float: right
}

.header-item {
  display: inline-block;
  height: 100%;
  padding: 0 15px ;
  margin-top: -3px;
}

.header-item:hover {
  background: #E3F2FD;
}

.header-refresh {
  cursor: pointer;
}

.header-user {
  cursor: pointer;
  margin-bottom: 20px;
}

.ant-layout-header {
  background: #fff;
  // color: #fff;
  position: relative;
  // z-index: 1;
  top: 0;
  width: 100%;
  box-shadow: 0 5px 20px #888888;
  height: 64px;
}

.ant-menu-horizontal {
  border-bottom: 0px;
}

.logo {
  float: left;
}

h1 {
  margin-bottom: 0;
  display: inline-block;
}

.ant-menu {
  height: 64px;
}

.ant-menu-submenu {
  float: right;
}

.trigger {
  font-size: 18px;
  line-height: 64px;
  padding: 0 24px;
  cursor: pointer;
  transition: color .3s;
}

#components-layout-demo-custom-trigger .trigger:hover {
  color: #1890ff;
}
</style>
