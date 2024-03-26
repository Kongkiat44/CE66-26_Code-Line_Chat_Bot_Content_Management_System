<script setup lang="ts">
    import { RouterView } from 'vue-router'
    import Titlebar from './components/titlebar/titlebar.vue';
</script>

<template class="no-select">
    <header >
        <!-- title bar container, in portrait mode -->
        <div class="wrapper" v-if="isPortrait">
            <!--  title bar -->
            <Titlebar/>
        </div>
    </header>
    <!-- can use any page if use in portrait mode -->
    <RouterView v-if="isPortrait"/>
    <!-- if landscape mode, just render this page -->
    <div class="not-portrait" v-else>
        <!-- icon -->
        <div class="img-not-portrait">
            <img src="./components/pic/rotate_icon2.png" height="100vh" width="auto"/>
        </div>
        <!-- message -->
        <div class="p-not-portrait">
            <p>
              กรุณาใช้โทรศัพท์แนวตั้งเพื่อใช้งาน
            </p>
        </div>
    </div>
</template>

<style scoped>
    .no-select {
        /* Disable text selection */
        -webkit-touch-callout: none; /* iOS Safari */
        -webkit-user-select: none; /* Safari */
        -khtml-user-select: none; /* Konqueror HTML */
        -moz-user-select: none; /* Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
        user-select: none; /* Non-prefixed version, supported by most modern browsers */
    }

    header {
        line-height: 1.5;
        max-height: 100vh;
    }

    .logo {
        display: block;
        margin: 0 auto 2rem;
    }

    nav {
        width: 100%;
        font-size: 12px;
        text-align: center;
        margin-top: 2rem;
    }

    nav a.router-link-exact-active {
        color: var(--color-text);
    }


    nav a.router-link-exact-active:hover {
        background-color: transparent;
    }

    nav a {
        display: inline-block;
        padding: 0 1rem;
        border-left: 1px solid var(--color-border);
    }

    nav a:first-of-type {
        border: 0;
    }
    .not-portrait{
        display: grid;
        grid-gap: 20px;
        grid-template-columns: 1fr;
        grid-template-rows: 1.5fr 1fr;
        height: 90vh;
        width: 100%;
        font-size: 120%;
    }

    .not-portrait>div{
        display: flex;
        justify-content: center;
    }

    .img-not-portrait{
        display: flex;
        align-self: flex-end;
    }
    .p-not-portrait{
        display: flex;
        align-items: start;
    }

    @media (min-width: 1024px) {
        header {
            display: flex;
            place-items: center;
            padding-right: calc(var(--section-gap) / 2);
        }

        .logo {
            margin: 0 2rem 0 0;
        }

        header .wrapper {
            display: flex;
            place-items: flex-start;
            flex-wrap: wrap;
        }

        nav {
            text-align: left;
            margin-left: -1rem;
            font-size: 1rem;

            padding: 1rem 0;
            margin-top: 1rem;
        }
    }
</style>

<script lang="ts"> 
    export default {
        // default value
        data() {
            return {
                isPortrait: true
            };
        },
        // when the page is mounted
        mounted() {
            // check for resizing
            window.addEventListener('resize', this.handleOrientationChange);
            this.checkInitialOrientation();
        },
        // befor the page is destroy
        beforeDestroy() {
            // check for resizing
            window.removeEventListener('resize', this.handleOrientationChange);
        },
        methods: {
            // if resizing screen
            handleOrientationChange() {
                if (window.innerHeight > window.innerWidth) {
                    this.isPortrait = true;
                } else {
                    this.isPortrait = false;
                }
            },
            // if resizing screen
            checkInitialOrientation() {
                if (window.innerHeight > window.innerWidth) {
                    this.isPortrait = true;
                } else {
                    this.isPortrait = false;
                }
            }
        }
    };
</script>