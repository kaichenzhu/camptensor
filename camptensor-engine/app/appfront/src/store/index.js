import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

function get_endpoints() {
  if (process.env.NODE_ENV === 'production') {
    return {
      jwtauth: 'https://www.camptensor.cn/jwtauth',
      baseUrl: 'https://www.camptensor.cn/api'
    }
  } else if (process.env.NODE_ENV === 'development') {
    return {
      jwtauth: 'http://123.57.224.241:8000/jwtauth',
      baseUrl: 'http://123.57.224.241:8000/api'
    }
  }
  console.error('cannot get environment variable at store: get_endpoints');
}

export const store = new Vuex.Store({
  state: {
    // 用户信息放state内存相较于直接从localstorage存储会快一些
    userId:localStorage.getItem('userId'),
    authUser: localStorage.getItem('authUser'),
    access: localStorage.getItem('access'),
    accessExp: localStorage.getItem('accessExp'),
    refresh: localStorage.getItem('refresh'),
    refreshExp: localStorage.getItem('refreshExp'),
    shops: JSON.parse(localStorage.getItem('shops')),
    current_shopId: localStorage.getItem('current_shopId'),
    current_shop_idx: localStorage.getItem('current_shop_idx'),
    current_profileId: localStorage.getItem('current_profileId'),
    current_profile_idx: localStorage.getItem('current_profile_idx'),
    start_date: localStorage.getItem('start_date'),
    end_date: localStorage.getItem('end_date'),
    region: localStorage.getItem('region'),
    endpoints: get_endpoints(),
    navbar: {
      isCollapse: false
    }
  },
  mutations: {
    setAuthUser(state, {
      userId,
      authUser,
      access,
      accessExp,
      refresh,
      refreshExp
    }) {
      Vue.set(state, 'userId', userId)
      Vue.set(state, 'authUser', authUser)
      Vue.set(state, 'access', access)
      Vue.set(state, 'accessExp', accessExp)
      Vue.set(state, 'refresh', refresh)
      Vue.set(state, 'refreshExp', refreshExp)
      localStorage.setItem('userId', userId)
      localStorage.setItem('authUser', authUser)
      localStorage.setItem('access', access)
      localStorage.setItem('accessExp', accessExp)
      localStorage.setItem('refresh', refresh)
      localStorage.setItem('refreshExp', refreshExp)
    },
    refreshToken(state, { access, refresh }) {
      // TODO: For security purposes, take localStorage out of the project.
      Vue.set(state, 'access', access)
      Vue.set(state, 'refresh', refresh)
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },
    removeUser(state) {
      // TODO: For security purposes, take localStorage out of the project.
      localStorage.removeItem('userId')
      localStorage.removeItem('authUser')
      localStorage.removeItem('access')
      localStorage.removeItem('accessExp')
      localStorage.removeItem('refresh')
      localStorage.removeItem('refreshExp')
      localStorage.removeItem('shops')
      localStorage.removeItem('current_profileId')
      localStorage.removeItem('current_profile_idx')
      localStorage.removeItem('current_shopId')
      localStorage.removeItem('current_shop_idx')

      state.userId = null;
      state.authUser = null;
      state.access = null;
      state.accessExp = null;
      state.refresh = null;
      state.refreshExp = null;
      state.shops = null;
      state.current_profileId = null;
      state.current_profile_idx = null;
      state.current_shopId = null;
      state.current_shop_idx = null;
    },
    navbarToggleFold(state) {
      state.navbar.isCollapse = !state.navbar.isCollapse;
    },
    setProfiles(state, shops) {
      Vue.set(state, 'shops', shops);
      Vue.set(state, 'current_shop_idx', 0);
      Vue.set(state, 'current_profile_idx', 0);
      Vue.set(state, 'current_profileId', shops[0]['profiles'][0]['profileId']);
      Vue.set(state, 'current_shopId', shops[0]['shopId']);
      localStorage.setItem('shops', JSON.stringify(shops));
      localStorage.setItem('current_profileId', shops[0]['profiles'][0]['profileId']);
      localStorage.setItem('current_shopId', shops[0]['shopId']);
      localStorage.setItem('current_profile_idx', 0);
      localStorage.setItem('current_shop_idx', 0);
    },
    setCurrentShop(state, {currentShopId, currentShopIdx}) {
      Vue.set(state, 'current_shopId', currentShopId);
      Vue.set(state, 'current_shop_idx', currentShopIdx);
      localStorage.setItem('current_shopId', currentShopId);
      localStorage.setItem('current_shop_idx', currentShopIdx);
    },
    setCurrentProfile(state, {currentProfileId, currentProfileIdx}) {
      Vue.set(state, 'current_profileId', currentProfileId);
      Vue.set(state, 'current_profile_idx', currentProfileIdx);
      localStorage.setItem('current_profileId', currentProfileId);
      localStorage.setItem('current_profile_idx', currentProfileIdx);
    },
    setStartDate(state, start) {
      state.start_date = start;
      localStorage.setItem('start_date', start);
    },
    setEndDate(state, end) {
      state.end_date = end;
      localStorage.setItem('end_date', end);
    },
    refreshProfileState(state, {shopIdx, profileIdx, newState}) {
      state.shops[shopIdx]['profiles'][profileIdx]['state'] = newState;
      localStorage.setItem('shops', JSON.stringify(state.shops));
    },
    setRegion(state, region) {
      state.region = region;
      localStorage.setItem('region', region);
    }
  }
})