/*
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:28:55
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-08 08:11:33
 * @FilePath: /MiniAdmin/front/src/main.js
 */
import { createApp } from 'vue'
import Antd from 'ant-design-vue';
import App from './App.vue'
// import 'ant-design-vue/dist/antd.css'; // 默认色
import 'ant-design-vue/dist/antd.dark.css' // 暗黑主题
import router from './router';
import './assets/main.css'
import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:8000/'
axios.defaults.headers = {
  "accept": "application / json",
  "Authorization": "Bearer " + sessionStorage.getItem('token')
}
const app = createApp(App);
app.use(Antd);
app.use(router);
app.mount('#app');


router.beforeEach((to, from, next) => {
  /* 路由发生变化修改页面title */
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})