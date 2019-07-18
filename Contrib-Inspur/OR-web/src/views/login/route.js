const Login = resolve => require(['./login'], resolve)

export default [{
  path: '/login',
  component: Login,
  meta: {
    requiresRole: 'ALL'
  }
}]
