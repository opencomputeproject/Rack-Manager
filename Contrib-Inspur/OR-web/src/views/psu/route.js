const Psu = resolve => require(['./psu'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/psu',
  component: Layout,
  children: [{
    path: '',
    component: Psu,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
