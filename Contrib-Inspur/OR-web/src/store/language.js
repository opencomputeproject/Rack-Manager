export default {
  state: {
    lang: localStorage.getItem('lang')
  },
  getters: {
    getLang (state) {
      return state.lang
    }
  },
  mutations: {
    setLang (state, lang) {
      localStorage.setItem('lang', lang)
      state.lang = lang
    }
  }
}
