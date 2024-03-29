<template>
    <!-- group search bar -->
    <SeachgroupBar :groupSort="groupSort"  @dataToParent="handleDataFromChild" @searchQuery="searchGroups"/>
    <!-- collection of group user are in with chatbot -->
    <div class="menu-container">
        <!-- loop to show all the group in groups list -->
        <div v-if="groups.length>0" class="have-group"
            v-for=' group in groupsSearch ' :key='group.groupId'
        >
            <!-- link to select menu and update selected group info -->
            <router-link class="router-link" @click="updateSelectedGroupInfo(group)" :to="{path: '/selectmenu'}" >
                <!-- each group -->
                <div class="item-container">
                    <!-- group profile image -->
                    <img :src= 'group.groupProfileLink' alt="user_pic">
                    <!-- group's name -->
                    <div class="groupname-container">
                        <p class="groupname">
                            {{ group.groupName }}
                        </p>
                    </div>
                </div>
            </router-link>    
        </div>
        <!-- if the group is loading or no group the user are with bot-->
        <div v-else class="no-group">
            <p>{{isLoading ? "กำลังโหลด":"ไม่พบกลุ่มไลน์ที่มี CMS Official กับผู้ใช้"}}</p>
        </div>
    </div>
</template>

<style scoped>
    .menu-container{
        display:grid;
        grid-gap: 20px;
        grid-template-columns: repeat(3, 1fr);
        width: 100vw;
        padding: 30px 30px 30px 30px;
    }
    .have-group{
        margin-bottom: 5px;
    }
    .no-group{
        display: flex;
        height: 40vh;
        width: 100vw;
        margin: 0px -30px 0px -30px;
        text-align: center;
        justify-content: center;
        align-items: center;
    }
    .item-container{
        display: grid;
        grid-template: 
            "a"
            "a"
            "b";
        width: 100%;

    }
    .item-container>img{
        width: 24vw;
        aspect-ratio: 1/1 ;
        border-radius: 100%;
        border: 1px solid #DEDEDE;
        justify-self: center;
    }
    .groupname-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        text-align: center;
        overflow: hidden;
    }

    .groupname {
        line-height: 1.5em;
        max-height: 3em;
        text-overflow: ellipsis;
        white-space: pre-wrap;
        overflow: hidden;
        margin: 0;
        color: #000;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow-wrap: break-word;
    }
    
    .router-link{
        padding:0px;
    }

</style>

<script lang="ts">
    import axios from "axios"
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import { ref, onMounted, onBeforeUnmount } from 'vue';
    import SeachgroupBar from '../searchbar/searchbar_group.vue'
    import liff from '@line/liff';
    import { useRouter } from "vue-router";


    export default {
        name: "group-grid",
        components:{
            SeachgroupBar,
        },
        setup() {
            // declare variable
            const store = useStore()
            const groups =  ref([])
            const userID = ref("")
            const groupSort = ref("ล่าสุด")
            const isLoading = ref(true)
            const groupsSearch = ref([])
            const router = useRouter()

            // get how to sort from search bar
            const handleDataFromChild = (data:string) => {
                groupSort.value = data;
                // A-Z
                if (groupSort.value == 'ก-ฮ'){
                    groupsSearch.value.sort((a, b) => {
                        const nameA = a.groupName.toUpperCase();
                        const nameB = b.groupName.toUpperCase();
                        if (nameA < nameB) {
                            return -1;
                        }
                        if (nameA > nameB) {
                            return 1;
                        }
                        return 0;
                    });
                }
                // Z-A
                else if (groupSort.value == 'ฮ-ก'){
                    groups.value.sort((a, b) => {
                        const nameA = a.groupName.toUpperCase();
                        const nameB = b.groupName.toUpperCase();
                        if (nameA < nameB) {
                            return 1;
                        }
                        if (nameA > nameB) {
                            return -1;
                        }
                        return 0;
                    });
                }
                // last update
                else if(groupSort.value =='ล่าสุด'){
                    groups.value.sort((a, b) => {
                        const nameA = a.lastUsedTime;
                        const nameB = b.lastUsedTime;
                        if (nameA < nameB) {
                            return 1;
                        }
                        if (nameA > nameB) {
                            return -1;
                        }
                        return 0;
                    });
                }
            }

            // when initialize this page
            onMounted(() => {
                // connect to liff
                liff.init({
                    liffId: '1660748214-64JZBlo0',
                })
                // after connected
                .then(async () => {
                    // try to get group list user are in with chat bot
                    try {
                        // get user id
                        const context = await liff.getContext();
                        if(context.userId){
                            userID.value = context.userId;
                        }
                        // if user is not using liff browser, redirect to blank page
                        if (context.type != 'utou'){
                            store.dispatch('setBrowserType', context.type);
                            router.push({name:'redirectpage'})
                        }

                        // request group list user are in with chat bot by user id
                        const response = await axios.request({
                            url: API_URL+'/data/group/search_all',
                            method: 'POST',
                            data: JSON.stringify({
                                userId: userID.value,
                            }),
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            timeout: 5000,
                        });
                        groups.value = response.data.responseData;
                        groupsSearch.value = groups.value
                        // sort the group by current sort
                        handleDataFromChild(groupSort.value);
                    } catch (error) {
                        console.error('Error:', error.response.data);
                    }
                    // end loading/requesting status
                    isLoading.value = false;

                })
                .catch(error => {
                    console.error('Error initializing LIFF:', error);
                    // end loading/requesting status
                    isLoading.value = false;

                });
            });
            // before the page is destroy.
            onBeforeUnmount(() => {
                // save user id to localStorage to be used in next all process need.
                localStorage.setItem('userID', userID.value);
            });

            return{
                userID,
                store,
                groups,
                isLoading,
                handleDataFromChild,
                groupSort,
                groupsSearch,
            }
        },
        methods:{
            // update selected group info
            updateSelectedGroupInfo(group:{}): void{
                // update value to store
                this.store.dispatch('setGroupID', group.groupId);
                this.store.dispatch('setGroupProfileImage', group.groupProfileLink);
                this.store.dispatch('setGroupName', group.groupName);

                // update value to be store in localStorage
                localStorage.setItem('groupID', group.groupId);
                localStorage.setItem('groupProfileLink', group.groupProfileLink);
                localStorage.setItem('groupName', group.groupName);
            },
            // search group by keyword.
            searchGroups(searchQuery:string){
                // filter the group from the user's input
                this.groupsSearch = this.groups.filter(group => {
                    const groupNameLower = group.groupName.toLowerCase();
                    const searchQueryLower = searchQuery.toLowerCase();
                    return groupNameLower.includes(searchQueryLower);
                });
            }
        }
    }
</script>

