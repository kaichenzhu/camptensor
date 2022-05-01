<template>
  <div>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="sku" label="SKU" width="250">
        <template slot-scope="scope">
          <el-select v-model="scope.row.sku" placeholder="选择待投放SKU">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="budget" label="预算" width="80">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.budget"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="defaultBid" label="广告组默认竞价" width="120">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.defaultBid"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="campaignType" label="广告类型" width="500">
        <template slot-scope="scope">
          <el-radio-group v-model="scope.row.campaignType">
            <el-radio label="auto">自动广告</el-radio>
            <el-radio label="keyword">手动广告(关键词)</el-radio>
            <el-radio label="product">手动广告(商品ASIN))</el-radio>
          </el-radio-group>
        </template>
      </el-table-column>
      <el-table-column prop="exact" label="精准匹配/ASIN" width="150">
        <template slot-scope="scope">
          <el-input
            v-if="
              scope.row.campaignType === 'keyword' ||
                scope.row.campaignType === 'product'
            "
            type="textarea"
            :rows="2"
            placeholder="多个关键词请转行"
            v-model="scope.row.exact"
          >
          </el-input>
        </template>
      </el-table-column>
      <el-table-column prop="phrase" label="词组匹配" width="150">
        <template slot-scope="scope">
          <el-input
            v-if="scope.row.campaignType === 'keyword'"
            type="textarea"
            :rows="2"
            placeholder="多个关键词请转行"
            v-model="scope.row.phrase"
          >
          </el-input>
        </template>
      </el-table-column>
      <el-table-column prop="broad" label="宽泛匹配" width="150">
        <template slot-scope="scope">
          <el-input
            v-if="scope.row.campaignType === 'keyword'"
            type="textarea"
            :rows="2"
            placeholder="多个关键词请转行"
            v-model="scope.row.broad"
          >
          </el-input>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="200">
        <template slot-scope="scope">
          <el-button
            @click.native.prevent="deleteRow(scope.$index)"
            type="danger"
            size="small"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="button-group">
      <el-button @click="addRow" type="primary">添加新的广告</el-button>
      <el-button @click="saveAll" type="primary">批量创建</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdReportQuick",
  data() {
    return {
      tableData: [],
      addCount: 0,
      options: []
    };
  },
  methods: {
    deleteRow(index) {
      this.tableData.splice(index, 1);
      if (this.addCount > 0) --this.addCount;
    },
    addRow: function() {
      var obj = {
        sku: "",
        budget: 10,
        defaultBid: 0.6,
        campaignType: "auto",
        exact: "",
        phrase: "",
        broad: ""
      };
      if (this.addCount > 0) {
        obj = this.tableData[this.tableData.length - 1];
      }
      const newRow = Object.assign({}, obj);
      this.tableData = [...this.tableData, newRow];
      ++this.addCount;
    },
    saveAll: function() {
      for (let index = 0; index < this.tableData.length; index++) {
        const element = this.tableData[index];
        if (
          element.sku === "" ||
          element.budget === "" ||
          element.defaultBid === "" ||
          element.campaignType === ""
        ) {
          this.$message.error("第" + (index + 1) + "行存在空值");
        } else if (
          typeof element.budget != "number" ||
          typeof element.defaultBid != "number"
        ) {
          this.$message.error("第" + (index + 1) + "行数值类型错误");
        }
      }
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/quickCreateCampaign`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          campaigns: this.tableData
        })
        .then(response => {
          this.options = response.data.sort((a, b) =>
            a.value.localeCompare(b.value)
          );
          this.$message({
            duration: 1000,
            message: "获取SKU成功",
            type: "success"
          });
        });
    },
    getSkus() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/productSku`, {
          params: {
            profileId: this.$store.state.current_profileId
          }
        })
        .then(response => {
          this.options = response.data.sort((a, b) =>
            a.value.localeCompare(b.value)
          );
          this.$message({
            duration: 1000,
            message: "获取SKU成功",
            type: "success"
          });
        });
    }
  },
  created: function() {
    this.getSkus();
  }
};
</script>
<style lang="">
.button-group {
  margin-top: 2em;
}
</style>
