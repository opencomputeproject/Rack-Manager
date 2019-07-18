import '@babel/polyfill'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/store'
import './antd.config'

import Vuelidate from 'vuelidate'
import VueI18n from 'vue-i18n'

import i18nMessage from './service/i18n'

import './assets/font/iconfont/iconfont.css'
import './assets/css/styles.css'
import 'animate.css/animate.min.css'

Vue.config.productionTip = false

Vue.use(Vuelidate)
Vue.use(VueI18n)

const i18n = new VueI18n({
  locale: 'en', // set locale
  messages: i18nMessage // set locale messages
})

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
