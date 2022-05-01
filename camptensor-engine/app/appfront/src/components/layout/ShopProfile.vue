<template>
    <el-cascader
        v-model="value"
        :options="options"
        :props="{ expandTrigger: 'hover' }"
        @change="handleChange">
    </el-cascader>
</template>

<script>
export default {
    name: 'ShopProfile',
    data() {
        return {
            value: [],
            options: []
        }  
    },
    created() {
        this.getData();
    },
    methods: {
        getData() {
            this.value = [Number(this.$store.state.current_shop_idx), Number(this.$store.state.current_profile_idx)];
            const shops = this.$store.state.shops;
            for (let index = 0; index < shops.length; index++) {
                const shop = shops[index];
                const profiles = shop.profiles;
                const children = [];
                for (let index = 0; index < profiles.length; index++) {
                    const profile = profiles[index];
                    children.push({
                        value: index,
                        label: profile.countryCode + ' / ' + profile.profileId + ' / ' + profile.marketplaceStringId
                    })
                }
                this.options.push({
                    value: index,
                    label: shop.name,
                    children: children
                })
            }
        },
        handleChange(value) {
            const shop = this.$store.state.shops[value[0]];
            const profile = shop.profiles[value[1]];
            this.$store.commit('setCurrentShop', {
                currentShopId: shop.shopId,
                currentShopIdx: value[0]
            });
            this.$store.commit('setCurrentProfile', {
                currentProfileId: profile.profileId,
                currentProfileIdx: value[1]
            });
            this.$router.go(0);
        }
    }
}
</script>