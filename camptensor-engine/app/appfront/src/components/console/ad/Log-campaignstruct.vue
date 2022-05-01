<template>
  <el-table :data="tableData" style="width: 100%">
      <el-table-column property="changeLog" label="日志" min-width="90%" show-overflow-tooltip></el-table-column>
    </el-table>
</template>

<script>
  export default {
    name: 'AdLogCampaignStruct',
    data() {
      return {
        tableData: []
      }
    },
    methods: {
      getDate(date) {
        return date.substring(0, 4) + '-' + date.substring(4, 6) + '-' + date.substring(6);
      }
    },
    created: function () {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/campaignStructLog/`, {
        params: {
          profileId: this.$store.state.current_profileId,
          add_date_after: this.getDate(this.$store.state.start_date) + ' 0:00',
          add_date_before: this.getDate(this.$store.state.end_date) + ' 23:59',
          type: 'struct'
        }
      }).then(response => {
        if(response.data instanceof Array) {
          this.tableData = response.data;
        }
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      })
    }
  }

</script>
