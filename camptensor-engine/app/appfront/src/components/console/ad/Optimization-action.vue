<template>
  <div>
    <el-row>
      <el-col :span="2" :offset="0">
        <el-button type="primary" @click="SynchronizeReports">同步</el-button>
      </el-col>
      <el-col :span="2" :offset="0">
        <el-input placeholder="开始日期" v-model="start"></el-input>
      </el-col>
      <el-col :span="1" :offset="0"> _ </el-col>
      <el-col :span="2" :offset="0">
        <el-input placeholder="截止日期" v-model="end"></el-input>
      </el-col>
      <el-col :span="3" :offset="0"> 天内广告报表数据 </el-col>
    </el-row>
    <el-row>
      <el-col :span="2" :offset="0">
        <el-button type="primary" @click="DataProcess">计算数据预处理</el-button>
      </el-col>
      <el-col :span="3" :offset="0"> 时间戳: </el-col>
      <el-col :span="2" :offset="0">
        <el-input placeholder="截止日期" v-model="pilot"></el-input>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="2" :offset="0">
        <el-button type="primary" @click="Optimize('searchtermOpt')">关键词优化</el-button>
      </el-col>
      <el-col :span="2" :offset="1">
        <el-button type="primary" @click="Optimize('bidinit')">关键词竞价优化(每周)</el-button>
      </el-col>
      <el-col :span="2" :offset="1">
        <el-button type="primary" @click="DailyBid">关键词竞价实时优化(每天4次)</el-button>
      </el-col>
      <el-col :span="2" :offset="1">
        <el-button type="primary" @click="UpdateCampaignBudget">广告预算调整</el-button>
      </el-col>
      <el-col :span="2" :offset="1">
        <el-button type="primary" @click="Optimize('wordRecommend')">关键词推荐</el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="2" :offset="0">
        <el-button type="primary" @click="change">修改db</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'AdOptimizationAction',
  data () {
    return {
      start: 20210312,
      end: 20210312,
      pilot: 20210312
    }
  },
  methods: {
    SynchronizeReports () {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/synchronizeReport`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          start: this.start,
          end: this.end
        }
      }).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "同步历史广告报表成功",
          type: "success"
        });
      })
    },
    DailyBid() {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/dailyBid`).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "更新竞价成功",
          type: "success"
        });
      })
    },
    UpdateCampaignBudget() {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/updateCampaignBudget`).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "更新广告预算成功",
          type: "success"
        });
      })
    },
    Optimize (optType) {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/optimize`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          optType: optType
        }
      }).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "同步历史广告报表成功",
          type: "success"
        });
      })
    },
    DataProcess () {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/dataProcess`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          pilot: this.pilot
        }
      }).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "同步历史广告报表成功",
          type: "success"
        });
      })
    },
    change () {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/change`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          profileId: this.$store.state.current_profileId
        }
      }).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "同步历史广告报表成功",
          type: "success"
        });
      })
    }
  },
}
</script>

<style>
.el-row {
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap
  }

</style>