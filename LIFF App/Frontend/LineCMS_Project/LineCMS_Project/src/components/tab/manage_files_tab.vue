<template>
    <!-- the tab contain the viewed user profile picture and the couple of buttons (image and file) -->
    <div class="menu-container">
        <!-- viewed user profile picture -->
        <div id="profile-pic-container">
            <img v-if="userInfo.userProfileLink" :src='userInfo.userProfileLink' alt="user_pic">
            <img v-else src='../pic/account_user.png' alt="user_pic">
        </div>
        <!-- the couple of buttons -->
        <form>
            <!-- image button -->
            <button class="btn" id="classnumber1_container" @click="clickImages();" :style='{borderColor: image_selected ? "#544E4E" : "#E9E9E9"}'>
                <!-- button inner container -->
                <div class="number-container">
                    <div>
                        <!-- title of image button -->
                        <p class="classnumber" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                            รูปภาพ
                        </p>
                        <!-- arrow right icon, visible if another one is selected -->
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="arrow-right">
                            <path :style='{strokeWidth:"1", stroke: image_selected ? "#E9E9E9" : "#9D9D9D", fill: image_selected ? "#E9E9E9" : "#9D9D9D"}' 
                                d="M16.2424621,12.7424621 L10.2424621,18.7424621 C9.83241161,19.1525126 9.16758839,19.1525126 8.75753788,18.7424621 C8.34748737,18.3324116 8.34748737,17.6675884 8.75753788,17.2575379 L14.0150758,12 L8.75753788,6.74246212 C8.34748737,6.33241161 8.34748737,5.66758839 8.75753788,5.25753788 C9.16758839,4.84748737 9.83241161,4.84748737 10.2424621,5.25753788 L16.2424621,11.2575379 C16.6525126,11.6675884 16.6525126,12.3324116 16.2424621,12.7424621 L16.2424621,12.7424621 Z">
                            </path>
                        </svg>
                    </div>
                    <!-- images count -->
                    <p class="totalnumber" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                        {{ userInfo.imageCount }}
                    </p>
                </div>
            </button>
            <!-- file button -->
            <button class="btn" id="classnumber2_container" @click="clickFiles();" :style='{borderColor: image_selected ? "#E9E9E9" : "#544E4E"}'>
                <!-- button inner container -->
                <div class="number-container">
                    <div>
                        <!-- title of file button -->
                        <p class="classnumber" :style='{color: image_selected ? "#9D9D9D" : "#535353"}'>ไฟล์</p>
                        <!-- arrow right icon, visible if another one is selected -->
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="arrow-right">
                            <path :style='{strokeWidth:"1", stroke: image_selected ? "#9D9D9D" : "#E9E9E9", fill: image_selected ? "#9D9D9D" : "#E9E9E9"}'
                                d="M16.2424621,12.7424621 L10.2424621,18.7424621 C9.83241161,19.1525126 9.16758839,19.1525126 8.75753788,18.7424621 C8.34748737,18.3324116 8.34748737,17.6675884 8.75753788,17.2575379 L14.0150758,12 L8.75753788,6.74246212 C8.34748737,6.33241161 8.34748737,5.66758839 8.75753788,5.25753788 C9.16758839,4.84748737 9.83241161,4.84748737 10.2424621,5.25753788 L16.2424621,11.2575379 C16.6525126,11.6675884 16.6525126,12.3324116 16.2424621,12.7424621 L16.2424621,12.7424621 Z">
                            </path>
                        </svg>
                    </div>
                    <!-- files count -->
                    <p class="totalnumber" :style='{color: image_selected ? "#9D9D9D" : "#535353"}'>
                        {{ userInfo.fileCount }}
                    </p>
                </div>
            </button>
        </form>
    </div>
</template>

<style scoped>
    #profile-pic-container{
        display: flex;
        flex-wrap: wrap;
    }
    #profile-pic-container>img{
        height: 100%;
        width: 100%;
        aspect-ratio: 1/1;
        border-radius: 30px;
    }
    form{
        padding: 0px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-gap: 10px;
    }
    .menu-container{
        display:grid;
        grid-gap: 15px;
        grid-template-columns: 2fr 6fr;
        height: 103px;
        align-items: center;
        padding: 10px 30px 0px 30px;
    }
    .btn{
        padding: 0px;
        margin: 0px;
        width: 100%;
        height: 73px;
        display: flex;
        border: 4px solid;
        background-color: #e9e9e9;
    }
    .arrow-right{
        height: 15px;
        width: 15px;
    }
    .number-container{
        display: grid;
        height: 100%;
        width: 100%;
        grid-template-rows: 1fr 2fr;
        padding: 4px 4px 4px 4px;
    }
    .number-container div{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-right: 7px;
    }

    #classnumber1_container{
        border-radius: 25px 10px 10px 25px;
    }
    #classnumber2_container{
        border-radius: 10px 25px 25px 10px;
    }
    .classnumber{
        color: #000;
        font-size: 100%;
        font-weight: 600;
        margin: 4px 0px 0px 4px;
        text-align: start;
    }
    .totalnumber{
        color: #000;
        align-self: center;
        font-size: 200%;
        font-weight: 600;
        text-align: right;
        margin: 0px 10px -5px 0px;
    }
    .router-link{
        padding: 0px;
    }


</style>

<script lang="ts">
    import axios from "axios"
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import { ref, onMounted } from 'vue';

    export default {
        props:{
            image_selected:Boolean,
            reloadtab:Boolean,
        },
        data(props){
            return{
                image_selected: this.image_selected,
                reloadtab: props.reloadtab,
            };
        },
        setup() {
            // declare variables
            const store = useStore()
            const groupID = ref("")
            const userID = ref("")
            const userInfo = ref(Object)

            // get user info (profile pic, image count, file count etc.)
            const getUserInfo = async () => {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/group/user_info',
                        method: 'POST',
                        data: JSON.stringify({
                            userId: userID.value,
                            groupId: groupID.value,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    });
                    userInfo.value = response.data;
                } catch (error) {
                    console.error('Error:', error.response.data);
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
                    // then save user id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }

                // get cluster id that is saved at localStorage
                const saveViewUserID = localStorage.getItem('viewUserID');
                if (saveViewUserID && saveViewUserID.length > 0) {
                    // if there is cluster id at localStorage
                    userID.value = saveViewUserID;
                } else {
                    userID.value = store.state.view_user_ID;
                    // then save cluster id from store to localStorage
                    localStorage.setItem('viewUserID', userID.value);
                }
                getUserInfo();
            });

            return{
                store,
                groupID,
                userID,
                userInfo,
                getUserInfo,
            }
        },
        
        // watch if values is changed
        watch: {
            // watch 'reloadtab' variable
            reloadtab: {
                // handle for change
                handler(newValue) {
                    // if value is change
                    if(newValue){
                        // reload (get new amount of picture and files info)
                        this.getUserInfo().then(async()=>{
                            // after new amount is get, tell the parent
                            this.$emit("reset_isReload", false)
                        })
                    }
                },
                // do the handle immediately
                immediate: true
            }
        },
        methods: {
            // if image button is clicked
            clickImages(){
                // image button is selected, so we have to show the list of images 
                this.image_selected = true;
                event?.preventDefault();
                // tell the parent to show list of image
                this.$emit('dataToParent', true);
            },
            clickFiles(){
                // image button is not selected, so we have to show the list of files (just like toggle) 
                this.image_selected = false;
                event?.preventDefault();
                // tell to parent to show the list of files
                this.$emit('dataToParent', false);
            },
        }
    }
</script>