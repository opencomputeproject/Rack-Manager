<template>
  <view-content message="fwUpdate" @refresh="refresh">
    <a-row>
      <a-col :span="24">
        <a-steps direction="horizontal" :current="currentStep">
          <a-step :title="$t('message.fwUpdate.fw_update_entrance')" />
          <a-step :title="$t('message.fwUpdate.fw_src')" />
          <a-step :title="$t('message.fwUpdate.fw_file')" />
          <a-step :title="$t('message.fwUpdate.fw_update')" />
        </a-steps>
      </a-col>
    </a-row>
    <a-row style="margin-bottom: 20px">
      <a-col :span="24">
        <div class="step-content">
          <div id="fw-update-entrance" v-if="currentStep == 0">
            <div class="fwupdate-warning">
              <div class="warning-title">{{$t('message.fwUpdate.fw_update_warning_title')}}</div>
              <div class="warning-msg">{{$t('message.fwUpdate.fw_update_warning_msg')}}</div>
              <div>
                <a-button type="primary" @click.prevent="enterFwUpdate">{{$t('message.fwUpdate.fw_update_entrance')}}</a-button>
              </div>
            </div>
          </div>
          <div id="fw-src" v-if="currentStep == 1">
            <a-form>
              <a-form-item :label="$t('message.fwUpdate.fw_src')" :labelCol="{ span: 4 }" :wrapperCol="{ span: 10 }"
                :validate-status="fwSrcError" :help="fwSrcHint"
              >
                <a-radio-group v-model="fwSrc" disabled>
                  <a-radio value="local">{{$t('message.fwUpdate.local_fw')}}</a-radio>
                  <a-radio value="tftp">{{$t('message.fwUpdate.tftp_fw')}}</a-radio>
                </a-radio-group>
              </a-form-item>
              <a-form-item :labelCol="{ span: 4 }" :wrapperCol="{ span: 4, offset: 4 }">
                <a-button @click.prevent="stepToUpload" type='primary'>{{$t('message.fwUpdate.next')}}</a-button>
              </a-form-item>
            </a-form>
          </div>
          <div id="fw-file" v-if="currentStep == 2">
            <a-row style="margin-bottom: 20px" v-if="fwSrc === 'local'">
              <a-col :span="24">
                <a-upload-dragger name="file" @change="handleChange" :beforeUpload="beforeUpload"
                  :fileList="fileList"
                  >
                  <p class="ant-upload-drag-icon">
                    <a-icon type="inbox" />
                  </p>
                  <p class="ant-upload-text">{{$t('message.fwUpdate.upload_text')}}</p>
                  <p class="ant-upload-hint">{{$t('message.fwUpdate.upload_hint')}}</p>
                </a-upload-dragger>
              </a-col>
            </a-row>
            <a-row style="margin-bottom: 20px" v-if="fwSrc === 'tftp'">
              <a-col :span="24">
                <a-form>
                  <a-form-item :label="$t('message.fwUpdate.tftp_addr')" :labelCol="{ span: 4 }" :wrapperCol="{ span: 4 }"
                    :validate-status="tftpAddrError" :help="tftpAddrHint" has-feedback
                  >
                    <a-input v-model="tftpAddr" :placeholder="$t('message.fwUpdate.tftp_addr_placeholder')"></a-input>
                  </a-form-item>
                  <a-form-item :label="$t('message.fwUpdate.tftp_file')" :labelCol="{ span: 4 }" :wrapperCol="{ span: 4 }"
                    :validate-status="fileNameError" :help="fileNameHint" has-feedback
                  >
                    <a-input v-model="fileName" :placeholder="$t('message.fwUpdate.tftp_file')"></a-input>
                  </a-form-item>
                </a-form>
              </a-col>
            </a-row>
            <a-row style="text-align: center">
              <!-- <a-button type='danger' @click="getPrepared">{{$t('message.common.reboot')}}</a-button>
              <a-button style="margin-left: 20px" @click="checkUpdateStatus">check</a-button> -->
              <a-button :loading="fileLoading" v-if="fwSrc === 'local'" @click="upload" icon="upload" type='primary'>{{$t('message.common.upload')}}</a-button>
              <a-button :loading="fileLoading" v-if="fwSrc === 'tftp'" @click="download" icon="download" type='primary'>{{$t('message.common.download')}}</a-button>
              <a-button style="margin-left: 20px" :disabled="!imgReady" @click="() => {currentStep = 3}" type='primary'>{{$t('message.fwUpdate.next')}}</a-button>
              <a-button style="margin-left: 20px" :disabled="imgReady || fileLoading" @click="() => {currentStep = 1}">{{$t('message.fwUpdate.previous')}}</a-button>
            </a-row>
          </div>
          <div id="fw-flash" v-if="currentStep == 3">
            <div class="fwupdate-warning">
              <div class="warning-title">{{$t('message.fwUpdate.fw_update_warning_title')}}</div>
              <div class="warning-msg">{{$t('message.fwUpdate.flash_warning_msg')}}</div>
              <div>
                <a-button style="margin-left: 20px" @click="warmReboot" type="primary">{{$t('message.fwUpdate.flash')}}</a-button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="currentStep != 0" class="abort-button">
          <a-button size="large" @click.prevent="abortFwUpdate">{{$t('message.fwUpdate.abort')}}</a-button>
        </div>
      </a-col>
    </a-row>
  </view-content>
</template>

<script>
import ViewContent from '@/components/viewContent'
import { mapMutations } from 'vuex'

import errorHandler,
{ prepareForUpdate, downloadFromTftp, getStatusAndProgress, applyImage, rebootBmc } from '@/service/api'

