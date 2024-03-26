<template>
    <!-- the bar -->
    <div>
        <!-- inner of the bar -->
        <div class="searchgroupform">
            <!-- black div for insert something -->
            <div>
            </div>
            <!-- the filter -->
            <div id="filter" @click="clickSort">
                <div>{{ pic_lastest_sorted ? 'ล่าสุด' : 'แรกสุด' }}
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .searchgroupform{
        display: flex;
        flex-wrap: wrap;
        margin: 5px 30px 0px 30px;
        padding-bottom: 8px;
        justify-content: space-between;
        border-bottom: solid 2px #DEDEDE;
    }
</style>

<script lang="ts">
    export default {
        props: {
            pic_lastest_sorted: Boolean
        },
        methods: {
            // when the sort button is clicked
            clickSort() {
                this.$emit('dataToParent', !this.pic_lastest_sorted);
            },
        }
    };
</script>