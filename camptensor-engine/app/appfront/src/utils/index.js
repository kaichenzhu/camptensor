import { store } from "@/store/index";
import { request } from "@/request/index";
import { router } from "@/router/index";

function parseJwt(encode) {
  var base64Url = encode.split(".")[1];
  var base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  var jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map(function(c) {
        return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join("")
  );

  return JSON.parse(jsonPayload);
}

function saveToken(token) {
  const access = token.access;
  const refresh = token.refresh;
  const access_info = parseJwt(access);
  const refresh_info = parseJwt(refresh);
  store.commit("setAuthUser", {
    userId: access_info.user_id,
    authUser: access_info.user_name,
    access: access,
    accessExp: access_info.exp,
    refresh: refresh,
    refreshExp: refresh_info.exp
  });
  var date = new Date();
  var year = date.getFullYear(); //获取完整的年份(4位)
  var month = date.getMonth() + 1; //获取当前月份(0-11,0代表1月)
  var day = date.getDate(); //获取当前日
  if (month <= 9) {
    month = "0" + month;
  }
  if (day <= 9) {
    day = "0" + day;
  }
  store.commit("setStartDate", year + month + day);
  store.commit("setEndDate", year + month + day);
  router.push({ name: "AdReport" }).catch(err => err);
}

function refreshToken(token) {
  const access = token.access;
  const access_info = parseJwt(access);
  store.commit("refreshToken", {
    access: access,
    accessExp: access_info.exp
  });
}

async function setProfile() {
  try {
    let response = await request.get(
      `${store.state.endpoints.baseUrl}/profile/`,
      {
        params: {
          userId: store.state.userId
        }
      }
    );
    if (response.data.length === 0) {
      router.push({ name: "ShopManage" }).catch(err => err);
    } else {
      const shops = [];
      for (let index = 0; index < response.data.length; index++) {
        const profile = response.data[index];
        const profileId = profile["profileId"];
        const countryCode = profile["countryCode"];
        const currencyCode = profile["currencyCode"];
        const dailyBudget = profile["dailyBudget"];
        const timezone = profile["timezone"];
        const accountInfo = profile["accountInfo"];
        const shopId = profile["shop"];
        const state = profile["state"];
        const marketplaceStringId = accountInfo["marketplaceStringId"];
        if (!delete accountInfo["marketplaceStringId"]) {
          throw new Error("无法删除:marketplaceStringId");
        }
        var idx = shops.findIndex(shop => shop.id === accountInfo["id"]);
        if (idx == -1) {
          accountInfo["profiles"] = [];
          accountInfo["shopId"] = shopId;
          shops.push(accountInfo);
          idx = shops.length - 1;
        }
        shops[idx]["profiles"].push({
          profileId: profileId,
          countryCode: countryCode,
          currencyCode: currencyCode,
          dailyBudget: dailyBudget,
          timezone: timezone,
          marketplaceStringId: marketplaceStringId,
          state: state
        });
      }
      store.commit("setProfiles", shops);
    }

    return response;
  } catch (error) {
    return error;
  }
}

export { saveToken, refreshToken, setProfile };
