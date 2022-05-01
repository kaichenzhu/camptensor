// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import { router } from './router'
import { store } from './store'
import { request } from './request'

Vue.config.productionTip = false

// 引入 element-ui
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import '@/assets/style/theme/index.css'
Vue.use(ElementUI)

// // 引入 axios
// import axios from 'axios'
// axios.defaults.xsrfCookieName = 'csrftoken'
// axios.defaults.xsrfHeaderName = 'X-CSRFToken'
Vue.prototype.$request = request

// 引入echart
import * as echarts from 'echarts'
Vue.prototype.$echarts = echarts;
/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  request,
  components: { App },
  template: '<App/>'
})