<template>
    <div>
        <h1>广告活动</h1>
        <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="广告结构" name="struct" :lazy="true"><AdReportStruct/></el-tab-pane>
            <el-tab-pane label="快速新建广告" name="quick" :lazy="true"><AdReportQuick/></el-tab-pane>
            <el-tab-pane label="新建广告" name="creater" :lazy="true"><AdReportCreater/></el-tab-pane>
            <el-tab-pane label="关键词投放" name="manual" :lazy="true"><AdReportManual/></el-tab-pane>
        </el-tabs>
    </div>
</template>
<script>
import AdReportStruct from '@/components/console/ad/Report-struct.vue'
import AdReportQuick from '@/components/console/ad/Report-quick.vue'
import AdReportCreater from '@/components/console/ad/Report-creater.vue'
import AdReportManual from '@/components/console/ad/Report-manual.vue'
export default {
    name:"AdReport",
    components: { AdReportStruct, AdReportQuick, AdReportCreater, AdReportManual },
    data() {
        return {
            activeName: 'struct'
        };
    },
    methods: {
        handleClick(tab, event) {
            console.log(tab, event);
        }
    }
};
</script>``