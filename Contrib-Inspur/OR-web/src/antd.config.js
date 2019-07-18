import Vue from 'vue'
import { Row, Col, Card, Button, Form, Input, Icon, Layout, Menu, Radio,
  Tabs, Tooltip, Table, Spin, Dropdown, Checkbox, Select, Switch, DatePicker,
  TimePicker, LocaleProvider, Tag, Drawer, Steps, Upload, Alert, notification,
  Modal } from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css'

Vue.prototype.$notification = notification
Vue.prototype.$confirm = Modal.confirm
Vue.prototype.$warning = Modal.warning

Vue.use(Row)
Vue.use(Col)
Vue.use(Card)
Vue.use(Button)
Vue.use(Form)
Vue.use(Input)
Vue.use(Icon)
Vue.use(Layout)
Vue.use(Menu)
Vue.use(Radio)
Vue.use(Tabs)
Vue.use(Tooltip)
Vue.use(Table)
Vue.use(Spin)
Vue.use(Dropdown)
Vue.use(Checkbox)
Vue.use(Select)
Vue.use(Switch)
Vue.use(DatePicker)
Vue.use(TimePicker)
Vue.use(LocaleProvider)
Vue.use(Tag)
Vue.use(Drawer)
Vue.use(Steps)
Vue.use(Upload)
Vue.use(Alert)
Vue.use(Modal)
