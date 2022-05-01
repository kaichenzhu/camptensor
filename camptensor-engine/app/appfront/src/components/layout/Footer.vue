<template>
  <el-footer v-if="user">
      Copyright © 2020-2021 扬州天下汇科技有限公司 CAMPTENSOR.CN 版权所有
      <a href="https://beian.miit.gov.cn/" target="_blank">苏ICP备2021009489号</a>
    </el-footer
  >
</template>

<script>
export default {
  name: "Footer",
  computed: {
    user() {
      return this.$store.state.authUser;
    }
  }
};
</script>
