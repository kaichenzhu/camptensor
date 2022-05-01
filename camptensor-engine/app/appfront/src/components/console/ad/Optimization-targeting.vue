<template>
  <div>
    <!-- <el-button type="primary" @click="getData">获取数据</el-button> -->
    <el-button type="primary" @click="postData">确认暂停</el-button>
    <el-table
      ref="multipleTable"
      :data="tableData"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"> </el-table-column>
      <div v-if="id_show">
        <el-table-column property="campaignId" label="campaignId" show-overflow-tooltip>
        </el-table-column>
        <el-table-column property="adGroupId" label="adGroupId" show-overflow-tooltip>
        </el-table-column>
        <el-table-column property="targetId" label="targetId" show-overflow-tooltip>
        </el-table-column>
        <el-table-column property="type" label="type" show-overflow-tooltip>
        </el-table-column>
      </div>
      <el-table-column property="targetName" label="目标" show-overflow-tooltip>
      </el-table-column>
      <el-table-column
        property="targetType"
        label="目标类型"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="campaignName"
        label="广告活动"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column
        property="adGroupName"
        label="广告组"
        show-overflow-tooltip
      >
      </el-table-column>
      <el-table-column property="clicks" label="点击" show-overflow-tooltip>
      </el-table-column>
      <el-table-column property="orders" label="订单" show-overflow-tooltip>
      </el-table-column>
      <el-table-column property="spends" label="花费"  :formatter="handelFix" show-overflow-tooltip>
      </el-table-column>
      <el-table-column property="sales" label="销售额" show-overflow-tooltip>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'AdOptimizationTargeting',
  data () {
    return {
      tableData: [],
      multipleSelection: [],
      id_show: false
    }
  },
  created() {
    this.getData();
  },
  methods: {
    handelFix(row, column){
        return row[column.property].toFixed(2)
    },
    toggleSelection (rows) {
      if (rows) {
        rows.forEach(row => {
          this.$refs.multipleTable.toggleRowSelection(row);
        });
      } else {
        this.$refs.multipleTable.clearSelection();
      }
    },
    handleSelectionChange (val) {
      this.multipleSelection = val;
    },
    getData () {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/optimization-targeting`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          profileId: this.$store.state.current_profileId
        }
      }).then(response => {
        this.tableData = response.data;
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      })
    },
    postData () {
      this.$request.post(`${this.$store.state.endpoints.baseUrl}/optimization-targeting`, {
        shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
        profileId: this.$store.state.current_profileId,
        optimizeType: 'negative',
        targetings: this.multipleSelection
      }).then(response => {
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      })
    }
  }
}
</script>
