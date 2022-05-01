<template>
  <el-table :data="tableData" style="width: 100%" height="250">
    <el-table-column fixed prop="countryCode" label="地区码" width="150">
    </el-table-column>
    <el-table-column prop="dailyBudget" label="每日预算" width="120">
    </el-table-column>
    <el-table-column prop="currencyCode" label="币种" width="120">
    </el-table-column>
    <el-table-column prop="timezone" label="时区" width="120">
    </el-table-column>
    <el-table-column prop="marketplaceStringId" label="市场码" width="120">
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  name: 'ShopOverView',
  data() {
    return {
      tableData: []
    }
  },
  mounted() {
    this.initData()
  },
  methods: {
    initData() {
      this.tableData = this.$store.state.shops[this.$store.state.current_shop_idx]['profiles'];
    }
  }
}

</script>
