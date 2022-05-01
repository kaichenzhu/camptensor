import Vue from 'vue'
import Router from 'vue-router'
import Welcome from '@/components/Welcome'
import Login from '@/components/Login'
import NotFound from '@/components/NotFound'
import Register from '@/components/Register'
import Amzauth from '@/components/console/auth/Amzauth'
import Amzcallback from '@/components/console/auth/Amzcallback'
import ShopManage from '@/components/console/auth/ShopManage'
import AdLog from '@/components/console/ad/Log'
import AdOptimization from '@/components/console/ad/Optimization'
import AdOverview from '@/components/console/ad/Overview'
import AdReport from '@/components/console/ad/Report'
import AdDetail from '@/components/console/ad/Detail'
import AnlsSale from '@/components/console/anls/Sale'
import AnlsAd from '@/components/console/anls/Ad'
import ShopOverView from '@/components/console/shop/Overview'
import ShopProduct from '@/components/console/shop/Product'
import ShopStatus from '@/components/console/shop/Status'
import Test from '@/components/backend/Test'
import {
  store
} from '@/store/index'
import {
  setProfile
} from '@/utils/index'
Vue.use(Router)

export const router = new Router({
  mode: 'history',
  routes: [{
      path: '/',
      name: 'Welcome',
      component: Welcome
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '*',
      name: 'NotFound',
      component: NotFound
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/selftest',
      name: 'SelfTest',
      component: Test
    },
    {
      path: '/console/amzauth',
      name: 'Amzauth',
      component: Amzauth
    },
    {
      path: '/console/shopmanage',
      name: 'ShopManage',
      component: ShopManage
    },
    {
      path: '/console/callback',
      name: 'Amzcallback',
      component: Amzcallback
    },
    {
      path: '/console/ad/overview',
      name: 'AdOverview',
      component: AdOverview
    },
    {
      path: '/console/ad/report',
      name: 'AdReport',
      component: AdReport
    },
    {
      path: '/console/ad/detail',
      name: 'AdDetail',
      component: AdDetail
    },
    {
      path: '/console/ad/optimization',
      name: 'AdOptimization',
      component: AdOptimization
    },
    {
      path: '/console/ad/log',
      name: 'AdLog',
      component: AdLog
    },
    {
      path: '/console/anls/sale',
      name: 'AnlsSale',
      component: AnlsSale
    },
    {
      path: '/console/anls/ad',
      name: 'AnlsAd',
      component: AnlsAd
    },
    {
      path: '/console/shop/overview',
      name: 'ShopOverView',
      component: ShopOverView
    },
    {
      path: '/console/shop/product',
      name: 'ShopProduct',
      component: ShopProduct
    },
    {
      path: '/console/shop/status',
      name: 'ShopStatus',
      component: ShopStatus
    }
  ]
})

router.beforeEach((to, from, next) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const authRequired = to.path.startsWith('/console/');
  const authUser = store.state.authUser;
  const current_shopId = store.state.current_shopId;
  if (authUser && to.path === '/login') {
    router.push({ path: '/console/ad/report' }).catch(err => err);
  } else if (authRequired) {
    if (!authUser) {
      router.push({ path: '/login' }).catch(err => err);
    } else {
      if ((current_shopId == null || isNaN(current_shopId)) && !to.path.endsWith('callback') && !to.path.endsWith('shopmanage')) {
        setProfile().then(res => { next() });
      } else {
        next();
      }
    }
  } else {
    next();
  }
})
