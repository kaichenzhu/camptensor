<template>
  <div>
    <el-form ref="form" :model="form" label-width="80px">
      <div v-for="(target, index) in form.targets" :key="index">
        <el-row>
          <el-col :span="4" :offset="0">
            <el-form-item label="关键词">
              <el-input v-model="target.keyword"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12" :offset="1">
            <el-form-item :label-width="'150px'" label="SKU/广告活动/广告组">
              <el-cascader
                style="width:600px; margin-left:-70px;"
                v-model="target.target"
                :options="form.options"
                :props="{ expandTrigger: 'hover' }"
                @change="handleChange"></el-cascader>
            </el-form-item>
          </el-col>
          <el-col :span="5" :offset="0">
            <el-form-item label="匹配类型">
            <template>
              <el-checkbox-group v-model="target.type">
                <el-checkbox label="exact"></el-checkbox>
                <el-checkbox label="phrase"></el-checkbox>
                <el-checkbox label="broad"></el-checkbox>
              </el-checkbox-group>
            </template>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      <el-divider></el-divider>
      <el-form-item>
        <el-button type="success" @click="addNewTarget">新增投放目标</el-button>
        <el-button type="primary" @click="onSubmit">立即创建</el-button>
        <el-button>取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'AdReportManual',
  data () {
    return {
      form: {
        targets: [{
          keyword: '',
          target: [],
          type: []
        }],
        options: []
      }
    }
  },
  created() {
    this.getOptions();
  },
  methods: {
    getOptions() {
      this.$request.get(`${this.$store.state.endpoints.baseUrl}/getSkuManualCampaigns`, {
        params: {
          shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
          profileId: this.$store.state.current_profileId
        }
      }).then(response => {
        this.form.options = response.data.sort((a, b) => a.value.localeCompare(b.value));
        this.$message({
          duration: 1000,
          message: "获取数据成功",
          type: "success"
        });
      })
    },
    addNewTarget () {
      var target = Object.assign({}, this.form.targets[this.form.targets.length - 1]);
      target['keyword'] = '';
      this.form.targets.push(target);
    },
    onSubmit () {
      this.$request.post(`${this.$store.state.endpoints.baseUrl}/createManual`, {
        shopId: this.$store.state.shops[this.$store.state.current_shop_idx]['shopId'],
        profileId: this.$store.state.current_profileId,
        targets: this.form.targets
      }).then(response => {
        console.log(response);
        this.$message({
          duration: 1000,
          message: "创建广告明细成功",
          type: "success"
        });
      })
    },
    handleChange(value) {
      console.log(value);
    }
  }
}

</script>

<style>
</style>
