<template>
  <div>
    <el-row>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="shopId, split by comma"
          v-model="shopIds"
        >
        </el-input>
      </el-col>
      <el-col :span="4">
        <el-input placeholder="Please input" v-model="days1"></el-input>
      </el-col>
      <el-col :span="4">
        <el-button
          @click.native.prevent="getShopData"
          type="primary"
          size="small"
        >
          更新店铺数据
        </el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="profileId, split by comma"
          v-model="profileIds"
        >
        </el-input>
      </el-col>
      <el-col :span="4">
        <el-input placeholder="Please input" v-model="days2"></el-input
      ></el-col>
      <el-col :span="4">
        <el-button
          @click.native.prevent="getProfileData"
          type="primary"
          size="small"
        >
          更新店铺站点数据
        </el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-button @click.native.prevent="custom" type="primary" size="small">
        自定义功能
      </el-button>
    </el-row>
    <el-row>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="账号名"
          v-model="account"
        ></el-input>
      </el-col>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="超级密码"
          v-model="password"
        ></el-input>
      </el-col>
      <el-col :span="4">
        <el-button
          @click.native.prevent="getAccountInfo"
          type="primary"
          size="small"
        >
          获取账号信息
        </el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="起始账期"
          v-model="start_bill"
        ></el-input>
      </el-col>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="结束账期"
          v-model="end_bill"
        ></el-input>
      </el-col>
      <el-col :span="4">
        <el-button
          @click.native.prevent="getBill"
          type="primary"
          size="small"
        >
          获取账单
        </el-button>
      </el-col>
      <el-col :span="4">
        <el-input
          type="textarea"
          :rows="2"
          placeholder="费用那个"
          v-model="bill"
        ></el-input>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "test",
  data() {
    return {
      shopIds: "",
      profileIds: "",
      days1: 0,
      days2: 0,
      account: "",
      password: "",
      start_bill: "",
      end_bill: "",
      bill: ""
    };
  },
  methods: {
    getShopData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/getShopData`, {
          params: {
            shopIds: this.shopIds,
            day: this.days1,
          },
        })
        .then((response) => {
          this.$message({
            duration: 1000,
            message: "获取数据成功",
            type: "success",
          });
        });
    },
    getProfileData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/getProfileData`, {
          params: {
            profileIds: this.profileIds,
            day: this.days2,
          },
        })
        .then((response) => {
          this.$message({
            duration: 1000,
            message: "获取数据成功",
            type: "success",
          });
        });
    },
    custom() {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/custom`);
    },
    getAccountInfo() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/getAccountInfo`, {
          params: {
            account: this.account,
            password: this.password,
          },
        })
        .then((response) => {
          this.password = response.data;
        });
    },
    getBill() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/getBill`, {
          params: {
            profileId: this.$store.state.current_profileId,
            startBill: this.start_bill,
            endBill: this.end_bill,
          },
        })
        .then((response) => {
          this.bill = response.data;
        });
    }
  },
};
</script>

<style></style>
