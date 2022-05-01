<template>
  <div>
    <!-- <el-button type="primary" @click="getData">获取数据</el-button> -->
    <el-button type="primary" @click="postData">确认否定</el-button>
    <el-table
      ref="multipleTable"
      :data="tableData.slice((currentPage-1)*pagesize,currentPage*pagesize)"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" :min-width="5"> </el-table-column>
      <div v-if="id_show">
        <el-table-column
          property="campaignId"
          label="campaignId"
          show-overflow-tooltip
        >
        </el-table-column>
        <el-table-column
          property="adGroupId"
          label="adGroupId"
          show-overflow-tooltip
        >
        </el-table-column>
        <el-table-column
          property="targetId"
          label="targetId"
          show-overflow-tooltip
        >
        </el-table-column>
        <el-table-column property="type" label="type" show-overflow-tooltip>
        </el-table-column>
      </div>
      <el-table-column
        property="query"
        sortable
        :min-width="12"
        label="搜索词"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="campaignName"
        label="广告活动"
        show-overflow-tooltip
        :min-width="23"
      >
      </el-table-column>
      <el-table-column
        property="adGroupName"
        label="广告组"
        show-overflow-tooltip
        :min-width="16"
      ></el-table-column>
      <el-table-column
        property="adTarget"
        label="投放目标"
        show-overflow-tooltip
        :min-width="12"
      ></el-table-column>
      <el-table-column
        property="clicks"
        :min-width="7"
        label="点击"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="orders"
        :min-width="7"
        label="订单"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="spends"
        :min-width="7"
        label="花费"
        :formatter="handelFix"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="sales"
        :min-width="7"
        label="销售额"
        show-overflow-tooltip
      >
      </el-table-column>
    </el-table>
    <el-pagination
      background
      layout="prev, pager, next, jumper"
      :total="total"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-size="pagesize"
    >
    </el-pagination>
  </div>
</template>

<script>
export default {
  name: "AdOptimizationNegative",
  data() {
    return {
      tableData: [],
      multipleSelection: [],
      id_show: false,
      pagesize: 30,
      currentPage: 1,
      total: 0
    };
  },
  created() {
    this.getData();
  },
  methods: {
    handelFix(row, column) {
      return row[column.property].toFixed(2);
    },
    toggleSelection(rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },
    handleSizeChange(val) {
        this.pagesize =val;
    },
    handleCurrentChange(val) {
      this.currentPage = val;
    },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    getData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/optimization-searchterm`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            optimizeType: "negative"
          }
        })
        .then(response => {
          this.tableData = response.data;
          this.total = this.tableData.length;
          this.$message({
            duration: 1000,
            message: "获取数据成功",
            type: "success"
          });
        });
    },
    postData() {
      this.$request
        .post(
          `${this.$store.state.endpoints.baseUrl}/optimization-searchterm`,
          {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            optimizeType: "negative",
            searchterms: this.multipleSelection
          }
        )
        .then(response => {
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
