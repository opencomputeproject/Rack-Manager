<template>
  <div id="login">
    <login-form></login-form>
  </div>
</template>

<script>
import LoginForm from './loginForm'

export default {
  name: 'Login',
  data () {
    return {}
  },
  components: {
    LoginForm
  }
}
</script>

<style scoped>
#login {
  position: absolute;
  top: 120px;
  width: 100%;
  padding: 0;
  height: 70%;
  /*margin-top: 120px;*/
  background-color: #f5f5f5;
  background: url("../../assets/img/data-center.jpg") no-repeat;
  background-size: 100% 100%
}

#inspur {
  margin-left: 13.33%;
  background-image: url("../../assets/img/inspur.png");
  position: absolute;
  top: -50px;
  width: 209px;
  height: 41px;
  overflow: hidden;
}
</style>
