<template>
  <el-table :data="tableData" style="width: 100%">
      <!-- <el-table-column property="add_date" label="时间" :formatter="formatDate" show-overflow-tooltip></el-table-column> -->
      <el-table-column property="changeLog" label="日志" min-width="90%" show-overflow-tooltip></el-table-column>
    </el-table>
</template>

<script>
  export default {
    name: 'AdLogBid',
    data() {
      return {
        tableData: []
      }
    },
    methods: {
      formatDate(row, column) {
          // 获取单元格数据
          let data = row[column.property]
          if(data == null) {
              return null
          }
          let dt = new Date(data)
          return dt.getFullYear() + '年' + (dt.getMonth() + 1) + '月' + dt.getDate() + '号' + dt.getHours() + ':' + (dt.getMinutes()).toString().padStart(2, '0');
      },
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
          type: 'dailybid'
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
