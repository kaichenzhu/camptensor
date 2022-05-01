<template>
  <div>
    <el-row>
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item
          style="cursor: pointer;"
          v-if="dataType != 'sku'"
          @click.native="handleClcik('sku')"
          >全部商品</el-breadcrumb-item
        >
        <el-breadcrumb-item
          style="cursor: pointer;"
          v-if="sku.length > 0"
          @click.native="handleClcik('campaign')"
          >{{ sku }}</el-breadcrumb-item
        >
        <el-breadcrumb-item
          style="cursor: pointer;"
          v-if="campaignName.length > 0"
          @click.native="handleClcik('adgroup')"
          >{{ campaignName }}</el-breadcrumb-item
        >
        <el-breadcrumb-item
          style="cursor: pointer;"
          v-if="adGroupName.length > 0"
          >{{ adGroupName }}</el-breadcrumb-item
        >
      </el-breadcrumb>
    </el-row>
    <el-row>
      <DatePicker />
      <el-col :span="5">
        <el-checkbox-group
          class="my-checkbox"
          v-model="promotionTarget"
          v-if="dataType == 'sku'"
        >
          <el-checkbox
            v-for="item in options"
            :key="item.value"
            :label="item.value"
            >{{ item.label }}</el-checkbox
          >
        </el-checkbox-group>
      </el-col>
      <el-button class="search" type="primary" @click="getData">查询</el-button>
    </el-row>
    <el-row :gutter="27">
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(0)"
          v-bind:style="[cardSelected.indexOf(0) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          曝光: {{ this.impressions }}
        </el-card>
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(1)"
          v-bind:style="[cardSelected.indexOf(1) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          点击: {{ this.clicks }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(2)"
          v-bind:style="[cardSelected.indexOf(2) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          订单: {{ this.orders }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(3)"
          v-bind:style="[cardSelected.indexOf(3) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          花费: {{ this.cost }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(4)"
          v-bind:style="[cardSelected.indexOf(4) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          收入: {{ this.sales }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(5)"
          v-bind:style="[cardSelected.indexOf(5) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          点击率: {{ this.CTR }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(6)"
          v-bind:style="[cardSelected.indexOf(6) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          转化率: {{ this.CVR }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(7)"
          v-bind:style="[cardSelected.indexOf(7) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          ACOS: {{ this.ACOS }}</el-card
        >
      </el-col>
      <el-col :span="3">
        <el-card
          shadow="hover"
          style="cursor: pointer;"
          @click.native="selectCard(8)"
          v-bind:style="[cardSelected.indexOf(8) != -1 ? {'borderStyle': 'solid', 'borderWidth': 'medium', 'borderColor': '#6f93ff'} : {}]"
        >
          CPC: {{ this.CPC }}</el-card
        >
      </el-col>
    </el-row>
    <div id="detail-line-chart" style="width: 1600px;height:400px;" />
    <el-table :data="datatree" :cell-style="cellcolor">
      <el-table-column width="250" label="名称" border>
        <template slot-scope="scope">
          <span
            v-show="!scope.row.show"
            style="cursor: pointer;"
            @click="rowClick(scope.row)"
            >{{ scope.row.name }}</span
          >
        </template>
      </el-table-column>
      <el-table-column label="状态" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.state }}</span>
        </template>
      </el-table-column>
      <el-table-column label="曝光" prop="impressions" sortable border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.impressions }}</span>
        </template>
      </el-table-column>
      <el-table-column label="点击" prop="clicks" sortable border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.clicks }}</span>
        </template>
      </el-table-column>
      <el-table-column label="订单" prop="orders" sortable border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.orders }}</span>
        </template>
      </el-table-column>
      <el-table-column label="花费" sortable :sort-method="(a, b) => sortNum(a, b, 'cost')" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.cost }}</span>
        </template>
      </el-table-column>
      <el-table-column label="收入" sortable :sort-method="(a, b) => sortNum(a, b, 'sales')" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.sales }}</span>
        </template>
      </el-table-column>
      <el-table-column label="点击率" sortable :sort-method="(a, b) => sortPercent(a, b, 'ctr')" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.ctr }}</span>
        </template>
      </el-table-column>
      <el-table-column label="转化率" sortable :sort-method="(a, b) => sortPercent(a, b, 'cvr')" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.cvr }}</span>
        </template>
      </el-table-column>
      <el-table-column label="ACOS" sortable :sort-method="(a, b) => sortPercent(a, b, 'acos')" border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.acos }}</span>
        </template>
      </el-table-column>
      <el-table-column label="CPC" prop="cpc" sortable border>
        <template slot-scope="scope">
          <span v-show="!scope.row.show">{{ scope.row.cpc }}</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import DatePicker from "@/components/util/Date-picker.vue";
