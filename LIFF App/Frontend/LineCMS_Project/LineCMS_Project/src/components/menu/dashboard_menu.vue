<template>
    <!-- search bar of showing group's member at gallery page -->
    <DashboardMenuSearchBar :memberCount="getMemberCount(groupGalleryData)" @dataToParent="handleDataFromChild" :memberSort="memberSort"/>
    <!-- collection of group's member -->
    <div class="menu-container">
        <!-- loop to get all cluster in the group -->
        <div
            v-for='member in groupGalleryData' :key='member.userId'
        >
            <!-- link to manage-file page when click -->
            <router-link class="router-link" :to="{path: '/managefiles'}">
                <!-- each member -->
                <div class="item-container" @click="setViewUserInfo(member.userId,member.userName)">
                    <!-- member profile -->
                    <img :src= 'member.userProfileLink' alt="user_pic">
                    <!-- member username -->
                    <div class="boxname">
                        {{ member.userName }}
                    </div>
                    <!-- picture icon -->
                    <div>
                        <img src="../pic/pic.png" height="18px" width="auto"/>
                    </div>
                    <!-- amount of images -->
                    <div>
                        {{ member.imageCount }}
                    </div>
                    <!-- folder icon -->
                    <div>
                        <img src="../pic/folder.png" height="18px" width="auto"/>
                    </div>
                    <!-- amount of files -->
                    <div>
                        {{ member.fileCount }}
                    </div>
                </div>
            </router-link>    
        </div>
    </div>
    <!-- check if requesting member or there is no member there -->
    <div class="no-member" v-if="groupGalleryData.length<=0">
        {{isGotMember ? "ไม่พบสมาชิก" : "กำลังโหลด"}}
    </div>
</template>

<style scoped>

    .menu-container{
        display:grid;
        grid-gap: 10px;
        justify-items: stretch;
        grid-template-columns: repeat(1, auto);
        width: 100%;
        align-items: center;
        padding: 5% 30px 5% 30px;
    }
    .item-container{
        display: grid;
        width: 100%;
        height: 100%;
        align-items: center;
        grid-template-columns: 1fr 2fr 0.2fr 0.5fr 0.2fr 0.5fr;
        grid-gap: 10px;
    }
    .item-container>img{
        width: 15vw;
        aspect-ratio: 1/1 ;
        border-radius: 100%;
    }
    .item-container>div{
        color: #333;
    }
    .item-container>div>img{
        margin-top: 5px;

    }
    .boxname{
        color:black;
    }

    .router-link{
        padding: 0px;
    }
    .no-member{
        display: flex;
        width: 100%;
        height: 40vh;
        justify-content: center;
        align-items: center;
    }

</style>

<script lang="ts">
    import axios from "axios"
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import { ref, onMounted } from 'vue';
    import DashboardMenuSearchBar from '../searchbar/dashboard_menu_search.vue'

    export default {
        components:{
            DashboardMenuSearchBar,
        },
        data(){
            // declare default sort of member name
            return {
                memberSort: "ก-ฮ",
            }
        },
        setup() {
            // declare variables
            const store = useStore()
            const groupID = ref("")
            const groupGalleryData = ref([])
            const isGotMember = ref(false)

            // get all member of selected group and their amount of pictures and files
            const getGalleryInfo = async () => {
                // try to get group's member info using group id.
                try {
                    const response = await axios.request({
                    url: API_URL+'/data/group/member_info',
                    method: 'POST',
                    data: JSON.stringify({
                        groupId: groupID.value,
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    timeout: 5000,
                    });
                    groupGalleryData.value = response.data.memberList;
                    isGotMember.value = true;
                } catch (error) {
                    console.error('Error:', error.response.data);
                    isGotMember.value = true;
                }
            };
            // when initialize this page
            onMounted(() => {
                // get group id that is saved at localStorage
                const saveGroupID = localStorage.getItem('groupID');
                if (saveGroupID && saveGroupID.length > 0) {
                    // if there is group id at localStorage
                    groupID.value = saveGroupID;
                } else {
                    // if there is no group id at localStorage, get it from store
                    groupID.value = store.state.group_ID;
                    // then save group id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }
                // get group's member info
                getGalleryInfo();
            });

            return{
                store,
                groupID,
                groupGalleryData,
                isGotMember,
            }
        },
        methods:{
            // save selected user info
            setViewUserInfo(user_ID:string, user_name:string){
                // save user id
                this.store.dispatch('setViewUserID', user_ID); // save to store
                localStorage.setItem('viewUserID', user_ID); // save to localStorage

                // save member username
                this.store.dispatch('setViewUserName', user_name);
                localStorage.setItem('viewUserName', user_name)
            },
            // count member server is sent
            getMemberCount(jsonData:[]){
                let memberListSize = 0;
                if (jsonData && Array.isArray(jsonData)) {
                    memberListSize = jsonData.length;
                }
                return memberListSize
            },
            handleDataFromChild(data:string) {
                // change sorting way.
                this.memberSort = data;
                // if alphabetical order.
                if (this.memberSort == 'ก-ฮ'){
                    const tempSortData = this.groupGalleryData.sort((a, b) => {
                        const nameA = a.userName.toUpperCase();
                        const nameB = b.userName.toUpperCase();
                        if (nameA < nameB) {
                            return -1;
                        }
                        if (nameA > nameB) {
                            return 1;
                        }
                        return 0;
                    });
                    this.groupGalleryData = tempSortData
                }
                // if alphabetical reversed order
                else if (this.memberSort == 'ฮ-ก'){
                    this.groupGalleryData.sort((a, b) => {
                        const nameA = a.userName.toUpperCase();
                        const nameB = b.userName.toUpperCase();
                        if (nameA < nameB) {
                            return 1;
                        }
                        if (nameA > nameB) {
                            return -1;
                        }
                        return 0;
                    });
                }
                // if sort from most pictures sent
                else if(this.memberSort =='รูปมากสุด'){
                    this.groupGalleryData.sort((a, b) => {
                        const nameA = a.imageCount;
                        const nameB = b.imageCount;
                        if (nameA < nameB) {
                            return 1;
                        }
                        if (nameA > nameB) {
                            return -1;
                        }
                        return 0;
                    });
                }
                // if sort from most files sent
                else if(this.memberSort =='ไฟล์มากสุด'){
                    this.groupGalleryData.sort((a, b) => {
                        const nameA = a.fileCount;
                        const nameB = b.fileCount;
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
        },
    };
</script>