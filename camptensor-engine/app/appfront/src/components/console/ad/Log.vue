<template>
  <div>
    <h1>自动化日志</h1>
    <el-tabs v-model="activeName" @tab-click="handleClick">
      <el-row>
        <el-col :span="7"><DatePicker /></el-col>
        <el-col :span="1"
          ><el-button class="search" type="primary" @click="getData"
            >查询</el-button
          ></el-col
        >
      </el-row>
      <el-tab-pane label="关键词否定" name="negative" :lazy="true"
        ><AdLogNegative
      /></el-tab-pane>
      <el-tab-pane label="关键词优化" name="autotomanual" :lazy="true"
        ><AdLogAutotomanual
      /></el-tab-pane>
      <el-tab-pane label="竞价优化(周)" name="initbid" :lazy="true"
        ><AdInitBid
      /></el-tab-pane>
      <el-tab-pane label="实时竞价调整(4次/天)" name="bid" :lazy="true"
        ><AdLogBid
      /></el-tab-pane>
      <el-tab-pane label="广告调整" name="campaignStruct" :lazy="true"
        ><AdLogCampaignStruct
      /></el-tab-pane>
      <el-tab-pane label="广告预算优化" name="campaignBudget" :lazy="true"
        ><AdLogCampaignBudget
      /></el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
import AdLogNegative from "@/components/console/ad/Log-negative.vue";
import AdLogAutotomanual from "@/components/console/ad/Log-autotomanual.vue";
import AdInitBid from "@/components/console/ad/Log-initBid.vue";
import AdLogBid from "@/components/console/ad/Log-bid.vue";
import AdLogCampaignStruct from "@/components/console/ad/Log-campaignstruct.vue";
import AdLogCampaignBudget from "@/components/console/ad/Log-campaignBudget.vue";
import DatePicker from "@/components/util/Date-picker.vue";
export default {
  name: "AdReport",
  components: {
    AdLogNegative,
    AdLogAutotomanual,
    AdInitBid,
    AdLogBid,
    AdLogCampaignStruct,
    AdLogCampaignBudget,
    DatePicker
  },
  data() {
    return {
      activeName: "negative"
    };
  },
  computed: {
    start: {
      get() {
        return this.$store.state.start_date;
      },
      set(value) {
        this.$store.commit("setStartDate", value);
      }
    },
    end: {
      get() {
        return this.$store.state.end_date;
      },
      set(value) {
        this.$store.commit("setEndDate", value);
      }
    }
  },
  methods: {
    handleClick(tab, event) {
      console.log(tab, event);
    },
    getData() {
      this.$router.go(0);
    }
  }
};
</script>
