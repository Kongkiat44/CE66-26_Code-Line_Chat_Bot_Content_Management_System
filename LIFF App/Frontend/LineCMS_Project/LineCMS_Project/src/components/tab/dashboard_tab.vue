<template>
    <!-- form of the tab button -->
    <form class="menu-container">
        <!-- image button -->
        <button class="btn" id="classnumber1_container" @click="clickImages();" :style='{borderColor: image_selected ? "#544E4E" : "#E9E9E9"}'>
            <!-- group images info -->
            <div class="number-container">
                <!-- title and icon -->
                <div>
                    <!-- title of image button -->
                    <p class="classnumber" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                        รูปภาพ
                    </p>
                    <!-- icon -->
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="arrow-right">
                        <path :style='{strokeWidth:"1", stroke: image_selected ? "#E9E9E9" : "#9D9D9D", fill: image_selected ? "#E9E9E9" : "#9D9D9D"}' 
                            d="M16.2424621,12.7424621 L10.2424621,18.7424621 C9.83241161,19.1525126 9.16758839,19.1525126 8.75753788,18.7424621 C8.34748737,18.3324116 8.34748737,17.6675884 8.75753788,17.2575379 L14.0150758,12 L8.75753788,6.74246212 C8.34748737,6.33241161 8.34748737,5.66758839 8.75753788,5.25753788 C9.16758839,4.84748737 9.83241161,4.84748737 10.2424621,5.25753788 L16.2424621,11.2575379 C16.6525126,11.6675884 16.6525126,12.3324116 16.2424621,12.7424621 L16.2424621,12.7424621 Z">
                        </path>
                    </svg>
                </div>
                <!-- images count -->
                <p class="totalnumber" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                    {{groupGalleryData.imageTotalCount}}
                </p>
                <!-- show memory used for images in TB/GB/MB/KB -->
                <p class="totalMemory" v-if="groupGalleryData.imageTotalSizeByte>=1000000000000" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.imageTotalSizeByte/1000000000000).toFixed(2)}} TB
                </p>
                <p class="totalMemory" v-else-if="groupGalleryData.imageTotalSizeByte>=1000000000" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.imageTotalSizeByte/1000000000).toFixed(2)}} GB
                </p>
                <p class="totalMemory" v-else-if="groupGalleryData.imageTotalSizeByte>=1000000" :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.imageTotalSizeByte/1000000).toFixed(2)}} MB
                </p>
                <p class="totalMemory" v-else :style='{color: image_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.imageTotalSizeByte/1000).toFixed(2)}} KB
                </p>
            </div>
        </button>

        <!-- file button -->
        <button class="btn" id="classnumber2_container" @click="clickFiles();" :style='{borderColor: file_selected ? "#544E4E" : "#E9E9E9"}'>
            <!-- group files info -->
            <div class="number-container">
                <!-- title and icon -->
                <div>
                    <!-- title of file button -->
                    <p class="classnumber" :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>ไฟล์</p>
                    <!-- icon -->
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="arrow-right">
                        <path :style='{strokeWidth:"1", stroke: file_selected ? "#E9E9E9" : "#9D9D9D", fill: file_selected ? "#E9E9E9" : "#9D9D9D"}'
                            d="M16.2424621,12.7424621 L10.2424621,18.7424621 C9.83241161,19.1525126 9.16758839,19.1525126 8.75753788,18.7424621 C8.34748737,18.3324116 8.34748737,17.6675884 8.75753788,17.2575379 L14.0150758,12 L8.75753788,6.74246212 C8.34748737,6.33241161 8.34748737,5.66758839 8.75753788,5.25753788 C9.16758839,4.84748737 9.83241161,4.84748737 10.2424621,5.25753788 L16.2424621,11.2575379 C16.6525126,11.6675884 16.6525126,12.3324116 16.2424621,12.7424621 L16.2424621,12.7424621 Z">
                        </path>
                    </svg>
                </div>
                <!-- files count -->
                <p class="totalnumber" :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>
                    {{groupGalleryData.fileTotalCount}}
                </p>
                <!-- show memory used for files in TB/GB/MB/KB -->
                <p class="totalMemory" v-if="groupGalleryData.fileTotalSizeByte>=1000000000000" :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.fileTotalSizeByte/1000000000000).toFixed(2)}} TB
                </p>
                <p class="totalMemory" v-else-if="groupGalleryData.fileTotalSizeByte>=1000000000" :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.fileTotalSizeByte/1000000000).toFixed(2)}} GB
                </p>
                <p class="totalMemory" v-else-if="groupGalleryData.fileTotalSizeByte>=1000000" :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.fileTotalSizeByte/1000000).toFixed(2)}} MB
                </p>
                <p class="totalMemory" v-else :style='{color: file_selected ? "#535353" : "#9D9D9D"}'>
                    {{(groupGalleryData.fileTotalSizeByte/1000).toFixed(2)}} KB
                </p>
            </div>
        </button>
    </form>
