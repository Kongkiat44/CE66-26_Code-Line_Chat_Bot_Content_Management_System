<template>
    <!-- title bar -->
    <div class="title-bar">
        เลือกใบหน้า
    </div>
    <!-- collection of all cluster in group -->
    <div class="menu-container">
        <!-- loop to get all cluster in list -->
        <div
            v-for='cluster in clusters ' :key='cluster.clusterId'
        >
            <!-- link to next page if searching image by cluster -->
            <router-link class="router-link" v-if="$route.path==='/clustersearch'" :to="{path: '/imageresult'}">
                <div class="item-container"  @click="updateSampleCluster(cluster)">
                    <!-- sample image of each cluster -->
                    <img :src= 'cluster.faceLink' alt="user_pic">
                </div>
            </router-link>
            <!-- link to next page if create graph of a selecting cluster -->
            <router-link class="router-link" v-else-if="$route.path==='/graphcreate'" :to="{path: '/graphcreatestatus'}">
                <div class="item-container"  @click="updateSampleCluster(cluster)">
                    <!-- sample image of each cluster -->
                    <img :src= 'cluster.faceLink' alt="user_pic">
                </div>
            </router-link>
        </div>
    </div>
</template>

<style scoped>
    .title-bar{
        padding-top:0;
        margin: 0 30px 0 30px;
        display: flex;
        justify-content: flex-start;
        align-items: flex-end;
        height:8vh;
        font-size: 18px;
        font-weight: 600;
        border-bottom: 2px solid #DEDEDE;
    }
    
    .menu-container{
        display:grid;
        grid-gap: 20px;
        grid-template-columns: repeat(3, 1fr);
        margin: 30px 30px 30px 30px;
    }
    .item-container>img{
        max-width: 24vw;
        max-height: 24vw;
        aspect-ratio: 1/1 ;
        border-radius: 100%;
        border: 1px solid #999;
    }
    .item-container>div{
        text-align: center;
        color: #000;
    }
    .item-container{
        display: flex;
        flex-wrap: wrap;
        padding-bottom: 20px;
    }
    .router-link{
        padding: 0px;
    }

</style>

<script lang="ts">
    import axios from "axios"
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import { ref, onMounted, onBeforeUnmount } from 'vue';
    export default {

        setup() {
            // declare variables
            const store = useStore();
            const groupID = ref("");
            const clusters = ref ([]);
            
            // when initialize this page
            onMounted(() => {
                // get group id that ia saved at localStorage
                const savedGroupID = localStorage.getItem('groupID');
                if (savedGroupID) {
                    // if there is group id at localStorage
                    groupID.value = savedGroupID;
                } else {
                    // if there is not group id at localStorage, get it from store
                    groupID.value = store.state.group_ID;
                    // then save group id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }
            });
            // before destroy this page
            onBeforeUnmount(() => {
                // save group id to localStorage.
                localStorage.setItem('groupID', groupID.value);
            });
            return {
                store,
                groupID,
                clusters,
            };
        },
        // when the page is mounted
        mounted(){
            // get the cluster
            this.getCluster();
        },
        methods:{
            // save selected cluster info at localStorage to be used at next page.
            updateSampleCluster(cluster): void{
                // save clusterId
                localStorage.setItem('clusterSampleID', cluster.clusterId);
                // save faceLink
                localStorage.setItem('clusterSampleImage', cluster.faceLink);
            },

            // get group's cluster info
            async getCluster() {
                // try to get group's cluster info using group id.
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/face/search_all',
                        method: 'POST',
                        data: JSON.stringify({
                            groupId: this.groupID,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    })
                    // then save the cluster from response
                    .then(response => {
                        this.clusters = response.data.responseData;
                    })
                    // if error, catch it
                    .catch(error => {
                        console.error('Error:', error.response.data);
                    });
                }
                // if there is an error.
                catch (error) {
                    console.error('Error fetching data:', error);
                }
            },
        }
    }
</script>
