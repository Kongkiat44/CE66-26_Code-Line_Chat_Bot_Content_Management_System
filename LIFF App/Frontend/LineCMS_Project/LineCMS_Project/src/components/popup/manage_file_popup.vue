<template>
    <!-- popup page for managing files (including shadow zone) -->
    <div class="popup">
        <!-- the area of popup menu -->
        <div class="popup-inner">
            <!-- popup info container -->
            <div class="info-container">
                <!-- title bar of popup -->
                <div class="titlebar-container">
                    <!-- file name -->
                    <div class="title-container">
                        <h3 class="filename">
                            {{filename}}
                        </h3>
                    </div>
                    <!-- close button -->
                    <button class="popup-close" @click="togglePopUp">
                        <img src="../pic/close.png"height="auto" width="15px"/>
                    </button>
                </div>
                <!-- file info and sending info -->
                <div class="sending-info-container">
                    <p class="sender-header">ผู้ส่ง:</p>
                    <p class="sender-p">{{ senderName }}</p>
                    <p class="sender-header">เวลา:</p>
                    <p class="sender-p">{{ datesent }} &nbsp; {{ timesent }} น.</p>
                    <p class="sender-header">ประเภท:</p>
                    <p class="sender-p">{{ filetype }}</p>
                </div>
                <!-- send to chat button -->
                <div class="download-button popup-button" @click="sendToChat()">
                    ส่งในแชท
                </div>
                <!-- remove button (show only if the user view his own file) -->
                <div class="remove-button popup-button" v-if="userId==senderid" @click="isRemove()">
                    ลบไฟล์
                </div>
            </div>
        </div>
    </div>
    <!-- pop up of removing file (include the shadow zone) when remove button is clicked -->
    <div class="popup-remove-file" v-if="click_remove_button">
        <!-- the area of removing file popup -->
        <div class="popup-remove-file-inner">
            <!-- question to user -->
            <div>
                <h2 class="popup-title">
                    คุณต้องการลบไฟล์นี้หรือไม่
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
    .titlebar-container{
        display: flex;
        justify-content: space-between;

        flex-wrap: wrap;
        margin-bottom: 12px;
        width: 100%;
    }
    .title-container{
        display: grid;
        grid-template-columns: 1fr auto;
        grid-template-rows: auto;
        max-width: 70%;
    }
    .filename{
        text-align: left;
        font-size: 150%;
        font-weight: 600;
        max-width: 80vw;
        white-space: wrap;
        text-overflow: ellipsis;
        word-break: break-word;
        line-height: 1.3em;
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

    .popup{
        position:fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 100;
        background-color: rgba(0,0,0,0.06);
        display: flex;
        align-items: end;
        justify-content: stretch;
        width: 100vw;
        height: 100vh;
        
        .popup-inner{
            border-radius: 30px 30px 0px 0px; 
            height: auto;
            width: 100vw;
            background: #fff;
            display:flex;
            justify-content: stretch;
            box-shadow: 0px 0px 20px 5px rgba(0, 0, 0, 0.02);
        }
    }
    .info-container{
        width: 100%;
        margin: 30px;
    }
    .change-filename-button{
        margin-left: 10px
    }
    .sending-info-container{
        display: grid;
        grid-gap: 8px;
        grid-template-columns: 1fr 2.3fr;
        grid-template-rows: 1fr 1fr 1fr;
        border-top: solid #DEDEDE 2px;
        border-bottom: solid #DEDEDE 2px;
        font-size: 125%;
        margin-left: -30px;
        margin-right: -30px;
        padding-left: 30px;
        padding-right: 30px;
        padding-top: 10px;
        padding-bottom: 10px;
        width: 100vw

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
    import {API_URL} from "../../myPlugin"
    import axios from 'axios';

    export default {
        name: "PicPopup",
        props:{
            togglePopUp: Boolean,
            filename: String,
            fileid: String,
            senderid: String,
            datesent: String,
            timesent: String,
            filetype:String,
            filelink: String,
            userId: String,
            senderName: String,
        },
        data() {
            // default state value
            return{
                fetchSuccess: false,
                isGotfile: false,
                click_remove_button : false,
                deleteSuccess: false,
            }  
        },
        methods:{
            // send selected file to LINE private chat, using file id and user id
            async sendToChat () {
                this.click_remove_button = false;
                try {
                    const response = await axios.request({
                        url: API_URL+'/data/file/fetch_one',
                        method: 'POST',
                        data: JSON.stringify({
                            fileId: this.fileid,
                            userId: this.userId,
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        timeout: 5000,
                    });
                    this.fetchSuccess = response.data.fetchSuccess;

                    // if the request is success, just close the popup
                    if(this.fetchSuccess){
                        this.togglePopUp()
                    }
                } catch (error) {
                    console.error('Error:', error.response);

                }
            },
            // show the removing file popup if the remove button is clicked
            isRemove(){
                this.click_remove_button = true;
            },
            // to close the popup if the user cancel the removing process.
            closePopup(){
                this.click_remove_button = false;
            },
            // if user confirm for deleting file, tell the server for removing request (file id and user id are needed for rechecking the owner right.)
            async deleteContent (){
                try {
                    const response = await axios.request({
                    url: API_URL+'/data/file/delete_one',
                    method: 'POST',
                    data: JSON.stringify({
                        fileId: this.fileid,
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
                    this.$emit('reloadFileMenu', this.deleteSuccess);

                } catch (error) {
                    console.error('Error:', error.response);
                }
            }
        }
    }
</script>