export default {
  name: 'fwUpdate',
  data () {
    return {
      currentStep: 0,
      fwSrc: 'tftp',
      fileList: [],
      fwSrcError: '',
      tftpAddr: undefined,
      tftpAddrError: '',
      fileName: undefined,
      fileNameError: '',
      imageRedyFlag: false, // 镜像上传或从tftp下载成功的标志位
      intervalID: 0, // 进度轮询ID
      fileLoading: false, // 上传/下载按钮loading标志
      imgReady: false // 固件文件是否已准备完毕
    }
  },
  computed: {
    fwSrcHint () {
      if (this.fwSrcError === 'error') {
        return this.$t('message.fwUpdate.fw_src_error')
      } else {
        return ''
      }
    },

    tftpAddrHint () {
      if (this.tftpAddrError === 'error') {
        return this.$t('message.fwUpdate.tftp_addr_error')
      } else {
        return ''
      }
    },

    fileNameHint () {
      if (this.fileNameError === 'error') {
        return this.$t('message.fwUpdate.tftp_file_error')
      } else {
        return ''
      }
    }
  },
  watch: {
    fwSrc (val) {
      if (val) {
        this.fwSrcError = 'success'
      }
    },

    tftpAddr (val) {
      if (val) {
        this.tftpAddrError = 'success'
      } else {
        this.tftpAddrError = 'error'
      }
    },

    fileName (val) {
      if (val) {
        this.fileNameError = 'success'
      } else {
        this.fileNameError = 'error'
      }
    }
  },
  methods: {
    ...mapMutations(['setRefreshFlag', 'setFwUpdateState']),

    refresh () {
      setTimeout(() => {
        this.setRefreshFlag({ refreshFlag: false })
      }, 1000)
    },

    /* 进入固件更新模式 */
    enterFwUpdate (e) {
      this.setFwUpdateState(true)
      this.currentStep = 1
    },

    /* 退出固件更新模式 */
    abortFwUpdate () {
      let path = this.$route.path + `?t=${+new Date()}`
      this.$router.push({ path })
      this.setFwUpdateState(false)
    },

    stepToUpload (e) {
      if (!this.fwSrc) {
        this.fwSrcError = 'error'
      } else {
        this.currentStep = 2
      }
    },

    // 中断默认上传操作
    beforeUpload (file) {
      console.log(file)
      this.fileList = [file]
      return false
    },

    // 准备工作
    async getPrepared () {
      try {
        await prepareForUpdate()
      } catch (error) {
        errorHandler(this, error, 'prepare 失败')
      }
    },

    // 执行下载操作
    async download () {
      if (!this.tftpAddr || !this.fileName) {
        this.tftpAddrError = this.tftpAddr ? '' : 'error'
        this.fileNameError = this.fileName ? '' : 'error'
      } else {
        let data = [this.tftpAddr, this.fileName.trim()]
        this.fileLoading = true
        try {
          await downloadFromTftp({ data })
          this.intervalID = setInterval(this.getUpdateStatus, 2000)
        } catch (error) {
          errorHandler(this, error, this.$t('message.fwUpdate.upload_err_msg'))
        }
      }
    },

    // 获取更新进度
    async getUpdateStatus () {
      try {
        let res = await getStatusAndProgress()
        console.log(res)
        if (res.data.indexOf('Deferred for mounted filesystem. reboot BMC to apply') >= 0) {
          clearInterval(this.intervalID)
          this.fileLoading = false
          this.imgReady = true

          if (this.fwSrc === 'local') {
            this.$notification.success({
              message: this.$t('message.fwUpdate.upload_done'),
              placement: 'bottomRight'
            })
          } else {
            this.$notification.success({
              message: this.$t('message.fwUpdate.download_done'),
              placement: 'bottomRight'
            })
          }
        } else if (res.data.indexOf('Download Error') >= 0) {
          clearInterval(this.intervalID)
          this.fileLoading = false

          if (this.fwSrc === 'local') {
            this.$notification.error({
              message: this.$t('message.fwUpdate.upload_err_msg'),
              description: this.$t('message.fwUpdate.upload_err_msg'),
              placement: 'bottomRight'
            })
          } else {
            this.$notification.error({
              message: this.$t('message.fwUpdate.download_err_msg'),
              description: this.$t('message.fwUpdate.download_err_detail'),
              placement: 'bottomRight'
            })
          }
        }
      } catch (error) {
        errorHandler(this, error, '无法查看进度')
      }
    },

    // 执行刷新操作
    async flashImage () {
      try {
        await applyImage()
      } catch (error) {
        errorHandler(this, error, '刷新失败')
      }
    },

    // 执行重启动作
    async warmReboot () {
      try {
        await rebootBmc()
        this.$notification.success({
          message: this.$t('message.fwUpdate.reboot_done'),
          placement: 'bottomRight'
        })
      } catch (error) {
        errorHandler(this, error, this.$t('message.fwUpdate.reboot_done'))
      }
    },

    handleChange (info) {}
  },
  components: {
    ViewContent
  }
}
</script>
<style lang="less" scoped>
.warning-title {
  font-size: 2em;
  color: red;
  margin-bottom: 20px;
}

.warning-msg {
  font-size: 1em;
  margin-bottom: 20px;
}

.step-content {
  margin-top: 16px;
  border: 1px dashed #e9e9e9;
  border-radius: 6px;
  background-color: #fafafa;
  min-height: 200px;
  // text-align: center;
  padding: 40px;
}

.fwupdate-warning {
  text-align: center;
  padding: 30px;
  border: 1px dashed #ccc5c5;
  border-radius: 6px;
  min-height: 120px;
}

.abort-button {
  text-align: center;
  margin-top: 20px;
}

</style>
