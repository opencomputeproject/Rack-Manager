<template>
  <li>
    <div
      :class="{bold: isFolder}"
      @click="toggle(model.path)"
    >
      {{ model.name }}
      <span v-if="isFolder">[{{ open ? '-' : '+' }}]</span>
      <span class="ml-2">
        <half-circle-spinner v-if="loadingFlag" style="display: inline-block"
          :animation-duration="1000"
          :size="15"
          color="#000000"
        />
      </span>
    </div>
    <ul v-show="open" v-if="isFolder">
      <!-- 在此处递归 -->
      <item
        class="item"
        v-for="(model, index) in children"
        :key="index"
        :model="model">
      </item>
      <!-- <li class="add" @click="addChild">+</li> -->
    </ul>
  </li>
</template>

<script>
import { mapMutations } from 'vuex'
// import axios from 'axios'
import { HalfCircleSpinner } from 'epic-spinners'
import errorHandler, { getRedfish } from '@/service/api'

export default {
  name: 'item',
  props: {
    model: Object
  },
  data () {
    return {
      loadingFlag: false,
      open: false,
      children: []
    }
  },
  computed: {
    isFolder: function () {
      return this.children &&
        this.children.length
    }
  },
  methods: {
    ...mapMutations(['setURL', 'setRedfishBody', 'setRedfishHeader', 'setLoadingFlag']),
    toggle (path) {
      if (this.isFolder) { // 如果已经获取过下级，则再打开目录时不需要在重新获取
        this.open = !this.open
      } else { // 首次获取下级数据
        this.loadingFlag = true
        this.setLoadingFlag({ loadingFlag: this.loadingFlag })
        // this.getData(path)
      }
      // this.loadingFlag = true
      // this.setLoadingFlag({ loadingFlag: this.loadingFlag })
      this.getData(path)
      this.setURL({ url: path }) // 更新当前url
    },
    async getData (path) {
      try {
        let res = await getRedfish(path)
        console.log(res.data)
        let keys = Object.keys(res.data)
        if (!this.isFolder) {
          keys.forEach(key => { // 遍历返回数据的每个属性
            if (res.data[key]) {
              if (res.data[key]['@odata.id']) { // 如果子对象含有'@odata.id'属性，则保存其url值，push进children
                this.children.push({
                  name: key,
                  path: res.data[key]['@odata.id']
                })
              } else if (key === 'Members') { // 如果子对象存在Members数组
                let members = res.data[key]
                if (members.length) { // 数组不为空
                  members.forEach((val, index) => { // 则也push进children数组
                    this.children.push({
                      name: index + 1,
                      path: members[index]['@odata.id']
                    })
                  })
                }
              }
            }
          })
        }

        this.loadingFlag = false
        this.setRedfishBody({ redfishBody: res.data })
        this.setRedfishHeader({ redfishHeader: res.headers })
        this.setLoadingFlag({ loadingFlag: this.loadingFlag })
      } catch (error) {
        errorHandler(this, error, '')
        this.loadingFlag = false
        this.setLoadingFlag({ loadingFlag: this.loadingFlag })
      }
    }
  },
  components: {
    HalfCircleSpinner
  }
}
</script>

<style scoped>
  ul {
    /* list-style-type: none; */
    font-size: 16px;
    padding-left: 24px;
  }

  li:hover {
    font-size: 1.2em;
    /* background-color: aliceblue */
  }
</style>
