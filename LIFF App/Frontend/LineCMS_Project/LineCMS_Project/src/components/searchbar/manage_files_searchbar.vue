<template>
    <!-- form for submit the search query -->
    <form @submit.prevent="searchFiles">
        <!-- inner search bar container -->
        <div class="searchfileform">
            <!-- input field -->
            <div>
                <input type="search" id="file-search" v-model="searchQuery" placeholder="ค้นหา">
                <button type="submit">
                    <img src="../pic/magnifier.png" height="20px" width="auto">
                </button>
            </div>
            <!-- sort button -->
            <div id="filter" @click="clickSort">
                <!-- toggle the sort ways -->
                <div>{{ file_lastest_sorted ? 'ล่าสุด' : 'แรกสุด'}}</div>
            </div>
        </div>
    </form>
</template>
  
<style scoped>
    .searchfileform {
        display: flex;
        flex-wrap: wrap;
        margin: 5px 30px 0px 30px;
        padding-bottom: 8px;
        justify-content: space-between;
        background-color: #FFF;
    }
    #filter{
        padding-bottom: -5px;
    }
    .searchfileform>div{
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
        font-size: 15px;
        border: none;
        border-bottom: solid 2px #DEDEDE;
    }
</style>
  
<script lang="ts">
    export default {
        props: {
            file_lastest_sorted: Boolean
        },
        data(){
            return{
                searchQuery: '',
            }
        },
        methods: {
            // when click the sort button, tell the parent to toggle sort.
            clickSort() {
                this.$emit('dataToParent', !this.file_lastest_sorted);
            },
            // send keyword for search to parent.
            searchFiles(){
                this.$emit('searchQuery', this.searchQuery);
            }
        }
    };
  </script>