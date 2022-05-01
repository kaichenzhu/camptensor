import axios from "axios";
import { store } from "../store";
import { refreshToken } from "../utils";
import { router } from "../router";
import { Loading } from 'element-ui';

// 创建一个axios实例
export const request = axios.create({
  timeout: 300000,
  headers: {
    "Content-Type": "application/json"
  }
});

// 是否正在刷新的标记
let isRefreshing = false;
// 重试队列，每一项将是一个待执行的函数形式
let requests = [];
// 请求发起前页面加载等待
let loadingInstance = null;
request.interceptors.request.use((config) => {
  loadingInstance = Loading.service({ // 发起请求时加载全局loading，请求失败或有响应时会关闭
    spinner: 'fa fa-spinner fa-spin fa-3x fa-fw',
    text: '拼命加载中...'
  })
  if (!config.url.endsWith('jwtauth/register/')) {
    // 注册时不需要走token认证
    config.headers["Authorization"] = `Bearer ${store.state.access}`;
  }
  return config
}, (error) => {
  console.log(error);
  return Promise.reject(error)
})


request.interceptors.response.use(
  response => {
    loadingInstance.close();
    return response
  }, error => {
    if (
      error.response.data.code === "token_not_valid" &&
      error.response.status === 401 &&
      error.response.statusText === "Unauthorized"
    ) {
      const config = error.response.config;
      if (isRefreshing && error.response.config.url.endsWith('/refresh_token/')) {
        localStorage.clear();
        window.location.href = '/login'
      }
      if (!isRefreshing) {
        isRefreshing = true;
        return request
          .post(`${store.state.endpoints.jwtauth}/refresh_token/`, {
            refresh: store.state.refresh
          })
          .then(res => {
            refreshToken(res.data);
            requests.forEach(cb => cb());
            requests = [];
            return request(config);
          })
          .catch(res => {
            console.error("refreshtoken error =>", res);
          })
          .finally(() => {
            isRefreshing = false;
          });
      } else {
        // 正在刷新token，将返回一个未执行resolve的promise
        return new Promise(resolve => {
          // 将resolve放进队列，用一个函数形式来保存，等token刷新后直接执行
          requests.push(() => {
            resolve(request(config));
          });
        });
      }
    }
    loadingInstance.close();
    return Promise.reject(error);
  }
);
