<template>
    <div>
        <h1>广告分析</h1>
        <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="广告活动" name="campaign"><AdCampaign/></el-tab-pane>
            <el-tab-pane label="关键词" name="keyword"><AdKeyword/></el-tab-pane>
            <el-tab-pane label="ASIN" name="asin"><AdASIN/></el-tab-pane>
        </el-tabs>
    </div>
</template>
<script>
import AdCampaign from '@/components/console/anls/Ad-campaign.vue'
import AdKeyword from '@/components/console/anls/Ad-keyword.vue'
import AdASIN from '@/components/console/anls/Ad-asin.vue'
export default {
    name:"AnlsAd",
    components: { AdCampaign, AdKeyword, AdASIN},
    data() {
        return {
            activeName: 'keyword'
        };
    },
    methods: {
        handleClick(tab, event) {
            console.log(tab, event);
        }
    }
};
</script>