<template>
    <!-- search bar -->
    <form @submit.prevent="searchGroups">
        <!-- inner of the bar -->
        <div class="searchgroupform">
            <!-- input area -->
            <div>
                <input type="search" id="group-search" v-model="searchQuery" placeholder="ค้นหา">
                <!-- submit button -->
                <button>
                    <img src="../pic/magnifier.png" height="25px" width="auto">
                </button>
            </div>
            <!-- filter -->
            <div id="filter" @click="clickSort()">
                <div>
                    {{ groupSort }}
                </div>
            </div>
        </div>

    </form>
</template>

<style scoped>
    .searchgroupform{
        display: flex;
        height: 10vh;
        align-items: end;
        justify-content: space-between;
        margin: 0px 30px 0px 30px;
        padding-bottom: 10px;
    }

    .searchgroupform>div{
        display: grid;
        grid-template-columns: 1fr auto;
    }

    button{
        height: auto;
        width: 20px;
        align-self: flex-end;
        background-color: rgba(255, 255, 255, 0);
        border: none;

    }
    img{
        padding: -2px;
        margin:0px;
        justify-self: center;
        align-self: center;

    }

    input {
        width: 30vw;
        padding: 5px 5px;
        border-radius: 0px;
        background-color: #FFF;
        font-size: 16px;
        border: none;
        border-bottom: solid 2px #DEDEDE;
    }

</style>

<script lang="ts">
    export default {
        props:{
            groupSort : String,
        },
        data(){
            return{
                searchQuery: '',
            }
        },
        methods: {
            // when the filter button is click. tellthe parent to change to next sort
            clickSort() {
                if (this.groupSort == "ก-ฮ"){
                    this.$emit('dataToParent', "ฮ-ก");
                }
                else if (this.groupSort == "ฮ-ก"){
                    this.$emit('dataToParent', "ล่าสุด");
                } 
                else{
                    this.$emit('dataToParent', "ก-ฮ");
                }
            },
            // tell the parent about the search keyword
            searchGroups(){
                this.$emit('searchQuery', this.searchQuery);
            }
        }
    }
</script>