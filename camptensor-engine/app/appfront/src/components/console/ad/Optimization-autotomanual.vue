<template>
  <div>
    <el-button type="primary" @click="postData">确认优化</el-button>
    <el-table
      ref="multipleTable"
      row-key="id"
      :data="tableData.slice((currentPage-1)*pagesize,currentPage*pagesize)"
      :tree-props="{ children: 'children' }"
      style="width: 100%"
      @selection-change="handleTableSelectionChange"
    >
      <el-table-column type="selection" width="55" :selectable="checkSelectable"> </el-table-column>
      <el-table-column
        prop="skus"
        label="SKU"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="query"
        label="搜索词"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="campaignName"
        label="广告活动"
        show-overflow-tooltip
        :min-width="12"
      >
      </el-table-column>
      <el-table-column
        prop="adGroupName"
        label="广告组"
        show-overflow-tooltip
        :min-width="8"
      >
      </el-table-column>
      <el-table-column
        prop="adTarget"
        label="投放目标"
        show-overflow-tooltip
        :min-width="10"
      >
      </el-table-column>
      <el-table-column
        prop="clicks"
        label="点击"
        :min-width="5"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="orders"
        label="订单"
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
      <el-table-column
        prop="target"
        label="匹配类型"
        :min-width="20"
        show-overflow-tooltip
      >
        <template slot-scope="scope">
          <el-checkbox-group
            v-if="scope.row.matchType"
            v-model="scope.row.matchType"
          >
            <el-checkbox label="exact"></el-checkbox>
            <el-checkbox label="phrase"></el-checkbox>
            <el-checkbox label="broad"></el-checkbox>
          </el-checkbox-group>
        </template>
      </el-table-column>
      <el-table-column
        prop="bid"
        label="竞价"
        :min-width="5"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="target"
        label="目标"
        :min-width="20"
        show-overflow-tooltip
      >
        <template slot-scope="scope">
          <el-select
            v-if="scope.row.hasChild"
            placeholder="暂未创建手动广告"
            v-model="scope.row.currentTarget"
          >
            <el-option-group
              v-for="target in scope.row.target"
              :key="target.targetCampaignId"
              :label="target.targetCampaignName"
            >
              <el-option
                v-for="adGroup in target.adGroups"
                :key="adGroup.id"
                :label="adGroup.name"
                :value="adGroup.id"
              >
              </el-option>
            </el-option-group>
          </el-select>
        </template>
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
  name: "AdOptimizationAutotomanual",
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
    checkSelectable(row) {
      return row.hasChild
    },
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
    handleTableSelectionChange(val) {
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
            optimizeType: "optimize"
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
      console.log(this.multipleSelection);
      this.$request
        .post(
          `${this.$store.state.endpoints.baseUrl}/optimization-searchterm`,
          {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            optimizeType: "optimize",
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
