import { mapGetters, mapMutations } from 'vuex'

export default {
  created () {
    this.setRefreshFlag({ refreshFlag: true })
    this.refresh()
  },
  computed: {
    ...mapGetters({
      refreshFlag: 'getRefreshFlag'
    })
  },
  methods: {
    ...mapMutations(['setRefreshFlag'])
  },
  watch: {
    refreshFlag (val) {
      if (val) {
        this.refresh()
      }
    }
  }
}
