<script setup lang="ts">
    import DashboardTab from '../components/tab/dashboard_tab.vue'
    import DashboardMenu from '../components/menu/dashboard_menu.vue'
    import ManageFilesMenu from '../components/menu/manage_files_menu.vue'
    import ManagePicturesMenu from '../components/menu/manage_picture_menu.vue'
</script>

<template>
    <main>
        <!-- the button tab -->
        <DashboardTab :image_selected="image_selected" :file_selected="file_selected" @dataToParent="handleDataFromChild" :reloadtab="isReload"  @reset_isReload="resetReloadTab"/>
        <!-- the collection of members or pictures or files in the group -->
        <ManagePicturesMenu v-if="showType=='image_selected'"@reloadFileTab="reloadTab"/>
        <ManageFilesMenu v-else-if="showType=='file_selected'" @reloadFileTab="reloadTab"/>
        <DashboardMenu v-else-if="showType=='default_selected'" />
    </main>
</template>

<script lang="ts">
    export default {
        components: {
            DashboardTab,
            DashboardMenu,
        },
        data(){
            // default collection showing
            return{
                image_selected: false,
                file_selected: false,
                showType: "default_selected",
                isReload: false,
            };
        },
        methods: {
            // change the collection to show
            handleDataFromChild(data) {
                this.showType = data;
                // if member collection
                if(this.showType == "default_selected"){
                    this.image_selected= false;
                    this.file_selected= false;
                }
                // if image collection
                else if(this.showType == "image_selected"){
                    this.image_selected= true;
                    this.file_selected= false;
                }
                // if file selection
                else if(this.showType == "file_selected"){
                    this.image_selected= false;
                    this.file_selected= true;
                }
              console.log("data"+data);
            },
            // reload the tab
            reloadTab(isReload:boolean){
                this.isReload = isReload

            },
            // after the reload is success. just end the reload process.
            resetReloadTab(status:boolean){
                this.isReload = false
            }
        }
    }
</script>