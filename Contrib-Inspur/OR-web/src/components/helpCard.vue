<template>
  <div>
    <transition
        name="custom-classes-transition"
        enter-active-class="animated fadeIn"
      >
      <a-row class="help-msg" v-if="helpFlag">
        <a-col :span="24">
          <a-card :bordered="false" :bodyStyle="helpCardStyle">
            <slot></slot>
          </a-card>
        </a-col>
      </a-row>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'helpCard',
  props: ['helpFlag'],
  data () {
    return {
      helpCardStyle: {
        backgroundColor: '#E0F2F1',
        color: '#0277BD'
      }
    }
  }
}
</script>
