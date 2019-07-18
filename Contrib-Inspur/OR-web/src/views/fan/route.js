const FanCtrl = resolve => require(['./fanController'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/fan-controller',
  component: Layout,
  children: [{
    path: '',
    component: FanCtrl,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
