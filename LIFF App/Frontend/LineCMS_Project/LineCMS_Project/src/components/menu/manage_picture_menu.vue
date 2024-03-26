<template>
    <!-- search bar -->
    <ManagePicSearchbar :pic_lastest_sorted="this.pic_lastest_sorted" @dataToParent="handleDataFromChild" />
    <!-- collection of all pictures sent in the group or just any someone's pictures -->
    <div class="menu-container">
        <!-- loop to get all group of date in the list of picture (grouped by date) -->
        <div
            v-for='(image, index) in groupedImages ' :key="index"
        >
            <!-- title of pictures is the transformed date -->
            <div class="files-date">
                {{ changeDateForm(index) }}
            </div>
            <!-- the container of each group of pictures -->
            <div class="image-grid-container">
                <!-- loop to show the list of pictures in the same date (same group) -->
                <div column align-center v-for='img in image'>
                    <!-- each picture container -->
                    <div class="item-container" @click="togglePopUp('buttonTrigger'), updatePopupImg(img)">
                        <!-- each picture -->
                        <img class="result-image" :src= 'img.imageLink' alt="user_pic" >
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- if there is no picture, or waiting for the picture list -->
    <div class="no-file" v-if="Object.keys(groupedImages).length<=0">
            {{isGotfile ? "ไม่พบรูปภาพ" : "กำลังโหลด"}}
    </div>
    <!-- picture pop up when click each picture -->
    <PicPopup v-if="popupTrigger.buttonTrigger" :togglePopUp=" () => togglePopUp('buttonTrigger')" :imgid="img_popup.imageId" :senderid="img_popup.senderId" :datesent="img_popup.datesent" :timesent="img_popup.timesent" :imgtype=img_popup.imgtype :imgsrc="img_popup.imageLink" :userId="userID" :senderName="img_popup.senderUserName" @reloadPicMenu="reloadPicLists">    
    </PicPopup>
</template>

<style scoped>
    .menu-container{
        display:grid;
        grid-gap: 10px;
        justify-items: stretch;
        grid-template-columns: repeat(1, auto);
        width: 100%;
        align-items: center;
        padding: 10px 30px 30px 30px;
    }
    .files-date{
        margin-bottom: 3px;
        font-weight: 600;
    }
    .no-file{
        display: flex;
        width: 100%;
        height: 40vh;
        justify-content: center;
        align-items: center;
    }
    .image-grid-container{
        display: grid;
        grid-gap:5px;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(auto-fill, 1fr);
        padding-bottom: 30px;
    }
    .item-container{
        display: flex;
        width: 100%;
        height: 100%;
        align-items: center;
        flex-wrap: wrap;
    }
    .result-image{
        max-width: 100%;
        max-height: 100%;
    }
    .router-link{
        padding: 0px;
    }

</style>

