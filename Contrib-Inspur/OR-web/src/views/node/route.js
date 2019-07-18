const NodeInfo = resolve => require(['./nodeinfo'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/node-info',
  component: Layout,
  children: [{
    path: '',
    component: NodeInfo,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
