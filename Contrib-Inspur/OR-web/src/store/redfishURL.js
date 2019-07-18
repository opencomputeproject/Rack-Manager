export default {
  state: {
    currentURL: '',
    redfishBody: {},
    redfishHeader: {},
    loadingFlag: false
  },
  getters: {
    getURL (state) {
      return state.currentURL
    },
    getRedfishBody (state) {
      return state.redfishBody
    },
    getRedfishHeader (state) {
      return state.redfishHeader
    },
    getLoadingFlag (state) {
      return state.loadingFlag
    }
  },
  mutations: {
    setURL (state, { url }) {
      state.currentURL = url
    },
    setRedfishBody (state, { redfishBody }) {
      state.redfishBody = redfishBody
    },
    setRedfishHeader (state, { redfishHeader }) {
      state.redfishHeader = redfishHeader
    },
    setLoadingFlag (state, { loadingFlag }) {
      state.loadingFlag = loadingFlag
    }
  }
}
