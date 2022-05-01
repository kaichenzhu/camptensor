<template>
  <div>
    <a
      class="btn"
      href="https://www.amazon.com/ap/oa?client_id=amzn1.application-oa2-client.641aeab8c0c6436c819098e6af5ea8fc&scope=advertising::campaign_management&response_type=code&redirect_uri=https://www.camptensor.cn/console/callback"
      >前往亚马逊授权</a
    >
  </div>
</template>

<script>
export default {
  name: "Amzauth"
};
</script>

<style>
.btn {
  -webkit-border-radius: 12;
  -moz-border-radius: 12;
  border-radius: 12px;
  font-family: Arial;
  color: #fff;
  font-size: 20px;
  background: #36f;
  padding: 10px 40px 10px 40px;
  text-decoration: none;
}

.btn:hover {
  background: #66b1ff;
  text-decoration: none;
}
</style>
