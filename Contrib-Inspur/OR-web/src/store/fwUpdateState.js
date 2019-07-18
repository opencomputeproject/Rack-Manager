export default {
  state: {
    updateState: false
  },
  getters: {
    getFwUpdateState (state) {
      return state.updateState
    }
  },
  mutations: {
    setFwUpdateState (state, updateState) {
      state.updateState = updateState
    }
  }
}
