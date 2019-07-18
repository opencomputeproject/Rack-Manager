export default {
  state: {
    refreshFlag: false
  },
  getters: {
    getRefreshFlag (state) {
      return state.refreshFlag
    }
  },
  mutations: {
    setRefreshFlag (state, { refreshFlag }) {
      state.refreshFlag = refreshFlag
    }
  }
}
