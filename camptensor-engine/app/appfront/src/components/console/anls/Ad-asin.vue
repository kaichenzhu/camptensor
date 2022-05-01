<template>
  <div>
    <div class="sort">
      <el-radio-group v-model="sort_col">
        <el-radio-button label="impressions">曝光</el-radio-button>
        <el-radio-button label="clicks">点击</el-radio-button>
        <el-radio-button label="orders">订单量</el-radio-button>
        <el-radio-button label="cost">花费</el-radio-button>
        <el-radio-button label="sales">销售额</el-radio-button>
        <el-radio-button label="ctr">点击率</el-radio-button>
        <el-radio-button label="cvr">转化率</el-radio-button>
        <el-radio-button label="acos">ACOS</el-radio-button>
      </el-radio-group>
      <el-radio-group v-model="reverse">
        <el-radio-button label="0"><i class="el-icon-caret-top"></i></el-radio-button>
        <el-radio-button label="1"><i class="el-icon-caret-bottom"></i></el-radio-button>
      </el-radio-group>
      <el-button type="primary" @click="getData">获取数据</el-button>
    </div>
    <el-table
      row-key="id"
      :data="tableData"
      :tree-props="{ children: 'children' }"
      style="width: 100%"
    >
      <el-table-column
        prop="searchterm"
        label="SKU-关键词"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="impressions"
        label="曝光"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="clicks"
        label="点击"
        show-overflow-tooltip
        :min-width="12"
      >
      </el-table-column>
      <el-table-column
        prop="orders"
        label="订单量"
        show-overflow-tooltip
        :min-width="8"
      >
      </el-table-column>
      <el-table-column
        prop="ctr"
        label="点击率"
        show-overflow-tooltip
        :min-width="10"
      >
      </el-table-column>
      <el-table-column
        prop="cvr"
        label="转化率"
        :min-width="5"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="acos"
        label="ACOS"
        :min-width="5"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="cost"
        label="花费"
        show-overflow-tooltip
        :min-width="5"
      >
      </el-table-column>
      <el-table-column
        prop="sales"
        label="销售额"
        :min-width="5"
        show-overflow-tooltip
      >
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "AdASIN",
  data() {
    return {
      tableData: [],
      sort_col: 'orders',
      reverse: 1
    };
  },
  created() {
    this.getData();
  },
  methods: {
    toPercent (point) {
      var str=Number(point*100).toFixed(2);
      str+="%";
      return str;
    },
    processElement(e) {
      e.forEach(element => {
        element.cost=Number(element.cost).toFixed(2);
        element.sales=Number(element.sales).toFixed(2);
        element.ctr=this.toPercent(element.clicks/element.impressions);
        element.cvr=this.toPercent(element.orders/element.clicks);
        element.acos=this.toPercent(element.cost/element.sales);
      });
    },
    getData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/searchtermReport`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            searchtermType: 'asin',
            sort_col: this.sort_col,
            reverse: this.reverse
          }
        })
        .then(response => {
          this.tableData = response.data;
          this.tableData.forEach(element => {
            this.processElement(element.children)
          });
          this.$message({
            duration: 1000,
            message: "获取数据成功",
            type: "success"
          });
        });
    }
  }
};
</script>

<style lang="">
  .sort {
    text-align: left
  }
</style>