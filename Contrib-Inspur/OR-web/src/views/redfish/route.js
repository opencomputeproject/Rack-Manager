const Redfish = resolve => require(['./redfish'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/redfish',
  component: Layout,
  children: [{
    path: '',
    component: Redfish,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
