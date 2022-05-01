<template>
  <div>
    <!-- <el-button type="primary" @click="postData">确认优化</el-button>
    <el-table
      row-key="id"
      :data="tableData"
      :tree-props="{ children: 'children' }"
      style="width: 100%"
    >
      <el-table-column
        prop="sku"
        label="SKU"
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
        :formatter="handelFix"
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
    </el-table> -->
  </div>
</template>

<script>
export default {
  name: "AdCampaign",
  data() {
    return {
      tableData: []
    };
  },
  created() {
    // this.getData();
  },
  methods: {
    handelFix(row, column) {
      return row[column.property].toFixed(2);
    },
    getData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/searchtermReport`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            searchtermType: 'keyword'
          }
        })
        .then(response => {
          this.tableData = response.data;
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
