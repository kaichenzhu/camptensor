<template>
  <div>
    <el-row>
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item
          style="cursor: pointer;"
          v-if="dataType != 'campaign'"
          @click.native="handleClcik('campaign')"
          >全部广告活动</el-breadcrumb-item
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
    <el-table
      :data="datatree.slice((currentPage-1)*pagesize,currentPage*pagesize)"
    >
      <el-table-column label="名称" border>
        <template slot-scope="scope">
          <el-input
            placeholder="请输入内容"
            v-show="scope.row.show"
            v-model="scope.row.name"
          ></el-input>
          <span 
            v-show="!scope.row.show"
            style="cursor: pointer;"
            @click="rowClick(scope.row)"
          >{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" border>
        <template slot-scope="scope">
          <el-input
            placeholder="请输入内容"
            v-show="scope.row.show"
            v-model="scope.row.state"
          ></el-input>
          <span v-show="!scope.row.show">{{ scope.row.state }}</span>
        </template>
      </el-table-column>
      <el-table-column label="竞价/预算" border>
        <template slot-scope="scope">
          <el-input
            placeholder="请输入内容"
            v-show="scope.row.show"
            v-model="scope.row.bid"
          ></el-input>
          <span v-show="!scope.row.show">{{ scope.row.bid }}</span>
        </template>
      </el-table-column>
      <el-table-column label="上调/下调" border>
        <template slot-scope="scope">
          <el-input
            placeholder="请输入内容"
            v-show="scope.row.show"
            v-model="scope.row.bid_power"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button v-show="!scope.row.show" @click="scope.row.show = true"
            >编辑</el-button
          >
          <el-button v-show="scope.row.show" @click="scope.row.show = false"
            >取消</el-button
          >
          <el-button @click="editRow(scope.row)">保存</el-button>
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
  name: "AdReportStruct",
  data() {
    return {
      datatree: [],
      dataType: 'campaign',
      campaignName: '',
      campaignId: '',
      adGroupName: '',
      adGroupId: '',
      pagesize: 30,
      currentPage: 1,
      total: 0
    };
  },
  created: function() {
    this.getData()
  },
  methods: {
    handleSizeChange(val) {
        this.pagesize =val;
    },
    handleCurrentChange(val) {
      this.currentPage = val;
    },
    getData() {
      var id = '';
      if (this.dataType == 'adgroup') {
        id = this.campaignId;
      } else if (this.dataType == 'target') {
        id = this.adGroupId;
      }
      this.$request
      .get(`${this.$store.state.endpoints.baseUrl}/campaignStruct`, {
        params: {
          profileId: this.$store.state.current_profileId,
          dataType: this.dataType,
          parentId: id
        }
      })
      .then(response => {
        if (response.data instanceof Array) {
          this.datatree = response.data;
          this.total = this.datatree.length;
        }
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      });
    },
    handleClcik(e) {
      this.dataType = e;
      switch (e) {
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
    rowClick(row) {
      switch (this.dataType) {
        case "campaign":
          this.dataType = "adgroup";
          this.campaignId = row.id;
          this.campaignName = row.name;
          this.currentPage = 1;
          this.getData();
          break;
        case "adgroup":
          this.dataType = "target";
          this.adGroupId = row.id;
          this.adGroupName = row.name;
          this.currentPage = 1;
          this.getData();
          break;
        case "target":
          // this.getData()
          break;
        default:
          break;
      }
    },
    editRow(row) {
      row.show = false;
      console.log(row);
      switch (row.category) {
        case "campaign":
          this.updateCampaign(row);
          break;
        case "adgroup":
          this.updateAdGroup(row);
          break;
        case "keyword":
          this.updateKeyword(row);
          break;
        case "target":
          this.updateTargeting(row);
          break;
        case "sku":
          this.updateSku(row);
          break;
        default:
          break;
      }
    },
    updateCampaign(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/editCampaign`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          data: row
        })
        .then(response => {
          console.log(response);
          this.$message({
            duration: 1000,
            message: "修改广告成功",
            type: "success"
          });
        });
    },
    updateAdGroup(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/editAdGroup`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          data: row
        })
        .then(response => {
          console.log(response);
          this.$message({
            duration: 1000,
            message: "修改广告组成功",
            type: "success"
          });
        });
    },
    updateKeyword(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/editKeyword`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          data: row
        })
        .then(response => {
          console.log(response);
          this.$message({
            duration: 1000,
            message: "修改关键词成功",
            type: "success"
          });
        });
    },
    updateTargeting(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/editTargeting`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          data: row
        })
        .then(response => {
          console.log(response);
          this.$message({
            duration: 1000,
            message: "修改投放目标成功",
            type: "success"
          });
        });
    },
    updateSku(row) {
      this.$request
        .post(`${this.$store.state.endpoints.baseUrl}/editSku`, {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx][
            "shopId"
          ],
          profileId: this.$store.state.current_profileId,
          data: row
        })
        .then(response => {
          console.log(response);
          this.$message({
            duration: 1000,
            message: "修改SKU成功",
            type: "success"
          });
        });
    }
  }
};
</script>