<script lang="ts">
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import axios from "axios"
    import { ref, onMounted } from 'vue';
    import { useRoute } from 'vue-router';
    import PicPopup from '../popup/manage_pic_popup.vue'
    import ManagePicSearchbar from '../searchbar/manage_pic_searchbar.vue'

    export default {
        components: {
            PicPopup,
            ManagePicSearchbar,
        },
        data(){
            // declare default value
            return{
                popupTrigger: {
                    buttonTrigger: false,
                },
                img_popup:{
                    imageId: "",
                    senderId: "",
                    datesent: "",
                    timesent: "",
                    imgtype: "",
                    imageLink: "",
                    senderUserName: "",
                },
            }
        },
        setup() {
            // declare variables
            const groupID = ref("")
            const groupGalleryImagesData = ref([])
            const store = useStore()
            const groupedImages = ref({});
            const viewUserID = ref("")
            const userID = ref ("")
            const route = useRoute();
            const isGotfile = ref(false);
                
            const pic_lastest_sorted = ref(true);

            // reform the file list to be shown on page.
            const reFormPicGallery = (pic_data:[]) =>{
                if (pic_data) {
                    // create blank {}
                    var tempGroupedPics = {}
                    // group the picture by date
                    pic_data.forEach(pic => {
                        // get the sent date in all picture to be key, and group all pictures sent at the same date in the same key. then reformat the key (date).
                        const date = pic.savedTime.split("T")[0];
                        // if there is no some date key, just create the new one 
                        if (!tempGroupedPics[date]) {
                            tempGroupedPics[date] = [];
                        }
                        // push the picture the date key it was sent.
                        tempGroupedPics[date].push(pic);
                    });
                    // show the result
                    groupedImages.value = tempGroupedPics
                }
                else {
                    console.error("cannot group img");
                }
            };

            // get picture list in group
            const getGalleryImagesInfo_Group = async () => {
                try {
                    const response = await axios.request({
                    url: API_URL+'/data/image/sort_latest',
                    method: 'POST',
                    data: JSON.stringify({
                        groupId: groupID.value,
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    });
                    // collect data to be used as default value from server
                    groupGalleryImagesData.value = response.data.sortLatest;

                    // end page loading state 
                    isGotfile.value = true


                } catch (error) {
                    console.error('Error:', error.response.data);
                    // end page loading state 
                    isGotfile.value = true

                }
            };

            // get the picture list that someone sent
            const getGalleryImagesInfo_Me = async () => {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/image/sort_latest',
                        method: 'POST',
                        data: JSON.stringify({
                            userId: viewUserID.value,
                            groupId: groupID.value,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    });
                    // collect data to be used as default value from server
                    groupGalleryImagesData.value = response.data.sortLatest;

                    // end page loading state 
                    isGotfile.value = true

                } catch (error) {
                    console.error('Error:', error.response.data);
                    // end page loading state 
                    isGotfile.value = true
                }
            };

            // when initializing this page
            onMounted(function() {
                // get group id that is saved at localStorage
                const saveGroupID = localStorage.getItem('groupID');
                if (saveGroupID && saveGroupID.length > 0) {
                    // if there is group id at localStorage
                    groupID.value = saveGroupID;
                } else {
                    // if there is not group id at localStorage, get it from store
                    groupID.value = store.state.group_ID;
                    // then save group id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }

                // get user id that is saved at localStorage
                const saveUserID = localStorage.getItem('userID');
                if (saveUserID && saveUserID.length > 0) {
                    // if there is user id at localStorage
                    userID.value = saveUserID;
                } else {
                    // if there is not user id at localStorage, get it from store
                    userID.value = store.state.user_ID;
                    // then save user id from store to localStorage
                    localStorage.setItem('userID', userID.value);
                }

                // get viewed user's id that ia saved at localStorage
                const saveViewUserID = localStorage.getItem('viewUserID');
                if (saveViewUserID && saveViewUserID.length > 0) {
                    // is there is viewed user's id
                    viewUserID.value = saveViewUserID;
                } else {
                    // if there is no id at localStorage, get it from store
                    viewUserID.value = store.state.view_user_ID;
                    // then save id from store to localStorage
                    localStorage.setItem('viewUserID', viewUserID.value);
                }

                // check the rendering page
                if (route.path == "/gallery") {
                    // if it is gallery, get list of all files in group.
                    getGalleryImagesInfo_Group().then(async () => {await reFormPicGallery(groupGalleryImagesData.value)})
                } else if (route.path == "/managefiles") {
                    // if it is viewing the file sent by each member, get list of all files sent in that group
                    getGalleryImagesInfo_Me().then(async () => {await reFormPicGallery(groupGalleryImagesData.value)})
                }
            });
            return{
                groupID,
                userID,
                viewUserID,
                groupGalleryImagesData,
                groupedImages,
                isGotfile,
                route,
                getGalleryImagesInfo_Me,
                getGalleryImagesInfo_Group,
                reFormPicGallery,
                pic_lastest_sorted,

            }
        },
        methods:{
            // toggle pop up
            togglePopUp(trigger:string){
                this.popupTrigger[trigger] = !this.popupTrigger[trigger];
            },
            // update file info, and sender info to be shown in popup
            updatePopupImg(img:{}){
                this.img_popup.imageId = img.imageId;
                this.img_popup.senderId = img.senderId;
                this.img_popup.datesent = this.changeDateForm(img.savedTime);
                this.img_popup.timesent = img.savedTime.substring(11, 16);
                this.img_popup.imgtype = this.getFileType(img.imageId);
                this.img_popup.imageLink = img.imageLink;
                this.img_popup.senderUserName = img.senderUserName;
            },
            // get file type from file name
            getFileType(a:string){
                // get the last string after the last '.'
                return a.split('.').pop()
            },

            // change date from yyyy-mm-dd to thai form
            changeDateForm(date:string){
                // divide part into date, month and year.
                const arrdate = date.split('T')[0].split('-')
                let dd = arrdate[2]
                let mm = arrdate[1]
                let yy = arrdate[0]

                if      (mm == '01' || mm == '1') { mm = "ม.ค."}
                else if (mm == '02' || mm == '2') { mm = "ก.พ."}
                else if (mm == '03' || mm == '3') { mm = "มี.ค."}
                else if (mm == '04' || mm == '4') { mm = "เม.ย."}
                else if (mm == '05' || mm == '5') { mm = "พ.ค."}
                else if (mm == '06' || mm == '6') { mm = "มิ.ย."}
                else if (mm == '07' || mm == '7') { mm = "ก.ค."}
                else if (mm == '08' || mm == '8') { mm = "ส.ค."}
                else if (mm == '09' || mm == '9') { mm = "ก.ย."}
                else if (mm == '10') { mm = "ต.ค."}
                else if (mm == '11') { mm = "พ.ย."}
                else if (mm == '12') { mm = "ธ.ค."}

                // change year form from AD to B.E.
                yy = (parseInt(yy) + 543).toString()

                // connect date, month and year
                return dd + " " + mm + " " + yy
            },

            // sort in current selecting sort way
            handleDataFromChild(data:boolean) {
                // get the current sort way
                this.pic_lastest_sorted = data;
                    // copy the key (date) and reverse it, from latest to newest or newest to latest.
                    const sortedKeys = Object.keys(this.groupedImages).reverse();
                    // create black {}.
                    const sortedObject = {};
                    // copy the data of each key to it
                    sortedKeys.forEach(key => {
                        sortedObject[key] = this.groupedImages[key];
                    });
                    // reverse data inside each key
                    for (const key in sortedObject){
                        if (Array.isArray(sortedObject[key])) {
                            sortedObject[key].reverse();
                        }
                    }
                    // display the result
                    this.groupedImages = sortedObject
            },
            // reload list of file
            reloadPicLists(isReload:boolean){
                // when popup make change (delete the file) to the file list.
                if(isReload){
                    // check the rendering page. this use different API.
                    if (this.route.path == "/gallery") {
                        // wait for request for file list
                        this.getGalleryImagesInfo_Group()
                        // then, wait for reform the list th be shown.
                        .then(async () => {
                            await this.reFormPicGallery(this.groupGalleryImagesData)
                        })
                        // then ,sort in current sorting way
                        .then(async () => {
                            if(!this.pic_lastest_sorted){
                                await this.handleDataFromChild(false)
                            }
                        })
                        // after finish to reform the list, tell the parrent to reload the tab.
                        .then(async ()=>{
                            this.$emit('reloadFileTab', true);
                        })
                        // check the rendering page. this use different API.
                    } else if (this.route.path == "/managefiles") {
                        // wait for request for file list
                        this.getGalleryImagesInfo_Me()
                        .then(async () => {
                            await this.reFormPicGallery(this.groupGalleryImagesData)
                        })
                        // then ,sort in current sorting way
                        .then(async () => {
                            if(!this.pic_lastest_sorted){
                                await this.handleDataFromChild(false)
                            }
                        })
                        // after finish to reform the list, tell the parrent to reload the tab.
                        .then(async ()=>{
                            this.$emit('reloadFileTab', true);
                        })
                    }
                }
            }
        }
    }
</script>
