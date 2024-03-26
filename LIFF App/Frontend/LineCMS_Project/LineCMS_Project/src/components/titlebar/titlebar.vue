<template>
    <div class="titlebar">
        <!-- title of each page -->
        <div class="title-container" v-if="($route.path==='/selectmenu')||($route.path==='/gallery')||($route.path==='/managefiles')">
            <h1 id="title" v-if="$route.path==='/selectmenu'">กลุ่ม&nbsp;{{ getGroupName() }}</h1>
            <h1 id="title" v-else-if="$route.path==='/gallery'">กลุ่ม&nbsp;{{ getGroupName() }}</h1>
            <h1 id="title" v-else-if="($route.path==='/managefiles') && (getUserID()==getViewUserID())">จัดการไฟล์ส่วนตัว</h1>
            <h1 id="title" v-else-if="($route.path==='/managefiles') && (getUserID()!=getViewUserID())">{{ getViewUserName() }}</h1>
        </div>
    </div>
    <!-- black white box is for hide content on screen whe scroll -->
    <div id="white-box" v-if="($route.path==='/selectmenu')||($route.path==='/gallery')||($route.path==='/managefiles')"></div>
</template>

<style scoped>
    .titlebar{
        display: flex;
        width: 100%;
        align-items: flex-end;
        text-align: center;
        font-size: 70%;
        border-bottom: 2px solid #DEDEDE;
        position: fixed;
        background-color: white;     
        box-shadow: 0px 0px 10px 2px rgba(0, 0, 0, 0.1);
    }
    .icon-container{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 33px;
        width: 33px;
    }
    .close-button{
        padding: 6px;
    }
    .title-container{
        width:100%;
        white-space: nowrap; 
        padding: 0vh 30px 1.5vh 30px;
        overflow: hidden;
        display: flex;
        justify-content: center;
        min-height: 4.5vh;
    }
    #title{
        padding: 0% 0% 0% 0%;
        font-weight: 600;
        text-overflow: ellipsis;
        overflow: hidden;
        display: inline-block;
        width: 90%;
    }
    #white-box{
        height: 5.5vh;
    }
</style>

<script lang="ts">
    import { useStore } from 'vuex';

    export default{
        data(){
            return{
                store: useStore(),
            }
        },
        methods: {
            // get group name 
            getGroupName(){
                // get group name that is saved at localStorage
                const saveGroupName = localStorage.getItem('groupName');
                if (saveGroupName && saveGroupName.length > 0) {
                    // if there is group name at localStorage
                    return saveGroupName;
                } else if(this.store.state.group_name){
                    // if there is no group name at localStorage, get it from store and save it to localStorage.
                    localStorage.setItem('groupName', this.store.state.group_name);
                    return this.store.state.group_name;
                }
                else{
                    // no group name in both localStorage and store
                    return ""
                }
            },
            // get user id 
            getUserID(){
                // get user id that is saved at localStorage
                const saveUserID = localStorage.getItem('userID');
                if (saveUserID && saveUserID.length > 0) {
                    // if there is user id at localStorage
                    return saveUserID;
                } else if(this.store.state.user_ID){
                    // if there is no user id at localStorage, get it from store and save it to localStorage.
                    localStorage.setItem('userID', this.store.state.user_ID);
                    return this.store.state.user_ID;
                }
                else{
                    // no user id in both localStorage and store
                    return ""
                }
            },
            // get viewed user's id 
            getViewUserID(){
                // get viewed user's id that is saved at localStorage
                const saveViewUserID = localStorage.getItem('viewUserID');
                if (saveViewUserID && saveViewUserID.length > 0) {
                    // if there is the id at localStorage
                    return saveViewUserID;
                } else if (this.store.state.view_user_ID) {
                    // if there is no the id at localStorage, get it from store and save it to localStorage.
                    localStorage.setItem('viewUserID', this.store.state.view_user_ID);
                    return this.store.state.view_user_ID;
                }
                else{
                    // no id in both localStorage and store
                    return ""
                }
            },
            // get viewed user's name 
            getViewUserName(){
                // get viewed user's name that is saved at localStorage
                const saveViewUserName = localStorage.getItem('viewUserName');
                if (saveViewUserName && saveViewUserName.length > 0) {
                    // if there is the name at localStorage
                    return saveViewUserName;
                } else if (this.store.state.view_user_name) {
                    // if there is no the name at localStorage, get it from store and save it to localStorage.
                    localStorage.setItem('viewUserName', this.store.state.view_user_name);
                    return this.store.state.view_user_name;
                }
                else{
                    // no name in both localStorage and store
                    return ""
                }
            }

        }
    }

</script>