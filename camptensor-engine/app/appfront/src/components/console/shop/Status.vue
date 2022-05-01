<template>
  <div>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column
        property="countryCode"
        label="站点"
        width="50"
      ></el-table-column>
      <el-table-column property="sku" label="SKU" width="180"></el-table-column>
      <el-table-column
        property="asin"
        label="ASIN"
        width="150"
      ></el-table-column>
      <el-table-column
        property="price"
        label="价格"
        width="80"
      ></el-table-column>
      <el-table-column label="利润空间" width="120">
        <template slot-scope="scope">
          <el-progress :percentage="scope.row.macs"></el-progress>
        </template>
      </el-table-column>
      <el-table-column label="推广指数" width="180">
        <template slot-scope="scope">
          <el-progress
            v-if="[2, 3, 4, 5].includes(scope.row.state)"
            type="circle"
            :percentage="scope.row.percentage"
            :format="format"
            :color="scope.row.color"
            :width="40"
          ></el-progress>
        </template>
      </el-table-column>
      <el-table-column label="广告状态" width="200">
        <template slot-scope="scope">
          <span v-if="scope.row.state == 0">店铺历史数据获取中...</span>
          <span v-if="scope.row.note != null">{{
            scope.row.note
          }}</span>
        </template>
      </el-table-column>
      <el-table-column label="推广目标" width="200">
        <template slot-scope="scope">
          <el-switch
            v-if="[4, 5].includes(scope.row.state)"
            v-model="scope.row.state"
            :active-value="5"
            :inactive-value="4"
            active-color="#13ce66"
            inactive-color="#ff4949"
            active-text="利润率"
            inactive-text="销量"
            @change="controlSwitch($event, scope.$index)"
          >
          </el-switch>
          <el-popover
            v-if="[2, 3].includes(scope.row.state)"
            placement="top-start"
            title="注意"
            width="200"
            trigger="hover"
            content="请确保该SKU绑定的广告活动开启, 否则无法收集到有效数据"
          >
            <el-button
              slot="reference"
              @click.native.prevent="startTest(scope.row)"
              type="primary"
              size="small"
            >
              测试
            </el-button>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="广告操作" width="200">
        <template slot-scope="scope">
          <el-button
            @click.native.prevent="pauseAds(scope.row)"
            type="danger"
            size="small"
          >
            全部暂停
          </el-button>
          <el-button
            @click.native.prevent="startAds(scope.row)"
            type="success"
            size="small"
          >
            全部开启
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "ShopStatus",
  data() {
    return {
      tableData: [],
      addCount: 0,
      rateColor: ["#f71e1e", "#ebe234", "#34eb4c"]
    };
  },
  methods: {
    format(percentage) {
      return percentage / 10;
    },
    controlSwitch(val, index) {
      var new_val = this.tableData[index];
      new_val.state = val;
      this.tableData.splice(index, 1, new_val);
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/changeProductTarget`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            sku: new_val.sku,
            state: val
          }
        })
        .then(response => {
          this.$message({
            duration: 1000,
            message: "改变优化目标",
            type: "success"
          });
        });
    },
    toPercent(point) {
      var str = Number(point * 100).toFixed(2);
      str += "%";
      return str;
    },
    startTest(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/startTest`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          product: row
        })
        .then(response => {
          if (response.data == "success") {
            row.state = 1;
            row.note = "测试中...";
          }
          this.$message({
            duration: 1000,
            message: "开始测试",
            type: "success"
          });
        });
    },
    startAds(row) {
      var sku = row.sku;
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/startAds`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            sku: sku
          }
        })
        .then(response => {
          if (response.data == "success") {
            this.$message({
              duration: 1000,
              message: "广告全部开启",
              type: "success"
            });
          }
        });
    },
    pauseAds(row) {
      var sku = row.sku;
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/pauseAds`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            sku: sku
          }
        })
        .then(response => {
          if (response.data == "success") {
            this.$message({
              duration: 1000,
              message: "已全部暂停",
              type: "success"
            });
          }
        });
    }
  },
  created: function() {
    this.$request
      .get(`${this.$store.state.endpoints.baseUrl}/getProductsStatus`, {
        params: {
          profileId: this.$store.state.current_profileId
        }
      })
      .then(response => {
        if (response.data instanceof Array) {
          this.tableData = response.data;
          this.tableData.forEach(element => {
            element.macs = parseInt(parseFloat(element.macs) * 100);
            if ([2, 3, 4, 5].includes(element.state)) {
              element.percentage = parseInt(parseFloat(element.point) * 10);
              element.color = this.rateColor[
                parseInt(parseFloat(element.point) / 4)
              ];
            }
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
.button-group {
  margin-top: 2em;
}
</style>
