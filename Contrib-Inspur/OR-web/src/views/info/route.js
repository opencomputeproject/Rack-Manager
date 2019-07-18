const SystemInfo = resolve => require(['./systemInfo'], resolve)
const FRU = resolve => require(['./fruInfo'], resolve)
const BiosInfo = resolve => require(['./biosInfo'], resolve)
const Layout = resolve => require(['../layout/layout'], resolve)

export default [{
  path: '/system-info',
  component: Layout,
  children: [{
    path: '',
    component: SystemInfo,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}, {
  path: '/fru-info',
  component: Layout,
  children: [{
    path: '',
    component: FRU,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}, {
  path: '/bios-info',
  component: Layout,
  children: [{
    path: '',
    component: BiosInfo,
    meta: {
      requiresRole: 'ALL'
    }
  }]
}]
