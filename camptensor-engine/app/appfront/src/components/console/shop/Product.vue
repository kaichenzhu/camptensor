<template>
  <div>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column
        property="countryCode"
        label="站点"
        width="50"
      ></el-table-column>
      <el-table-column prop="sku" label="SKU" width="250">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.sku"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="asin" label="ASIN" width="150">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.asin"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="100">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.price"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="macs" label="利润空间" width="100">
        <template slot-scope="scope">
          <el-input
            size="small"
            style="text-align: center"
            v-model.trim="scope.row.macs"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="200">
        <template slot-scope="scope">
          <el-button
            @click.native.prevent="saveRow(scope.row)"
            type="success"
            size="small"
          >
            保存
          </el-button>
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
      <el-button @click="addRow" type="primary">添加产品</el-button>
      <el-button @click="saveAll" type="primary">批量保存</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ShopProduct",
  data() {
    return {
      tableData: [],
      addCount: 0
    };
  },
  methods: {
    toPercent(point) {
      var str = Number(point * 100).toFixed(2);
      str += "%";
      return str;
    },
    deleteRow(index) {
      if (this.tableData[index]["id"]) {
        this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/deleteProduct`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
            profileId: this.$store.state.current_profileId,
            id: this.tableData[index]["id"]
          }
        }).then(response => {
          this.$message({
            duration: 1000,
            message: "删除商品成功",
            type: "success"
          });
        });
      }
      this.tableData.splice(index, 1);
      if (this.addCount > 0) --this.addCount;
    },
    saveRow(row) {
      this.saveData([row])
    },
    saveData(productList) {
      this.$request.post(`${this.$store.state.endpoints.baseUrl}/shopProductsList`, {
        shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
        profileId: this.$store.state.current_profileId,
        productList: productList
      }).then(response => {
        this.$message({
          duration: 1000,
          message: "保存成功",
          type: "success"
        });
      });
    },
    addRow: function() {
      let shops = this.$store.state.shops;
      let current_shop_idx = this.$store.state.current_shop_idx;
      let current_profile_idx = this.$store.state.current_profile_idx;
      let newRow = {
        countryCode:
          shops[current_shop_idx]["profiles"][current_profile_idx][
            "countryCode"
          ],
        currencyCode:
          shops[current_shop_idx]["profiles"][current_profile_idx][
            "currencyCode"
          ],
        profileId: this.$store.state.current_profileId,
        sku: "",
        asin: "",
        price: 0,
        macs: 0
      };
      this.tableData = [...this.tableData, newRow];
      ++this.addCount;
      console.log(this.addCount);
    },
    saveAll: function() {
      var tempSet = new Set();
      var pushData = []
      for (let index = 0; index < this.tableData.length; index++) {
        const element = this.tableData[index];
        const sku = element.sku;
        if (tempSet.has(sku)) continue;
        tempSet.add(sku);
        pushData.push(element)
      }
      this.tableData = pushData;
      this.saveData(this.tableData);
    }
  },
  created: function() {
    let shops = this.$store.state.shops;
    let current_shop_idx = this.$store.state.current_shop_idx;
    let current_profile_idx = this.$store.state.current_profile_idx;
    this.$request
      .get(`${this.$store.state.endpoints.baseUrl}/shopProducts/`, {
        params: {
          profileId: this.$store.state.current_profileId,
          countryCode:
            shops[current_shop_idx]["profiles"][current_profile_idx][
              "countryCode"
            ]
        }
      })
      .then(response => {
        if (response.data instanceof Array) {
          this.tableData = response.data;
          this.tableData.forEach(element => {
            element.macs = this.toPercent(element.macs);
          });
        }
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      });
  }
};
</script>
<style lang="">
  .button-group{
    margin-top: 2em;
  }
</style>