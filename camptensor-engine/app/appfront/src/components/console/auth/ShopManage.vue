<template>
  <div>
    <div v-if="hasData">
      <el-table :data="tableData" style="width: 100%">
        <el-table-column type="expand">
          <template slot-scope="scope">
            <el-table :data="scope.row.profiles" style="width: 100%">
              <el-table-column
                prop="profileId"
                label="店铺ID"
                width="180"
              ></el-table-column>
              <el-table-column
                prop="countryCode"
                label="地区"
                width="180"
              ></el-table-column>
              <el-table-column
                prop="currencyCode"
                label="币种"
                width="180"
              ></el-table-column>
              <el-table-column label="状态" width="180">
                <template slot-scope="scope">
                  <el-switch
                    v-model="scope.row.state"
                    active-text="开始"
                    inactive-text="停止"
                    @change="controlSwitch(scope.row)"
                  >
                  </el-switch>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-table-column>
        <el-table-column label="账户ID" prop="id"> </el-table-column>
        <el-table-column label="账户名称" prop="name"> </el-table-column>
      </el-table>
    </div>
    <div v-else>
      <span>暂无店铺绑定该账号</span>
    </div>
    <el-divider></el-divider>
    <el-row>
      <el-col :span="6" :offset="6">
        <span>*选择大区:  </span>
        <el-radio-group v-model="region">
          <el-radio-button label="NA">北美大区</el-radio-button>
          <el-radio-button label="EU">欧洲大区</el-radio-button>
          <el-radio-button label="FE">亚太大区</el-radio-button>
        </el-radio-group>
      </el-col>
      <el-col :span="4" :offset="0">
        <a
          v-if="region == 'NA'"
          class="btn"
          href="https://www.amazon.com/ap/oa?client_id=amzn1.application-oa2-client.641aeab8c0c6436c819098e6af5ea8fc&scope=advertising::campaign_management&response_type=code&redirect_uri=https://www.camptensor.cn/console/callback"
          >开始授权</a
        >
        <a
          v-if="region == 'EU'"
          class="btn"
          href="https://eu.account.amazon.com/ap/oa?client_id=amzn1.application-oa2-client.641aeab8c0c6436c819098e6af5ea8fc&scope=advertising::campaign_management&response_type=code&redirect_uri=https://www.camptensor.cn/console/callback"
          >开始授权</a
        >
        <a
          v-if="region == 'FE'"
          class="btn"
          href="https://apac.account.amazon.com/ap/oa?client_id=amzn1.application-oa2-client.641aeab8c0c6436c819098e6af5ea8fc&scope=advertising::campaign_management&response_type=code&redirect_uri=https://www.camptensor.cn/console/callback"
          >开始授权</a
        >
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "ShopManage",
  data() {
    return {
      tableData: [],
      hasData: false
    };
  },
  computed: {
    region: {
      get() {
        return this.$store.state.region
      },
      set(value) {
        this.$store.commit("setRegion", value);
      }
    }
  },
  created() {
    this.initData();
  },
  methods: {
    getIdx(profileId) {
      for (let i = 0; i < this.tableData.length; i++) {
        const element = this.tableData[i];
        for (let j = 0; j < element.profiles.length; j++) {
          const e = element.profiles[j];
          if (e.profileId == profileId) {
            return [i, j];
          }
        }
      }
      return [-1, -1];
    },
    controlSwitch(row) {
      let index = this.getIdx(row.profileId);
      let shopIdx = index[0];
      let profileIdx = index[1];
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/changeProfileState`, {
          params: {
            profileId: row.profileId,
            state: row.state
          }
        })
        .then(response => {
          this.$message({
            duration: 1000,
            message: "修改成功",
            type: "success"
          });
          this.$store.commit("refreshProfileState", {
            shopIdx: shopIdx,
            profileIdx: profileIdx,
            newState: row.state
          });
        });
    },
    initData() {
      this.tableData = this.$store.state.shops;
      if (this.tableData && this.tableData.length > 0) {
        this.hasData = true;
        this.tableData.forEach(element => {
          element.profiles.forEach(e => {
            e.state = e.state == 1 ? true : false;
          });
        });
      }
    }
  }
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
