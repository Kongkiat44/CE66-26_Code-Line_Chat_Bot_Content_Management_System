<template>
    <!-- sample image of selected cluster -->
    <div class="sample-image-container">
        <img id="sample-image" :src="clusterSampleImage" alt="sample-pic">
    </div>
    <!-- collection of images of selected cluster -->
    <ul class="imageresult-container">
        <!-- loop to show all image in the list -->
        <li
            v-for='image in images_list '
        >
            <!-- each image -->
            <div class="item-container" @click="togglePopUp('buttonTrigger'), updatePopupImg(image)">
                <img class="result-image" :src= 'image' alt="user_pic">
            </div>
        </li>
    </ul> 
    <!-- if image is clicked, pop up show -->
    <PicPopup v-if="popupTrigger.buttonTrigger" :togglePopUp=" () => togglePopUp('buttonTrigger')" :imgid="getRidOfLink(img_popup.imageLink)" :senderid="img_popup.senderId" :datesent="img_popup.datesent" :timesent="img_popup.timesent" :imgtype=img_popup.imgtype :imgsrc="img_popup.imageLink" :userId="userID" :senderName="img_popup.senderUserName">    
    </PicPopup>
</template>

<style scoped>
    .sample-image-container{
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        padding: 25px
    }
    #sample-image{
        height: 15vh;
        max-width: 80vw;
        border-radius: 100px;
        aspect-ratio: 1/1;
        border: 2px solid #DEDEDE
    }
    .imageresult-container{

        list-style: none;
        column-gap: 0;
        padding: 0;
        column-count: 2;
    }
    .result-image{
        width: 100%;
    }
    .item-container{
        display: flex;
        flex-wrap: wrap;
        break-inside: avoid;
    }
    .router-link{
        padding: 0px;
        margin: 0px;
    }
    img{
        
        border: 3px solid white;
        padding: 0px;
        margin: 0px;
    }

</style>

<script lang="ts">
    import axios from "axios"
    import {API_URL, IP_API_URL} from "../../myPlugin"
    import { ref, onMounted } from 'vue';
    import { useStore } from 'vuex';
    import PicPopup from '../popup/manage_pic_popup.vue'

    export default {
        components:{
            PicPopup,
        },
        data(){
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
            const store = useStore();
            const clusterSampleImage = ref("")
            const images_list = ref([])
            const clusterSampleID = ref("")
            const groupID = ref("")
            const userID = ref("")

            // when initialize this page
            onMounted(() => {
                // get a sample image link of the selected cluster that is saved at localStorage
                const saveClusterSampleImage = localStorage.getItem('clusterSampleImage');
                if (saveClusterSampleImage && saveClusterSampleImage.length > 0) {
                    // if there is the link at localStorage
                    clusterSampleImage.value = saveClusterSampleImage;
                } else {
                    // if there is no link at local storage, get it from store
                    clusterSampleImage.value = store.state.cluster_sample_image;
                    // then save link to localStorage
                    localStorage.setItem('clusterSampleImage', clusterSampleImage.value);
                }

                // get user id of user using the LIFF app that is saved at localStorage
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

                // get a cluster id of the selected cluster that is saved at localStorage
                const saveClusterSampleID = localStorage.getItem('clusterSampleID');
                if (saveClusterSampleID && saveClusterSampleID.length > 0) {
                    // if there is the cluster id at localStorage
                    clusterSampleID.value = saveClusterSampleID;
                } else {
                    // if there is no cluster id at local storage, get it from store
                    clusterSampleID.value = store.state.cluster_ID;
                    // then save cluster id from store to localStorage
                    localStorage.setItem('clusterSampleID', clusterSampleID.value);
                }

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
            });
            return {
                clusterSampleImage,
                images_list,
                clusterSampleID,
                groupID,
                userID,
            };
        },
        // when the page is mounted, get the selected cluster image list.
        mounted(){
            this.getCluster();
        },
        methods:{
            // get cluster image list
            async getCluster() {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/image/search_by_face',
                        method: 'POST',
                        data: JSON.stringify({
                            clusterId: this.clusterSampleID,
                            groupId: this.groupID,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    })
                    .then(response => {
                        this.images_list = response.data.imageLinkList;
                    })
                    .catch(error => {
                        console.error('Error:', error.response.data);
                    });
                }
                catch (error) {
                    console.error('Error fetching data:', error);
                }
            },
            // trigger the pop up
            togglePopUp(trigger:string){
                this.popupTrigger[trigger] = !this.popupTrigger[trigger];
            },
            // update value of the popup
            updatePopupImg(img:string){
                // update the file type of the image
                this.img_popup.imgtype = this.getFileType(img);
                // update the link of the image
                this.img_popup.imageLink = img;
            },
            // get file type of image from imageLink
            getFileType(a:string){
                // get the last string after the last '.'
                return a.split('.').pop()
            },
            // change date from yyyy-mm-dd to thai form
            changeDateForm(date:string){
                // get only the date part from time stamp, and divide it to date, month and year
                const arrdate = date.split('T')[0].split('-')
                let dd = arrdate[2]
                let mm = arrdate[1]
                let yy = arrdate[0]

                // change month form
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

                // connect datte, month and year
                return dd + " " + mm + " " + yy
            },
            // get image id
            getRidOfLink(link:string){
                return link.replace(IP_API_URL+"/linecms/image/","")
            }
        }
    }
</script>

