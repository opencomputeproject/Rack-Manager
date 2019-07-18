<template>
  <a-table :columns="columns" :dataSource="memInfo" size="small" rowKey="name">

  </a-table>
</template>

<script>
export default {
  name: 'memInfo',
  props: ['memInfo'],
  data () {
    return {
      columns: [
        { title: this.$t('message.sysInfo.thead_name'), dataIndex: 'name' },
        { title: this.$t('message.sysInfo.thead_manufacturer'), dataIndex: 'vendor', align: 'center' },
        { title: this.$t('message.sysInfo.thead_size'), dataIndex: 'capacity', align: 'center' },
        { title: this.$t('message.sysInfo.thead_status'), dataIndex: 'health', align: 'center' },
        { title: this.$t('message.sysInfo.thead_mf'), dataIndex: 'speed', align: 'center' },
        { title: this.$t('message.sysInfo.thead_sn'), dataIndex: 'sn', align: 'center' }
      ]
    }
  }
}
</script>
