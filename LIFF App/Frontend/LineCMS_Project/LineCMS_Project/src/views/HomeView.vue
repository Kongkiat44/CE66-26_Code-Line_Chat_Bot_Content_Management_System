<template>
    <main>
        <GroupGrid/>
    </main>
</template>
<script lang="ts">
    import GroupGrid from '../components/grid/group_grid.vue'
    import { ref } from 'vue';

    export default {
        setup(){
            const cangetUserID = ref(false);
            return{
                cangetUserID,
            }
        },
        components: {
            GroupGrid,
        },
        methods: {
        }
    }
</script>

