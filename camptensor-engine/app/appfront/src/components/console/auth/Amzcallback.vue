<template>
  <div>
    <!-- <el-button
      class="my-btn"
      ref="btn"
      type="success"
      @click="bind()"
      style="float:left; margin: 2px;"
      >绑定至当前账户</el-button
    > -->
    <a href="#" class="button7" style="background-color:#0074D9" @click.prevent="bind()">
      <span
        style="font-size:3em; font-family:'Comic Sans MS'; border-right:1px solid rgba(255,255,255,0.5); padding-right:0.3em; margin-right:0.3em; vertical-align:middle"
        >Amz</span
      >
      绑定亚马逊店铺至当前账户
    </a>
  </div>
</template>

<script>
export default {
  name: "Amzcallback",
  methods: {
    bind() {
      if (this.$route.query.code) {
        this.$request
          .get(`${this.$store.state.endpoints.baseUrl}/bind`, {
            params: {
              userId: this.$store.state.userId,
              code: this.$route.query.code,
              region: this.$store.state.region
            }
          })
          .then(response => {
            this.$message({
              duration: 1000,
              message: "绑定成功",
              type: "success"
            });
            this.$router
              .push({
                name: "ShopOverView"
              })
              .catch(() => {});
          });
      }
    }
  }
};
</script>

<style>
a.button7 {
  display: inline-block;
  padding: 0.7em 1.7em;
  margin: 0 0.3em 0.3em 0;
  border-radius: 0.2em;
  box-sizing: border-box;
  text-decoration: none;
  font-family: "Roboto", sans-serif;
  font-weight: 400;
  color: #ffffff;
  background-color: #3369ff;
  box-shadow: inset 0 -0.6em 1em -0.35em rgba(0, 0, 0, 0.17),
    inset 0 0.6em 2em -0.3em rgba(255, 255, 255, 0.15),
    inset 0 0 0em 0.05em rgba(255, 255, 255, 0.12);
  text-align: center;
  position: relative;
}
a.button7:active {
  box-shadow: inset 0 0.6em 2em -0.3em rgba(0, 0, 0, 0.15),
    inset 0 0 0em 0.05em rgba(255, 255, 255, 0.12);
}
@media all and (max-width: 30em) {
   a.button7 {
    display: block;
    margin: 0.4em auto;
  }
}
</style>
