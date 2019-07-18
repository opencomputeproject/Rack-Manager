const Sensor = resolve => require(['./sensor'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/sensor',
  component: Layout,
  children: [{
    path: '',
    component: Sensor,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
