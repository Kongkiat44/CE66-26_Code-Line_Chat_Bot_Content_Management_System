<template>
    <!-- when user use external browser -->
    <div class="status-container">
        <!-- icon -->
        <img id="icon" src="../components/pic/warning_icon.png" alt="warning_pic">
        <!-- message -->
        <h1 id="title">กรุณาใช้งาน<br>บนแอปพลิเคชั่นไลน์</h1>
    </div>
</template>

<style>
    .status-container {
        min-height: 100vh;
        display: grid;
        grid-template-columns: 1fr;
        grid-template-rows: 0.8fr 1fr;
        align-items: center;
        text-align: center;
        justify-content: center;
        grid-gap: 10px;
    }
    #icon{
        width: 30vw;
        justify-self: center;
        align-self: end;
    }
    #title{
        justify-self: center;
        align-self:  flex-start;
        text-align: center;
        padding-top: 20px;
    }
</style>