</template>

<style scoped>

    .menu-container{
        display:grid;
        grid-gap: 15px;
        justify-items: stretch;
        grid-template-columns: repeat(2, 1fr);
        height: 18vh;
        justify-content: center;
        align-items: center;
        padding: 5% 30px 5% 30px;
    }
    .btn{
        padding: 0px;
        margin: 0px;
        width: 100%;
        height: 100%;
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
        font-size: 125%;
        font-weight: 600;
        margin: 4px 0px 0px 4px;
        text-align: start;
    }
    .totalnumber{
        color: #000;
        align-self: center;
        font-size: 250%;
        font-weight: 600;
        text-align: right;
        margin: 0px 10px -5px 0px;
    }
    .totalMemory{
        text-align: end;
        margin: 0px 10px 5px 0px;
        font-size: 100%;

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
            file_selected: Boolean,
            reloadtab: Boolean,
        },

        data(props) {
            // default showing member/image/file list from parent
            return {
                image_selected: this.image_selected,
                file_selected: this.file_selected,
                reloadtab: props.reloadtab,
            };
        },
        setup() {
            // declare variables
            const store = useStore()
            const groupID = ref("")
            const groupGalleryData = ref(Object)

            // get amount of pictures and files sent of selected group by group id.
            const getGalleryInfo = async () => {
                try {
                    const response = await axios.request({
                    url: API_URL+'/data/group/file_info',
                    method: 'POST',
                    data: JSON.stringify({
                        groupId: groupID.value,
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    timeout: 5000,
                    });
                    groupGalleryData.value = response.data;
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
                    // then save group id from store to localStorage
                    localStorage.setItem('groupID', groupID.value);
                }
                getGalleryInfo();
            });

            return{
                store,
                groupID,
                groupGalleryData,
                getGalleryInfo,
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
                        this.getGalleryInfo().then(()=>{
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
                // if image button is not selected previously, so user want to view group image info.  
                if(this.image_selected == false){
                    this.image_selected = true;
                    this.file_selected = false;
                    event?.preventDefault();
                    // tell the parent to show group's images info
                    this.$emit('dataToParent', "image_selected");
                }
                // if image button is selected previously, so user want to view group member info.  
                else{
                    this.image_selected = false;
                    this.file_selected = false;
                    event?.preventDefault();
                    // tell the parent to show group's member info
                    this.$emit('dataToParent', "default_selected");
                }
            },
            // if image button is clicked
            clickFiles(){
                // if file button is not selected previously, so user want to view group file info.  
                if(this.file_selected == false){
                    this.file_selected = true;
                    this.image_selected = false;
                    event?.preventDefault();
                    // tell the parent to show group's files info
                    this.$emit('dataToParent', "file_selected");
                }
                // if file button is selected previously, so user want to view group member info.  
                else{
                    this.image_selected = false;
                    this.file_selected = false;
                    event?.preventDefault();
                    // tell the parent to show group's member info
                    this.$emit('dataToParent', "default_selected");
                }
            },
        }
    }
</script>