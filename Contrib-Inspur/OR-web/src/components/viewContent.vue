<template>
  <div>
    <a-row>
      <a-col :span="24">
        <h1 style="display: inline-block;margin-right: 10px">{{$t(`message.${message}.title`)}}</h1>
        <span style="color: #9E9E9E">{{$t(`message.${message}.sub_title`)}}</span>
        <a-tooltip placement="top" >
          <template slot="title">
            <span>{{$t('message.common.help')}}</span>
          </template>
          <!-- <span class="help-mark"><a-icon type="question-circle" @click="toggleHelp"/></span> -->
        </a-tooltip>
      </a-col>
    </a-row>
    <!-- <help-card :helpFlag="helpFlag">{{$t(`message.${message}.helpMsg`)}}</help-card> -->
    <a-row>
      <a-col :span="24">
        <a-card :bordered="false" :loading="refreshFlag">
          <slot></slot>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import langWatcher from '@/service/mixin/langWatcher'
import toggleHelp from '@/service/mixin/toggleHelp'
import HelpCard from '@/components/helpCard'
import { mapGetters, mapMutations } from 'vuex'

export default {
  name: 'viewContent',
  mixins: [langWatcher, toggleHelp],
  props: ['message'],
  created () {
    this.setRefreshFlag({ refreshFlag: true })
  },
  computed: {
    ...mapGetters({
      refreshFlag: 'getRefreshFlag',
      lang: 'getLang'
    })
  },
  watch: {
    refreshFlag (val) {
      if (val) {
        this.$emit('refresh')
      }
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag'])
  },
  components: {
    HelpCard
  }
}
</script>
