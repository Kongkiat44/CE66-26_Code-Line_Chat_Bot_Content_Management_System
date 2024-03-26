<template>
    <!-- popup page for managing pictures (including shadow zone) -->
    <div class="popup">
        <!-- previewed picture -->
        <div class="popup-pic">
            <img :src="imgsrc" height="auto" width="100%"/>
        </div>
        <!-- the area of popup menu -->
        <div class="popup-inner">
            <!-- popup info container -->
            <div class="info-container">
                <!-- title bar of popup -->
                <div class="titlebar-container">
                    <!-- the image file type -->
                    <div class="title-container">
                        <h2 class="filename">
                            {{imgtype.toUpperCase()}}&nbsp;Image
                        </h2>
                    </div>
                    <!-- close button -->
                    <button class="popup-close" @click="togglePopUp()">
                        <img src="../pic/close.png"height="auto" width="15px"/>
                    </button>
                </div>
                <!-- picture info and sending info. The if case is for only showing the picture in gallery or manage file page -->
                <div class="sending-info-container" v-if="senderName">
                    <p class="sender-header">ผู้ส่ง:</p>
                    <p class="sender-p">{{ senderName }}</p>
                    <p class="sender-header">เวลา:</p>
                    <p class="sender-p">{{ datesent }} &nbsp; {{ timesent }} น.</p>
                </div>
                <!-- the else case is for preview the images list from the cluster search, there is no sending info sent from server -->
                <div v-else class="no-sending-info-container"></div>
                <!-- send to chat button -->
                <div class="download-button popup-button" @click="sendToChat()">
                    ส่งในแชท
                </div>
                <!-- remove button (show only if the user view his own picture) -->
                <div class="remove-button popup-button" v-if="userId==senderid" @click="isRemove()">
                    ลบรูปภาพ
                </div>
            </div>
        </div>
    </div>
    <!-- pop up of removing picture (include the shadow zone) when remove button is clicked -->
    <div class="popup-remove-file" v-if="click_remove_button">
        <!-- the area of removing picture popup -->
        <div class="popup-remove-file-inner">
            <!-- question to user -->
            <div>
                <h2 class="popup-title">
                    คุณต้องการลบรูปนี้หรือไม่
                </h2>
            </div>
            <!-- buttons area -->
            <div class="button-container">
                <!-- confirm to delete button -->
                <div class="button-name" id="remove-btn" @click="deleteContent()">
                    <h2>ลบ</h2>
                </div>
                <!-- cancel button -->
                <div class="button-name" id="cancel-btn" @click="closePopup()">
                    <h2>ยกเลิก</h2>
                </div>
            </div>
        </div>

    </div>
</template>

