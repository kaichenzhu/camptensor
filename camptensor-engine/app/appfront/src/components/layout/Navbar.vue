<template>
  <el-aside width="200px" v-if="user">
    <el-menu
      default-active="/console/ad/detail"
      class="el-menu-vertical-demo"
      router
      @open="handleOpen"
      @close="handleClose"
      :collapse="isCollapse"
    >
      <el-submenu index="/console/shop/overview">
        <template slot="title">
          <i class="el-icon-menu"></i>
          <span slot="title">商品管理</span>
        </template>
        <el-menu-item index="/console/shop/overview">销售总览</el-menu-item>
        <el-menu-item index="/console/shop/product">产品信息</el-menu-item>
        <el-menu-item index="/console/shop/status">产品状态</el-menu-item>
      </el-submenu>
      <el-submenu index="/console/ad/overview">
        <template slot="title">
          <i class="el-icon-s-operation"></i>
          <span slot="title">广告管理</span>
        </template>
        <el-menu-item index="/console/ad/overview">广告总览</el-menu-item>
        <el-menu-item index="/console/ad/report">广告活动</el-menu-item>
        <el-menu-item index="/console/ad/detail">广告明细</el-menu-item>
        <el-menu-item index="/console/ad/optimization">关键词优化</el-menu-item>
        <el-menu-item index="/console/ad/log">自动化日志</el-menu-item>
      </el-submenu>
      <el-submenu index="/console/anls/sale">
        <template slot="title">
          <i class="el-icon-s-opportunity"></i>
          <span slot="title">商业洞察</span>
        </template>
        <el-menu-item index="/console/anls/sale">销售分析</el-menu-item>
        <el-menu-item index="/console/anls/ad">广告分析</el-menu-item>
      </el-submenu>
    </el-menu>
  </el-aside>
</template>

<script>
export default {
  name: "Navbar",
  computed: {
    isCollapse() {
      return this.$store.state.navbar.isCollapse;
    },
    user() {
      return this.$store.state.authUser;
    }
  },
  methods: {
    handleOpen(key, keyPath) {
      console.log(key, keyPath);
    },
    handleClose(key, keyPath) {
      console.log(key, keyPath);
    }
  }
};
</script>

<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}
.el-menu {
  border-right: none;
}
</style>
