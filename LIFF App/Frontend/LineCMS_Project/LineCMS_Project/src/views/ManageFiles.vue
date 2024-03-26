<script setup lang="ts">
    import ManageFilesTab from '../components/tab/manage_files_tab.vue'
    import ManageFilesSearchbar from '../components/searchbar/manage_files_searchbar.vue'
    import ManageFilesMenu from '../components/menu/manage_files_menu.vue'
    import ManagePicturesMenu from '../components/menu/manage_picture_menu.vue'
</script>

<template>
    <main>
        <!-- the button tab -->
        <ManageFilesTab :image_selected="image_selected" @dataToParent="handleDataFromChild" :reloadtab="isReload" @reset_isReload="resetReloadTab"/>
        <!-- the collection of pictures or files in the group -->
        <ManageFilesMenu v-if="image_selected==false" @reloadFileTab="reloadTab"/>
        <ManagePicturesMenu v-if="image_selected==true" @reloadFileTab="reloadTab " />
    </main>
</template>

<script lang="ts">
    export default {
        components: {
            ManageFilesTab,
            ManageFilesSearchbar,
            ManageFilesMenu,
            ManagePicturesMenu,
        },
        props:{
            image_selected:Boolean,
        },
        data(){
            // default collection showing
            return{
                image_selected: true,
                isReload:false,
            };
        },
        methods: {
            // change the collection to show
            handleDataFromChild(data) {
                this.image_selected = data;
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