<template>
    <!-- status container -->
    <div class="status-container">
        <!-- success button if request is success -->
        <img src="../pic/check_icon.png" v-if="status==200" alt="success_pic" height="auto" width="auto">
        <!-- warning icon if request is unsuccess -->
        <img src="../pic/warning_icon.png" v-else-if="status==400" alt="warning_pic" height="auto" width="auto">
        <!-- waiting icon if request is not reponsed -->
        <img src="../pic/waiting_icon.png" v-else alt="waiting_pic" height="auto" width="auto">
        <!-- show in message to user that, the request is success -->
        <div v-if="status==200">
            <h1>
                ส่งคำขอเรียบร้อยแล้ว
            </h1>
            <p>
                ระบบจะดำเนินการส่งในแชทส่วนตัว
            </p>
        </div>
        <!-- show in message to user that, the request has a problem -->
        <div v-else-if="status==400">
            <h1>
                ส่งคำขอไม่สำเร็จ
            </h1>
            <p>
                สามารถส่งคำขออีกครั้งได้ในภายหลัง
            </p>
        </div>
        <!-- show in message to user to wait for the response -->
        <div v-else>
            <h1>
                กำลังส่งคำขอ
            </h1>
            <p>
                กรุณารอสักครู่
            </p>
        </div>
    </div>
    <!-- available green button if request is success -->
    <div v-if="status==200" class="success-link">
        <router-link class="router-link" :to="{path: '/selectmenu'}">
            <div class="back-to-line success-button">
                <div>
                    กลับหน้าเมนู
                </div>
            </div>
        </router-link>
    </div>
    <!-- available orrange button if request is fail -->
    <div v-else-if="status==400" class="unsuccess-link">
        <router-link class="router-link" :to="{path: '/selectmenu'}">
            <div class="back-to-line unsuccess-button">
                <div>
                    กลับหน้าเมนู
                </div>
            </div>
        </router-link>
    </div> 
    <!-- unavailable if waiting for response -->
    <div v-else class="disable-link">
        <div class="back-to-line disable-button">
            <div>
                กลับหน้าเมนู
            </div>
        </div>
    </div>
    
</template>

<style scoped>
    #img-linegroup{
        border-radius: 100%;
        border: 1px solid #000;
    }
    .status-container{
        display:grid;
        justify-items: center;
        align-content: center;
        height:75vh;
        margin: 0px 30px 0px 30px;
    }

    .status-container>img{
        margin-bottom: 15px;
        max-width: 30vw;
    }
    .status-container>div{
        text-align: center;;
    }
    .status-container>div>h1{
        font-size: 25px;
        font-weight: 600;
    }
    .status-container>div>p{
        font-size: 18px;
        font-weight: 500;
    }
    .back-to-line{
        display: flex;
        justify-content: center;
        align-items: center;
        height:8vh;
        margin: 0px 30px 0px 30px;
        border-radius: 25px;
        color: white;
    }
    .success-button{
        background-color: #1D9300;
    }
    .unsuccess-button{
        background-color: #FEA832;
    }
    .disable-button{
        background-color: #AAA;
    }
    .router-link{
        padding: 0px;
    }
    .back-to-line>div{
        font-size: 25px;
        font-weight: 800;
    }

</style>

<script lang = "ts">
    import axios from "axios"
    import {API_URL} from "../../myPlugin"
    import { useStore } from 'vuex';
    import { ref, onMounted, onBeforeUnmount } from 'vue';

    export default {

    setup() {
        // declare variables
        const store = useStore()
        const userID = ref("")
        const clusterID = ref("")
        const status =  ref(0)
        const serverResponse = ref(null)

        // send the graph request, and looking for the request response.
        const sendGraphCreateRequest = async () => {
            // try to request by, user id of and the cluster id that he is looking for the relation
            try {
                const response = await axios.request({
                url: API_URL+'/graph/create_graph',
                method: 'POST',
                data: JSON.stringify({
                    userId: userID.value,
                    clusterId: clusterID.value
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: 5000,
                });
                serverResponse.value = response.data.requestSuccess;
                // self define status value by the number.
                if (serverResponse.value == true){
                    status.value = 200 // success
                }
                else{
                    status.value = 400 // fail in any error
                }

            } catch (error) {
                console.error('Error:', error.response.data);
            }
        };

        // when initialize this page
        onMounted(() => {
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

            // get cluster id that is saved at localStorage
            const saveClusterID = localStorage.getItem('clusterSampleID');
            if (saveClusterID && saveClusterID.length > 0) {
                // if there is cluster id at localStorage
                clusterID.value = saveClusterID;
            } else {
                clusterID.value = store.state.cluster_ID;
                // then save cluster id from store to localStorage
                localStorage.setItem('clusterSampleID', clusterID.value);
            }
            sendGraphCreateRequest();
            
        });
        return{
            userID,
            clusterID,
            store,
            status,
            serverResponse,
        }
    },
};
</script>