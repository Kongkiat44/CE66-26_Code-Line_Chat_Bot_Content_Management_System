<template>
    <form>
        <!-- search bar (tool bar) -->
        <div class="searchgroupform">
            <!-- member count -->
            <div>
                สมาชิก ({{ memberCount }})
            </div>
            <!-- sort button -->
            <div id="filter" @click="clickSort">
                {{ memberSort }}
            </div>
        </div>
    </form>
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
        props:{
            memberCount: Number,
            memberSort : String,
        },
        methods: {
            // if sort button is clicked once change state to the next sort by tell the parent.
            clickSort() {
                if (this.memberSort == "ก-ฮ"){
                    this.$emit('dataToParent', "ฮ-ก");
                }
                else if (this.memberSort == "ฮ-ก"){
                    this.$emit('dataToParent', "รูปมากสุด");
                }
                else if (this.memberSort == "รูปมากสุด"){
                    this.$emit('dataToParent', "ไฟล์มากสุด");
                }
                else{
                    this.$emit('dataToParent', "ก-ฮ");
                }
            },
        }
    }

</script>