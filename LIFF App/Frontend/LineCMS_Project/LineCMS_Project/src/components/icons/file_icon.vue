<template>
    <!-- icon container -->
    <div class="icon-box" :style='{backgroundColor:setColor_IconBox(fileType), borderColor:setBorderColor_IconBox(fileType)}'>
        <!-- fliped corner -->
        <div class="corner">
            <div class="flip-corner" :style='{borderColor:setColor_FlipCorner(fileType)}'></div>
            <div class="no-corner"></div>
        </div>
        <!-- area of file type box -->
        <div class="file-type-zone">
            <!-- file type container -->
            <div class="file-type-container">
                <!-- name of file type -->
                <div class="file-type-box" :style='{backgroundColor:setColor_FileTypeBox(fileType), borderColor:setBorderColor_FileTypeBox(fileType)}'>
                    <p class="file-type" :style='{color: setFontColor(fileType)}'>{{ fileTypeFilter(fileType) }}</p>
                </div>
            </div>
        </div>
    </div>
    
</template>
<style scoped>
    .icon-box{
        display: grid;
        grid-template-rows: 1fr 3fr;
        grid-template-columns: 1fr;
        height: 40px;
        width: 30px;
        border-radius: 5px;
        border: 1.5px solid ;
        
    }
    .corner{
        display: flex;
        justify-content: end;
    }
    .no-corner{
        width: 0;
        height: 0;
        border-right: 12px solid white;
        border-bottom: 12px solid transparent;
        margin-right: -2.5px;
        margin-top: -2px;
    }
    .flip-corner{
        margin-right: -10px;
        margin-top: -0.5px;
        width: 0;
        height: 0;
        border-left: 10px solid;
        border-top: 10px solid transparent;
        border-radius: 0px 0px 0px 5px;
    } 
    .file-type-zone{
        display: flex;
        justify-content: flex-end;
        justify-self: end;
        width:30px;
    }
    .file-type-container{
        display: flex;
        justify-content: flex-end;
        max-width: 40px;

    }
    .file-type-box{
        margin-top: 6px;
        margin-right: 5px;
        height: 16px;
        min-width: 28.5px;
        width: auto;
        margin-left: -3px;
        display: flex;
        align-content: center;
        justify-content: center;
        border: 1.5px solid;
        align-items: center;
        border-radius: 3px;

    }
    .file-type{
        text-align: center;
        text-overflow: clip;
        white-space: nowrap;
        overflow: hidden;
        font-size: 12px;
        font-weight: 600;
        color: 999;
        padding: 0px 1px 0px 1px;
    }
    
</style>

<script lang="ts">
    export default {
        name: 'file-type',
        props:{
            fileType:String,
            hasFileType:Boolean,
        },
        methods:{
            // get file type (length: 1-4 char)
            fileTypeFilter(a:string){
                if (this.hasFileType===true){
                    return a.substring(0,4).toUpperCase();
                }
                // if no file type
                else {
                    return "..."; 
                }
            },
            // set main color of icon
            setColor_IconBox(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="TXT" || temp_fileType==="TEXT" ){
                    return "#BBB";
                }
                else{
                    return "white"
                }
            },
            // set border color of icon
            setBorderColor_IconBox(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="TXT" || temp_fileType==="TEXT" ){
                    return "#777";
                }
                else if(temp_fileType==="DOCX"){
                    return "#325B9C";
                }
                else if(temp_fileType==="PDF"){
                    return "#F40F02";
                }
                else{
                    return "#999"
                }
            },
            // set color of flip corner
            setColor_FlipCorner(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="TXT" || temp_fileType==="TEXT" ){
                    return "#777";
                }
                else if(temp_fileType==="DOCX"){
                    return "#254374";
                }
                else if(temp_fileType==="PDF"){
                    return "#ca0c02";
                }
                else{
                    return "#999";
                }
            },
            // set background color of file type box
            setColor_FileTypeBox(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="TXT" || temp_fileType==="TEXT" ){
                    return "white";
                }
                else if(temp_fileType==="DOCX"){
                    return "#325B9C";
                }
                else if(temp_fileType==="PDF"){
                    return "#F40F02";
                }
                else{
                    return "#CCC";
                }
            },
            // set border color of file type box
            setBorderColor_FileTypeBox(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="TXT" || temp_fileType==="TEXT" ){
                    return "#777";
                }
                else if(temp_fileType==="DOCX"){
                    return "#325B9C";
                }
                else if(temp_fileType==="PDF"){
                    return "#F40F02";
                }
                else{
                    return "#777";
                }
            },
            // set font color of file type
            setFontColor(a:string){
                let temp_fileType = this.fileTypeFilter(a);
                if(temp_fileType==="DOCX" || temp_fileType==="PDF"){
                    return "white";
                }
                else{
                    return "black";
                }
            },
        }
    }
</script>