<style scoped lang="scss">

    button{
        background-color: rgba($color: #fff, $alpha: 0);
        border: none;
    }
    h2{
        text-align: center;
        font-weight: 600;
    }
    .popup-remove-file{
        position:fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 100;
        background-color: rgba(0,0,0,0.6);
        display: flex;
        justify-content: center;
        align-items: center;

        .popup-remove-file-inner{
            border-radius: 20px; 
            height: 15vh;
            width: 80vw;
            background: #fff;
            display:grid;
            padding: 3% 3% 5% 3%;
            grid-template-columns: 1fr;
            grid-template-rows: 2fr 1fr;
        }
    }
    .button-container{
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr;
        text-align: center
    }

    .popup{
        position:fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 100;
        background-color: rgba(0,0,0,1);
        display: grid;
        grid-template-columns: 1fr;
        grid-template-rows: 1fr auto;

        width: 100vw;
        height: 100vh;
        .popup-inner{
            border-radius: 30px 30px 0px 0px; 
            height: auto;
            width: 100vw;
            background: #fff;
            display:flex;
            justify-content: stretch;
            box-shadow: 0px -5px 15px 5px rgba(0, 0, 0, 0.15);
        }

    }
    
    .popup-title{
        font-size:150%;
    }

    #remove-btn{
        border-right: solid 1px #DEDEDE;
        color: #FF0000;
    }
    #cancel-btn{
        border-left: solid 1px #DEDEDE;
        color: #157DF7;
    }

    .popup-pic{
        display:flex;
        justify-content: center;
        align-items: center;
        flex-wrap:wrap;
        height:auto;
        max-height: 60vh;
        width: 100%;
        margin-bottom: -30px;

    }
    .info-container{
        width: 100%;
        margin: 30px;
        align-self: end;
    }
    .change-filename-button{
        margin-left: 10px
    }
    .filename{
        max-width:60%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .titlebar-container{
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        width: 100%;

    }
    .title-container{
        width: 100%;
        display: flex;
        flex-wrap: wrap;
    }
    .popup-close{
        
    }
    .sending-info-container{
        display: grid;
        grid-gap: 8px;
        grid-template-columns: 1fr 4fr;
        grid-template-rows: 1fr 1fr;
        border-top: solid #DEDEDE 2px;
        border-bottom: solid #DEDEDE 2px;
        font-size: 125%;
        margin-left: -30px;
        margin-right: -30px;
        padding-left: 30px;
        padding-right: 30px;
        padding-top: 10px;
        padding-bottom: 10px;
        margin-bottom: 10px;
        width: 100vw
    }

    .no-sending-info-container{
        margin-left: -30px;
        margin-right: -30px;
        margin-bottom: 10px;
        width: 100vw;
        height: 0;
        border-bottom: solid #DEDEDE 2px;

    }
    .sender-header{
        font-weight: 400;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        
    }
    .sender-p{
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .popup-button{
        width: 100%;
        justify-content: center;
        text-align:center;
        font-weight: 800;
        font-size: 125%;
        padding: 8px;
    }
    .download-button{
        color: #157DF7;
    }
    .remove-button{
        border-top: solid 2px #DEDEDE;
        color: #FF0000;
    }
</style>

<script lang="ts">
    import axios from 'axios';
    import {API_URL} from "../../myPlugin"

    export default {
        name: "PicPopup",
        data() {
            // default state button
            return{
                fetchSuccess: false,
                isGotImage: false,
                click_remove_button : false,
                deleteSuccess:false,
            }  
        },
        props:{
            togglePopUp: Boolean,
            imgid: String,
            senderid: String,
            datesent: String,
            timesent: String,
            imgtype:String,
            imgsrc: String,
            userId: String,
            senderName: String,
        },

        methods:{
            // show the removing picture popup if the remove button is clicked
            isRemove(){
                this.click_remove_button = true;
            },
            // to close the popup if the user cancel the removing process.
            closePopup(){
                this.click_remove_button = false;
            },
            // send selected picture to LINE private chat, using file id and user id
            async sendToChat () {
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/image/fetch_one',
                        method: 'POST',
                        data: JSON.stringify({
                            imageId: this.imgid,
                            userId: this.userId,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });
                    this.fetchSuccess = response.data.fetchSuccess;
                    
                    if(this.fetchSuccess){
                        this.togglePopUp()
                        this.click_remove_button = false;
                    }

                } catch (error) {
                    console.error('Error:', error.response);

                }
            },
            // if user confirm for deleting picture, tell the server for removing request (image id and user id are needed for rechecking the owner right.)
            async deleteContent (){
                try {
                    const response = await axios.request({
                    url: API_URL+'/data/image/delete_one',
                    method: 'POST',
                    data: JSON.stringify({
                        imageId: this.imgid,
                        userId: this.userId,
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    timeout: 5000,
                    });
                    this.deleteSuccess = response.data.deleteSuccess;

                    // if the deleting is successed, close all popup.
                    if(this.deleteSuccess){
                        this.togglePopUp()
                        this.closePopup()
                    }
                    // tell the parent to reload the files and images count.
                    this.$emit('reloadPicMenu', this.deleteSuccess);

                } catch (error) {
                    console.error('Error:', error.response);
                }
            }
        }
    }
</script>