<template>
    <div>
        <h1>关键词优化</h1>
        <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="关键词否定" name="negative" :lazy="true"><AdOptimizationNegative/></el-tab-pane>
            <el-tab-pane label="关键词优化" name="autotomanual" :lazy="true"><AdOptimizationAutotomanual/></el-tab-pane>
            <el-tab-pane label="关键词推荐" name="recommend" :lazy="true"><AdOptimizationRecommend/></el-tab-pane>
            <el-tab-pane label="投放目标优化" name="targeting" :lazy="true"><AdOptimizationTargeting/></el-tab-pane>
            <!-- <el-tab-pane label="优化动作" name="action" :lazy="true"><AdOptimizationAction/></el-tab-pane> -->
        </el-tabs>
    </div>
</template>
<script>
import AdOptimizationNegative from '@/components/console/ad/Optimization-negative.vue'
import AdOptimizationAutotomanual from '@/components/console/ad/Optimization-autotomanual.vue'
import AdOptimizationRecommend from '@/components/console/ad/Optimization-recommend.vue'
import AdOptimizationTargeting from '@/components/console/ad/Optimization-targeting.vue'
// import AdOptimizationAction from '@/components/console/ad/Optimization-action.vue'
// import AdOptimizationBid from '@/components/console/ad/Optimization-bid.vue'

export default {
    name:"AdReport",
    components: { AdOptimizationAutotomanual, AdOptimizationNegative, AdOptimizationTargeting, AdOptimizationRecommend },
    data() {
        return {
            activeName: 'negative'
        };
    },
    methods: {
        handleClick(tab, event) {
            console.log(tab, event);
        }
    }
};
</script>