const FwUpdate = resolve => require(['./fwUpdate'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/firmware-update',
  component: Layout,
  children: [{
    path: '',
    component: FwUpdate,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
