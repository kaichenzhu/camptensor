<template>
  <el-header>
    <div class="left">
      <el-radio-group v-if="user" v-model="isCollapse" style="margin-bottom: 20px;">
        <el-radio-button :label="false">展开</el-radio-button>
        <el-radio-button :label="true">收起</el-radio-button>
      </el-radio-group>
    </div>
    <div class="right">
      <ShopProfile v-if="shops" />
      <el-dropdown>
        <div v-if="user">
          <el-avatar :src="asset"></el-avatar>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="manageShop">店铺管理</el-dropdown-item>
            <!-- <el-dropdown-item @click.native="bindShop">绑定新店铺</el-dropdown-item> -->
            <el-dropdown-item @click.native="logout">退出</el-dropdown-item>
          </el-dropdown-menu>
        </div>
        <div v-else>
          <router-link to="/login">登录</router-link>
          <el-divider direction="vertical"></el-divider>
          <router-link to="/register">注册</router-link>
        </div>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script>
import ShopProfile from "@/components/layout/ShopProfile.vue";
export default {
  name: "Header",
  components: { ShopProfile },
  data() {
    return {
      asset: require("@/assets/man.png")
    };
  },
  computed: {
    user() {
      return this.$store.state.authUser;
    },
    shops() {
      return this.$store.state.shops;
    },
    isCollapse: {
      get() {
        return this.$store.state.navbar.isCollapse;
      },
      set(value) {
        this.$store.commit("navbarToggleFold", value);
      }
    }
  },
  methods: {
    logout() {
      this.$store.commit("removeUser");
      this.$router
        .push({
          name: "Login"
        })
        .catch(() => {});
    },
    bindShop() {
      this.$router
        .push({
          name: "Amzauth"
        })
        .catch(() => {});
    },
    manageShop() {
      this.$router
        .push({
          name: "ShopManage"
        })
        .catch(() => {});
    },
    toggelfold() {
      this.$store.commit("navbarToggleFold");
    }
  }
};
</script>

<style scoped>
.el-header {
  color: #222b45;
  box-shadow: none;
  height: 4.75rem;
  padding: 1.25rem;
}
.left {
  float: left;
}
.right {
  float: right;
}
</style>