export default {
  name: "AdDetail",
  components: { DatePicker },
  data() {
    return {
      datatree: [],
      impressions: 0,
      clicks: 0,
      orders: 0,
      cost: 0,
      sales: 0,
      CTR: 0,
      CVR: 0,
      ACOS: 0,
      CPC: 0,
      dataType: "sku",
      sku: "",
      campaignId: "",
      campaignName: "",
      adGroupId: "",
      adGroupName: "",
      promotionTarget: [0, 1, 2, 3],
      options: [
        {
          value: 0,
          label: "测试"
        },
        {
          value: 1,
          label: "推广"
        },
        {
          value: 2,
          label: "盈利"
        },
        {
          value: 3,
          label: "清仓"
        }
      ],
      myChart: null,
      cardSelected: [0, 1],
      yAxis: [
        {
          type: "value",
          name: "曝光"
        },
        {
          type: "value",
          name: "点击"
        },
        {
          type: "value",
          name: "订单"
        },
        {
          type: "value",
          name: "花费"
        },
        {
          type: "value",
          name: "收入"
        },
        {
          type: "value",
          name: "点击率",
          axisLabel: {
            show: true,
            interval: "auto",
            formatter: function (value) {
                return value * 100 + '%';
            }
          }
        },
        {
          type: "value",
          name: "转化率",
          axisLabel: {
            show: true,
            interval: "auto",
            formatter: function (value) {
                return value * 100 + '%';
            }
          }
        },
        {
          type: "value",
          name: "ACOS",
          axisLabel: {
            show: true,
            interval: "auto",
            formatter: function (value) {
                return value * 100 + '%';
            }
          }
        },
        {
          type: "value",
          name: "CPC"
        },
      ],
      source: []
    };
  },
  created: function() {
    this.getData();
  },
  mounted() {
    this.drawChart();
  },
  methods: {
    sortNum(a, b, sortType) {
      if (sortType == 'cost') {
        return parseFloat(a.cost) - parseFloat(b.cost);
      } else if (sortType == 'sales') {
        return parseFloat(a.sales) - parseFloat(b.sales);
      }
      return a - b;
    },
    sortPercent(a, b, sortType) {
      if (sortType == 'ctr') {
        a = a.ctr;
        b = b.ctr;
      } else if (sortType == 'cvr') {
        a = a.cvr;
        b = b.cvr;
      } else if (sortType == 'acos') {
        a = a.acos;
        b = b.acos;
      }
      a = a.substring(0, a.length-1);
      b = b.substring(0, b.length-1);
      if (a == 'Infinity') {
        a = parseInt(9999999)
      } else if (a == 'NaN') {
        a = -1;
      } else {
        a = parseFloat(a)
      }
      if (b == 'Infinity') {
        b = parseInt(9999999)
      } else if (b == 'NaN') {
        b = -1;
      }  else {
        b = parseFloat(b)
      }
      return a - b;
    },
    selectCard(idx) {
      const index = this.cardSelected.indexOf(idx);
      if (index > -1) {
        if (this.cardSelected.length != 1)
          this.cardSelected.splice(index, 1);
      } else {
        if (this.cardSelected.length == 2) {
          this.cardSelected.shift();
        }
        this.cardSelected.push(idx);
      }
      this.setChartOption();
    },
    drawChart() {
      this.myChart = this.$echarts.init(
        document.getElementById("detail-line-chart")
      );
      this.myChart.setOption({
        tooltip: { trigger: "item" },
        xAxis: { type: "category" },
        yAxis: {}
      });
    },
    getCtrPerc(x) {
      var [a, b, c, d, m] = [
        -0.143272565,
        1.70912511,
        0.00208597634,
        100.50824,
        0.4359404
      ];
      var res = d + (a - d) / (1 + (x / c) ** b) ** m;
      return Math.min(100, Math.max(res, 0));
    },
    getCvrPerc(x) {
      var [a, b, c, d, m] = [
        0.14596741,
        1.42160323,
        0.11587171,
        100.77540273,
        1.24233436
      ];
      var res = d + (a - d) / (1 + (x / c) ** b) ** m;
      return Math.min(100, Math.max(res, 0));
    },
    getAcosPerc(x) {
      var [a, b, c, d, m] = [
        97.7003117,
        1.37673678,
        254.185172,
        -2.45787384,
        5544.8177
      ];
      var res = d + (a - d) / (1 + (x / c) ** b) ** m;
      return Math.min(100, Math.max(res, 0));
    },
    cellcolor({ row, column, rowIndex, columnIndex }) {
      if (columnIndex == 7) {
        var { impressions, clicks } = row;
        var ctr = impressions == 0 ? 0 : clicks / impressions;
        var perc = this.getCtrPerc(ctr);
        var color = this.perc2color(perc);
        return "text-shadow: black 0.1em 0.1em 0.15em; color:" + color;
      } else if (columnIndex == 8) {
        var { clicks, orders } = row;
        var cvr = clicks == 0 ? 0 : orders / clicks;
        var perc = this.getCvrPerc(cvr);
        var color = this.perc2color(perc);
        return "text-shadow: black 0.1em 0.1em 0.15em; color:" + color;
      } else if (columnIndex == 9) {
        var { cost, sales } = row;
        cost = Number(cost);
        sales = Number(sales);
        var acos = sales == 0 ? 2 : cost / sales;
        var perc = this.getAcosPerc(acos);
        var color = this.perc2color(perc);
        return "text-shadow: black 0.1em 0.1em 0.15em; color:" + color;
      }
    },
    perc2color(perc) {
      var r,
        g,
        b = 0;
      if (perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
      } else {
        g = 255;
        r = Math.round(510 - 5.1 * perc);
      }
      var h = r * 0x10000 + g * 0x100 + b * 0x1;
      return "#" + ("000000" + h.toString(16)).slice(-6);
    },
    handleClcik(e) {
      this.dataType = e;
      switch (e) {
        case "sku":
          this.sku = "";
          this.campaignId = "";
          this.campaignName = "";
          this.adGroupId = "";
          this.adGroupName = "";
          this.currentPage = 1;
          break;
        case "campaign":
          this.campaignId = "";
          this.campaignName = "";
          this.adGroupId = "";
          this.adGroupName = "";
          this.currentPage = 1;
          break;
        case "adgroup":
          this.adGroupId = "";
          this.adGroupName = "";
          this.currentPage = 1;
          break;
        default:
          break;
      }
      this.getData();
    },
    toPercent(point) {
      var str = Number(point * 100).toFixed(2);
      str += "%";
      return str;
    },
    rowClick(row) {
      switch (this.dataType) {
        case "sku":
          this.dataType = "campaign";
          this.sku = row.id;
          this.getData();
          break;
        case "campaign":
          this.dataType = "adgroup";
          this.campaignId = row.id;
          this.campaignName = row.name;
          this.getData();
          break;
        case "adgroup":
          this.dataType = "target";
          this.adGroupId = row.id;
          this.adGroupName = row.name;
          this.getData();
          break;
        case "target":
          // this.getData()
          break;
        default:
          break;
      }
    },
    setChartOption() {
      var myChartParams = { yAxis: [], series: [], source: [] };
      if (this.cardSelected.length == 2) {
        myChartParams["yAxis"] = [
          this.yAxis[this.cardSelected[0]],
          this.yAxis[this.cardSelected[1]]
        ];
        myChartParams["series"] = [
          {
            type: "line",
            smooth: true,
            seriesLayoutBy: "row",
            lineStyle: {
              width: 4
            },
            emphasis: { focus: "series" }
          },
          {
            type: "line",
            smooth: true,
            yAxisIndex: 1,
            seriesLayoutBy: "row",
            lineStyle: {
              width: 4
            },
            emphasis: { focus: "series" }
          }
        ];
        myChartParams["source"] = [
          this.source[0],
          this.source[this.cardSelected[0] + 1],
          this.source[this.cardSelected[1] + 1]
        ];
      } else if (this.cardSelected.length == 1) {
        myChartParams["yAxis"] = [this.yAxis[this.cardSelected[0]]];
        myChartParams["series"] = [
          {
            type: "line",
            smooth: true,
            seriesLayoutBy: "row",
            lineStyle: {
              width: 4
            },
            emphasis: { focus: "series" }
          }
        ];
        myChartParams["source"] = [
          this.source[0],
          this.source[this.cardSelected[0] + 1]
        ];
      }
      this.myChart.setOption(
        {
          tooltip: {
            trigger: "item"
          },
          xAxis: { type: "category" },
          dataset: {
            source: myChartParams["source"]
          },
          yAxis: myChartParams["yAxis"],
          series: myChartParams["series"]
        },
        true
      );
    },
    initDate() {
      var date = new Date();
      var year = date.getFullYear(); //获取完整的年份(4位)
      var month = date.getMonth() + 1; //获取当前月份(0-11,0代表1月)
      var day = date.getDate(); //获取当前日
      if (month <= 9) {
        month = "0" + month;
      }
      if (day <= 9) {
        day = "0" + day;
      }
      if (!this.$store.state.start_date) {
        this.$store.commit("setStartDate", year + month + day);
      }
      if (!this.$store.state.end_date) {
        this.$store.commit("setEndDate", year + month + day);
      }
    },
    getData() {
      if (!this.$store.state.start_date || !this.$store.state.end_date) {
        this.initDate();
      }
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/campaignData`, {
          params: {
            shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
              "shopId"
            ],
            profileId: this.$store.state.current_profileId,
            start: this.$store.state.start_date,
            end: this.$store.state.end_date,
            dataType: this.dataType,
            sku: this.sku,
            campaignId: this.campaignId,
            adGroupId: this.adGroupId,
            promotionTarget: this.promotionTarget.join(",")
          }
        })
        .then(response => {
          const { detail, total, source } = response.data;
          if (detail instanceof Array) {
            this.datatree = detail;
            this.impressions = total.impressions;
            this.clicks = total.clicks;
            this.orders = total.orders;
            this.cost = total.cost.toFixed(2);
            this.sales = total.sales.toFixed(2);
            this.CTR =
              this.impressions > 0
                ? this.toPercent(this.clicks / this.impressions)
                : 0;
            this.CVR =
              this.clicks > 0 ? this.toPercent(this.orders / this.clicks) : 0;
            this.ACOS =
              this.sales > 0 ? this.toPercent(this.cost / this.sales) : 0;
            this.CPC =
              this.clicks > 0 ? (this.cost / this.clicks).toFixed(2) : 0;
            this.datatree.forEach(element => {
              element.cost = element.cost.toFixed(2);
              element.sales = element.sales.toFixed(2);
              element.ctr = this.toPercent(
                element.clicks / element.impressions
              );
              element.cvr = this.toPercent(element.orders / element.clicks);
              element.acos = this.toPercent(element.cost / element.sales);
              element.cpc = (element.cost / element.clicks).toFixed(2);
            });
            this.source = source;
          }
          this.setChartOption();
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
<style>
.el-row {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
}
.search {
  margin-left: 10px;
}
.my-checkbox {
  margin-top: 10px;
}
.el-col {
  width: 20%;
  margin-bottom: 10px;
}
</style>
