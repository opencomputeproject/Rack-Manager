export default {
  watch: {
    lang (val) {
      let path = this.$route.path + `?t=${+new Date()}`
      this.$router.push({ path })
    }
  }
}
