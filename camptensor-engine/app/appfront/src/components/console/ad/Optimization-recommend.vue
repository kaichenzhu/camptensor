<template>
  <div>
    <el-button type="primary" @click="postData">确认投放</el-button>
    <el-table
      ref="multipleTable"
      :data="tableData.slice((currentPage-1)*pagesize,currentPage*pagesize)"
      style="width: 100%"
      @selection-change="handleTableSelectionChange"
    >
      <el-table-column type="selection" width="55"> </el-table-column>
      <el-table-column
        prop="sku"
        label="SKU"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="phrase"
        label="关键词"
        :min-width="15"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        prop="point"
        sortable
        label="推荐指数"
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
  name: "AdOptimizationRecommend",
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
    handleSizeChange(val) {
        this.pagesize =val;
    },
    handleCurrentChange(val) {
      this.currentPage = val;
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
    handleTableSelectionChange(val) {
      this.multipleSelection = val;
    },
    getData() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/optimization-recommend`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
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
          `${this.$store.state.endpoints.baseUrl}/optimization-recommend`,
          {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
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
