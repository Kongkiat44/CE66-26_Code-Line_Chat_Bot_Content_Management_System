<template>
    <!-- search bar -->
    <ManageFileSearchbar :file_lastest_sorted="this.file_lastest_sorted" @dataToParent="handleDataFromChild" @searchQuery="searchFiles"/>
    <!-- collection of all files sent in the group or just any someone's files -->
    <div class="menu-container">
        <!-- loop to get all group of date in the list of file (grouped by date) -->
        <div
            v-for='(file, index) in groupedFiles '
        >
            <!-- title of file is the transformed date -->
            <div class="files-date">
                {{ changeDateForm(index) }}
            </div>
            <!-- the container of each group of files -->
            <div class="file-grid-container">
                <!-- loop to show the list of file in the same date (same group) -->
                <div v-for='fi in file'>
                    <!-- each file container -->
                    <div class="item-container" @click="togglePopUp('buttonTrigger'), updatePopupFile(fi)">
                        <!-- file icon container -->
                        <div id="file-icon">
                            <!-- flexible file icon -->
                            <FILE_icon :fileType="getFileType(fi.savedFileName)" :hasFileType="hasFileType(fi.savedFileName)"/>
                        </div>
                        <!-- file name -->
                        <div class="boxname">
                            {{ fi.savedFileName }}
                        </div>
                        <!-- sent time -->
                        <div class="boxtime">
                            {{ fi.savedTime.substring(11, 16) }}
                        </div>
                    </div>
                    <!-- file pop up when click each file -->
                    <FilePopup class="result-image" v-if="popupTrigger.buttonTrigger" :togglePopUp=" () => togglePopUp('buttonTrigger')" :filename="file_popup.filename" :fileid="file_popup.fileId" :senderid="file_popup.senderId" :datesent="file_popup.datesent" :timesent="file_popup.timesent" :filetype="file_popup.filetype" :filelink="file_popup.fileLink" :userId="userID" :senderName="file_popup.senderUserName" @reloadFileMenu="reloadFileLists">    
                    </FilePopup>
                </div>
            </div>
        </div>
    </div>
    <!-- if there is no file, or waiting for the file list -->
    <div class="no-file" v-if="Object.keys(groupedFiles).length<=0">
        {{isGotfile ? "ไม่พบไฟล์" : "กำลังโหลด"}}
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
        padding: 10px 30px 30px 30px;
    }
    .no-file{
        display: flex;
        width: 100%;
        height: 40vh;
        justify-content: center;
        align-items: center;
    }
    .file-grid-container{
        padding-bottom: 20px;
    }
    .files-date{
        margin-bottom: 3px;
        font-weight: 600;
    }
    .item-container{
        display: grid;
        width: 100%;
        height: 100%;
        align-items: center;
        margin-bottom: 6px;
        grid-template-columns: 0.7fr 3fr 1.3fr;
        border: none;
        border-bottom: 1px solid #DEDEDE;
        padding-bottom: 8px;

    }
    .item-container>img{
        width: 15vw;
        aspect-ratio: 1/1 ;
        border-radius: 100%;
    }
    #file-icon{
        color:black;
        display: flex;
        align-items: center;
    }
    .boxname{
        white-space: nowrap;
        color:black;
        text-overflow: ellipsis;
        overflow: hidden; 
        margin-right: 15px;
    }
    .boxtime{
        text-overflow: ellipsis;
        overflow: hidden; 
        display: flex;
        justify-content: flex-end;
        color: black;
    }
    .boxdownloadbutton{
        display: flex;
        justify-content: flex-end;
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
    import FILE_icon from "../icons/file_icon.vue"
    import { useRoute } from 'vue-router';
    import FilePopup from '../popup/manage_file_popup.vue'
    import ManageFileSearchbar from '../searchbar/manage_files_searchbar.vue'

    export default {
        components: {
            FILE_icon,
            FilePopup,
            ManageFileSearchbar,
        },
        data(){
            // declare default value
            return{
                popupTrigger: {
                    buttonTrigger: false,
                },
                file_popup:{
                    filename: "",
                    fileId: "",
                    senderId: "",
                    datesent: "",
                    timesent: "",
                    filetype: "",
                    fileLink: "",
                    senderUserName: "",
                },
            }
        },
        setup() {
            // declare variables
            const groupID = ref("");
            const groupGalleryFilesData = ref([]);
            const store = useStore();
            const groupedFiles = ref({});
            const userID = ref ("");
            const viewUserID = ref("")
            const route = useRoute();
            const isGotfile = ref(false);

            const filesSearch = ref([]);
            const searchQuery = ref("")
                
            const file_lastest_sorted = ref(true);

            // get file list in group
            const getGalleryFilesInfo_Group = async () => {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/file/sort_latest',
                        method: 'POST',
                        data: JSON.stringify({
                            groupId: groupID.value,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    });

                    // collect data to be used as default value from server
                    groupGalleryFilesData.value = response.data.sortLatest;
                    // collect data to be used for filter by keyword (search)
                    filesSearch.value = groupGalleryFilesData.value

                    // end page loading state 
                    isGotfile.value = true

                } catch (error) {
                    console.error('Error:', error.response);
                    // end page loading state 
                    isGotfile.value = true

                }
            };

            // get the file list that someone sent
            const getGalleryFilesInfo_Me = async () => {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/file/sort_latest',
                        method: 'POST',
                        data: JSON.stringify({
                            userId: viewUserID.value,
                            groupId: groupID.value,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });
                    // collect data to be used as default value from server
                    groupGalleryFilesData.value = response.data.sortLatest;
                    // collect data to be used for filter by keyword (search)
                    filesSearch.value = groupGalleryFilesData.value

                    // end page loading state 
                    isGotfile.value = true

                } catch (error) {
                    console.error('Error:', error.response.data);
                    // end page loading state 
                    isGotfile.value = true
                }
            };
            
            // reform the file list to be shown on page.
            const reFormFileGallery = (file_data:[]) =>{
                if (file_data) {
                    // create blank {}
                    var tempGroupedFiles = {}
                    // group the files by date
                    file_data.forEach(file => {
                        // get the sent date in all file to be key, and group all files sent at the same date in the same key. then reformat the key (date).
                        const date = file.savedTime.split("T")[0];
                        // if there is no some date key, just create the new one 
                        if (!tempGroupedFiles[date]) {
                            tempGroupedFiles[date] = [];
                        }
                        // push the file the date key it was sent.
                        tempGroupedFiles[date].push(file);
                    });
                    // show the result
                    groupedFiles.value = tempGroupedFiles
                }
                else {
                    console.error("can't reFormFileGallery()");
                }
            };

            // when initializing this page
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
                    localStorage.setItem('userID', groupID.value);
                }

                // get user id that is saved at localStorage
                const saveUserID = localStorage.getItem('userID');
                if (saveUserID && saveUserID.length > 0) {
                    // if there is user id at localStorage
                    userID.value = saveUserID;
                } else {
                    // if there is no user id at localStorage, get it from store
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
                    getGalleryFilesInfo_Group().then(async()=>{await reFormFileGallery(groupGalleryFilesData.value)})
                } else if (route.path == "/managefiles") {
                    // if it is viewing the file sent by each member, get list of all files sent in that group
                    getGalleryFilesInfo_Me().then(async()=>{await reFormFileGallery(groupGalleryFilesData.value)})
                }
            });
            return{
                groupID,
                userID,
                viewUserID,
                groupGalleryFilesData,
                groupedFiles,
                store,
                isGotfile,
                filesSearch,
                reFormFileGallery,
                route,
                getGalleryFilesInfo_Group,
                getGalleryFilesInfo_Me,
                searchQuery,
                file_lastest_sorted,
            }
        },
        methods: {
            // toggle pop up
            togglePopUp(trigger:string){
                this.popupTrigger[trigger] = !this.popupTrigger[trigger]
            },

            // update file info, and sender info to be shown in popup
            updatePopupFile(fi:{}){
                this.file_popup={
                    filename: fi.savedFileName,
                    fileId: fi.fileId,
                    senderId: fi.senderId,
                    datesent: this.changeDateForm(fi.savedTime.split('T')[0]),
                    timesent: fi.savedTime.substring(11, 16),
                    filetype: this.getFileType(fi.savedFileName),
                    fileLink: fi.fileLink,
                    senderUserName: fi.senderUserName,
                }
            },

            // get file type from file name
            getFileType(a:string){
                // get the last string after the last '.'
                return a.split('.').pop()
            },

            // is the file name have file type?
            hasFileType(a:string){
                return a.split('.').length>1
            },

            // change date from yyyy-mm-dd to thai form
            changeDateForm(date:string){
                // divide part into date, month and year.
                const arrdate = date.split('-')
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
                this.file_lastest_sorted = data;
                    // copy the key (date) and reverse it, from latest to newest or newest to latest.
                    const sortedKeys = Object.keys(this.groupedFiles).reverse();
                    // create black {}.
                    const sortedObject = {};       
                    // copy the data of each key to it
                    sortedKeys.forEach(key => {
                        sortedObject[key] = this.groupedFiles[key];
                    });
                    // reverse data inside each key
                    for (const key in sortedObject){
                        if (Array.isArray(sortedObject[key])) {
                            sortedObject[key].reverse();
                        }
                    }
                    // display the result
                    this.groupedFiles = sortedObject
            },

            // filter file from keyword
            searchFiles(searchQuery:string){
                this.searchQuery = searchQuery
                this.filesSearch = this.groupGalleryFilesData.filter(file => {
                    const fileNameLower = file.savedFileName.toLowerCase();
                    const searchQueryLower = searchQuery.toLowerCase();
                    return fileNameLower.includes(searchQueryLower);
                })
                this.reFormFileGallery(this.filesSearch)
            },

            // reload list of file
            reloadFileLists(isReload:boolean){
                // when popup make change (delete the file) to the file list.
                if(isReload){
                    // check the rendering page. this use different API.
                    if (this.route.path == "/gallery") {
                        // wait for request for file list
                        this.getGalleryFilesInfo_Group()
                        // then, wait for filter the current search key
                        .then(async()=>{
                            await this.searchFiles(this.searchQuery)
                        })
                        // then, wait for reform the list th be shown.
                        .then(async ()=> {
                            await this.reFormFileGallery(this.filesSearch)
                        })
                        // then ,sort in current sorting way
                        .then(async () => {
                            if(!this.file_lastest_sorted){
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
                        this.getGalleryFilesInfo_Me()
                        .then(async()=> {
                            await this.searchFiles(this.searchQuery)
                        })
                        // then, wait for filter the current search key
                        .then(async ()=> {
                            await this.reFormFileGallery(this.filesSearch)
                        })
                        // then ,sort in current sorting way
                        .then(async () => {
                            if(!this.file_lastest_sorted){
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
