<template>
  <div>
    <el-form ref="form" :rules="rules" :model="form" label-width="120px">
      <el-row>
        <el-col :span="5" :offset="6">
          <el-form-item label="SKU" prop="sku">
            <el-select v-model="form.sku" placeholder="选择待投放SKU">
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              >
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="5" :offset="6">
          <el-form-item label="广告活动名称" prop="campaignName">
            <el-input v-model.trim="form.campaignName"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="3">
          <el-form-item label="每日预算" prop="budget">
            <el-input v-model="form.budget"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="5" :offset="6">
          <el-form-item label="广告组名称" prop="groupName">
            <el-input v-model.trim="form.groupName"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="3">
          <el-form-item label="默认竞价" prop="defaultBid">
            <el-input v-model="form.defaultBid"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="8" :offset="6">
          <el-form-item label="广告类型" prop="campaignType">
            <el-radio-group v-model="form.campaignType">
              <el-radio label="auto">自动广告</el-radio>
              <el-radio label="keyword">手动广告(关键词)</el-radio>
              <el-radio label="product">手动广告(商品ASIN))</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider></el-divider>
      <el-row>
        <el-col :span="8" :offset="5">
          <el-form-item>
            <el-button
              type="primary"
              @click="submitForm('form')"
              round
              style="width:200px"
              >确认提交</el-button
            >
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script>
export default {
  name: "AdReportCreater",
  data() {
    var checkIsPositiveEx0 = (rule, value, callback) => {
      ///^(\d|[1-9]\d+)(\.\d{1,2})?$/          ---->2位小数
      var reg = /^(\d|[1-9]\d+)(\.\d+)?$/;
      if (reg.test(value)) {
        if (value == "0") {
          callback(new Error("请输入大于0的正实数"));
        } else {
          callback();
        }
      } else {
        callback(new Error("请输入大于0的正实数"));
      }
    };
    return {
      options: [],
      form: {},
      rules: {
        sku: [{ required: true, message: "请选择SKU", trigger: "blur" }],
        campaignName: [
          { required: true, message: "广告活动名称不可为空", trigger: "blur" }
        ],
        budget: [
          { required: true, message: "广告活动预算不可为空", trigger: "blur" },
          { validator: checkIsPositiveEx0, trigger: "blur" }
        ],
        groupName: [
          { required: true, message: "广告组名称不可为空", trigger: "blur" }
        ],
        defaultBid: [
          {
            required: true,
            message: "广告组默认竞价不可为空",
            trigger: "blur"
          },
          { validator: checkIsPositiveEx0, trigger: "blur" }
        ],
        campaignType: [
          { required: true, message: "广告类型不可为空", trigger: "blur" }
        ]
      }
    };
  },
  created() {
    this.getSkus();
  },
  methods: {
    getSkus() {
      this.$request
        .get(`${this.$store.state.endpoints.baseUrl}/productSku`, {
          params: {
            profileId: this.$store.state.current_profileId
          }
        })
        .then(response => {
          this.options = response.data.sort((a, b) => a.value.localeCompare(b.value));
          this.$message({
            duration: 1000,
            message: "获取SKU成功",
            type: "success"
          });
        });
    },
    submitForm(formName) {
      this.$refs[formName].validate(valid => {
        if (valid) {
          this.$request
            .post(`${this.$store.state.endpoints.baseUrl}/createCampaign`, {
              shopId: this.$store.state.shops[
                this.$store.state.current_shop_idx
              ]["shopId"],
              profileId: this.$store.state.current_profileId,
              campaign: this.form
            })
            .then(response => {
              console.log(response);
              this.$message({
                duration: 1000,
                message: "创建广告成功",
                type: "success"
              });
            });
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    }
  }
};
</script>

<style></style>
