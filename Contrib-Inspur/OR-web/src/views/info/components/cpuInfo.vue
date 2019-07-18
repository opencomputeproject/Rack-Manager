<template>
  <a-table :columns="columns" :dataSource="cpuInfo" size="small" rowKey="name">

  </a-table>
</template>

<script>
export default {
  name: 'cpuInfo',
  props: ['cpuInfo'],
  data () {
    return {
      columns: [
        { title: this.$t('message.sysInfo.thead_name'), dataIndex: 'name' },
        { title: this.$t('message.sysInfo.thead_manufacturer'), dataIndex: 'vendor', align: 'center' },
        { title: this.$t('message.sysInfo.thead_model'), dataIndex: 'model', align: 'center' },
        { title: this.$t('message.sysInfo.thead_status'), dataIndex: 'health', align: 'center' },
        { title: this.$t('message.sysInfo.thead_speed'), dataIndex: 'maxSpeed', align: 'center' },
        { title: this.$t('message.sysInfo.thead_core'), dataIndex: 'cores', align: 'center' },
        { title: this.$t('message.sysInfo.thead_tdp'), dataIndex: 'tdp', align: 'center' }
      ]
    }
  }
}
</script>
