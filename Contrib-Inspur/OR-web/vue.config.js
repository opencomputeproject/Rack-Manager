const path = require('path')

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src/')
      }
    }
  },
  devServer: {
    port: 23333,
    public: '0.0.0.0:23333',
    proxy: {
      '/redfish/v1': {
        target: 'https://100.2.76.86',
        ws: true,
        secure: false,
        cookieDomainRewrite: 'localhost',
        debug: true,
        /* http <-> https 取消secure标志，是浏览器可以储存cookie  */
        onProxyRes: (proxyRes) => {
          let removeSecure = str => str.replace(/; Secure/i, '')
          let set = proxyRes.headers['set-cookie']
          if (set) {
            let result = Array.isArray(set)
              ? set.map(removeSecure)
              : removeSecure(set)
            proxyRes.headers['set-cookie'] = result
          }
        }
      }
    }
  },
  productionSourceMap: false
}
