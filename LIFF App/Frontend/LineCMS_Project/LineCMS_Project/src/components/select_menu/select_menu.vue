<template>
    <!-- group profile image -->
    <div class="img-box">
        <img id="img-linegroup" :src='groupProfileLink' alt="user_pic" height="75%" width="auto">
    </div>
    <!-- pack of 4 buttons -->
    <form class="menu-container">
        <!-- search by face button -->
        <router-link class="router-link" :to="{path: '/clustersearch'}">
            <!-- button -->
            <div class="menu-button">
                <!-- icon -->
                <img src="../pic/user2.png" alt="user_pic" height="auto" width="auto">
                <div>
                    <!-- button's display name -->
                    <div>
                        ค้นหารูปด้วยใบหน้า
                    </div>
                </div>
            </div>
        </router-link>
        <!-- graph of relation button -->
        <router-link class="router-link" :to="{path: '/graphcreate'}">
            <!-- button -->
            <div class="menu-button">
                <!-- icon -->
                <img src="../pic/graph.png" alt="graph" height="auto" width="auto">
                <!-- button's display name -->
                <div>
                    <div>
                        สร้างกราฟ<br>
                        ความสัมพันธ์
                    </div>
                </div>
            </div>
        </router-link>
        <router-link class="router-link" :to="{path: '/gallery'}">
            <!-- button -->
            <div class="menu-button">
                <!-- icon -->
                <img src="../pic/gallery.png" alt="gallery" height="auto" width="auto">
                <!-- button's display name -->
                <div>
                    <div>
                        แกลเลอรี่
                    </div>
                </div>
            </div>
        </router-link>
        <router-link class="router-link" :to="{path: '/managefiles'}" @click="setViewUserID(userID)">
            <!-- button -->
            <div class="menu-button">
                <!-- icon -->
                <img src="../pic/folder.png" alt="folder" height="auto" width="auto">
                <!-- button's display name -->
                <div>
                    <div>
                        จัดการไฟล์<br>
                        ส่วนตัว
                    </div>
                </div>
            </div>
        </router-link>
    </form>
</template>

<style scoped>
    #img-linegroup{
        border-radius: 40px;
        border: 2px solid #DEDEDE;
    }
    .img-box{
        padding-top:0;
        margin: 0 0 0 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height:25vh
    }
    .menu-container{
        display:grid;
        justify-content: center;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, 1fr);
        height:65vh;
        padding: 0px 30px 30px 30px;
        grid-gap: 5px;
    }
    .menu-button{
        display: grid;
        width: 100%;
        height: 100%;
        grid-template-rows: 2fr 1.5fr;
        justify-items: center;
        background: #E9E9E9;
        border: none;
        border-radius: 20px;
        align-self: flex-start;
        color: #000;
        font-size: 110%;
        padding: 10%;

    }
    .menu-button>img{
        align-self: flex-end;
        padding-top: 1vh;
        padding-bottom: 1vh;
        max-width: 20vw;
        
    }
    .menu-button>div>div{
        font-size: 105%;
        font-weight: 600;
        text-align: center;
    }
    .menu-button>div{
        display: flex;
        justify-content: center;
        align-items: center;
    }

</style>

<script lang="ts">
    import { useStore } from 'vuex';
    import { ref, onMounted, onBeforeUnmount } from 'vue';

    export default {
        setup() {
            // declare variables
            const store = useStore();
            const userID = ref("")
            const groupProfileLink = ref("");
            const groupID = ref("")

            // when initializing this page
            onMounted(() => {
                // get group profile image link that is saved at localStorage
                const savedGroupProfileLink = localStorage.getItem('groupProfileLink');
                if (savedGroupProfileLink && savedGroupProfileLink.length > 0) {
                    // if there is the link at localStorage
                    groupProfileLink.value = savedGroupProfileLink;
                } else {
                    // if there is no link at localStorage, get it from store
                    groupProfileLink.value = store.state.group_profile_image;
                    // then save the link from store to localStorage
                    localStorage.setItem('groupProfileLink', groupProfileLink.value);
                }

                // get group id that is saved at localStorage
                const savedGroupID = localStorage.getItem('groupID');
                if (savedGroupID && savedGroupID.length > 0) {
                    // if there is group id at localStorage
                    groupID.value = savedGroupID;
                } else {
                    // if there is no group id at localStorage, get it from store
                    groupID.value = store.state.group_ID;
                    // then save group id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }

                // get user id that is saved at localStorage
                const savedUserID = localStorage.getItem('userID');
                if (savedUserID && savedUserID.length > 0) {
                    // if there is user id at localStorage
                    userID.value = savedUserID;
                } else {
                    // if there is no user id at localStorage, get it from store
                    userID.value = store.state.user_ID;
                    // then save user id from store to localStorage
                    localStorage.setItem('userID', userID.value);
                }
            });

            // before destroy the page, save user id, group id and group profile image link to localStorage
            onBeforeUnmount(() => {
                localStorage.setItem('userID', userID.value);
                localStorage.setItem('groupProfileLink', groupProfileLink.value);
                localStorage.setItem('groupID', groupID.value);
            });

            return {
                userID,
                groupProfileLink,
                groupID,
                store,
            };
        },
        methods:{
            // save user id of viewed user to store and localStorage. 
            setViewUserID(user_ID){
                this.store.dispatch('setViewUserID', user_ID);
                localStorage.setItem('viewUserID', user_ID);
            }
        }
    };
</script>