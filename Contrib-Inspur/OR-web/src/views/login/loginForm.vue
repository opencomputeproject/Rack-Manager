<template>
  <div>
    <a-row>
      <a-col :xl="7" :xxl="6" :offset="9" style="margin-top: 3%">
        <a-card style="opacity: 0.9" :title="$t('message.common.title')" :bordered=false :headStyle="cardTitleStyle">
          <a-form id='components-form-demo-normal-login'>
            <a-form-item :validate-status="userNameError" :help="userNameMsg" has-feedback>
              <a-input
                :placeholder="$t('message.signin.username')" v-model="userName"
                >
                <a-icon slot="prefix" type='user' style="color: rgba(0,0,0,.25)" />
              </a-input>
            </a-form-item>
            <a-form-item hasFeedback :validate-status="userPswError" :help="userPswMsg">
              <a-input
                type='password' v-model="userPsw"
                :placeholder="$t('message.signin.psw')"
                @keyup.native.enter="submit"
                >
                <a-icon slot="prefix" type='lock' style="color: rgba(0,0,0,.25)" />
              </a-input>
            </a-form-item>
            <a-form-item>
              <a-radio-group v-model="lang">
                <a-radio-button value="zh">中文</a-radio-button>
                <a-radio-button value="en">English</a-radio-button>
              </a-radio-group>
            </a-form-item>
            <a-form-item>
              <a-button type='primary' @click='submit' style='width: 100%' :loading="loadingFlag">
                {{$t('message.signin.signin')}}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import errorHandler, { LOGIN } from '@/service/api'

export default {
  name: 'loginForm',
  data () {
    return {
      userName: undefined,
      userPsw: undefined,
      userNameError: '',
      userPswError: '',
      lang: '',
      loadingFlag: false,
      cardTitleStyle: {
        textAlign: 'center',
        fontSize: '1.5em'
      }
    }
  },
  created () {
    let curLang = localStorage.getItem('lang')

    if (curLang) this.lang = curLang
    else this.lang = 'zh'

    this.$i18n.locale = this.lang
  },
  watch: {
    lang (val) {
      localStorage.setItem('lang', this.lang)
      this.$i18n.locale = this.lang
      document.title = this.$t('message.common.title')
    },

    userName (val) {
      if (val) {
        this.userNameError = 'success'
      } else {
        this.userNameError = 'error'
      }
    },

    userPsw (val) {
      if (val) {
        this.userPswError = 'success'
      } else {
        this.userNameError = 'error'
      }
    }
  },
  computed: {
    userNameMsg () {
      if (this.userNameError === 'error') {
        return this.$t('message.signin.empty_user_err')
      } else {
        return ''
      }
    },

    userPswMsg () {
      if (this.userPswError === 'error') {
        return this.$t('message.signin.empty_psw_err')
      } else {
        return ''
      }
    }
  },
  methods: {
    submit (e) {
      e.preventDefault()
      if (!this.userName) {
        this.userNameError = 'error'
      }
      if (!this.userPsw) {
        this.userPswError = 'error'
      }

      if (this.userName && this.userPsw) {
        let data = {
          UserName: this.userName,
          Password: this.userPsw
        }

        this.onLogin(data)
      }
    },
    async onLogin (data) {
      this.loadingFlag = true
      try {
        await LOGIN(data)
        this.loadingFlag = false
        localStorage.setItem('username', this.userName)
        this.$router.push({ path: '/system-info' })
      } catch (error) {
        errorHandler(this, error, this.$t('message.signin.login_err_msg'))
        this.loadingFlag = false
      }
    }
  }
}
</script>
