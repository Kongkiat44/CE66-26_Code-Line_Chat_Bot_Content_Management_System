import { createStore, Store } from 'vuex';

// centralize data can be use in every page. but can be lose if refresh the page
interface State{
    user_ID: string;
    group_ID: string;
    group_name: string;
    group_profile_image: string;
    cluster_ID: string;
    cluster_sample_image: string;
    view_user_ID: string;
    view_user_name: string;
}

export default createStore<State>({
    state: {
      user_ID: "",
      group_ID: "",
      group_name: "",
      group_profile_image: "",
      cluster_ID: "",
      cluster_sample_image: "",
      view_user_ID: "",
      view_user_name: "",
      browser_type: "",
    },
    // save to store
    mutations: {
        updateUserID(state, user_ID: string){
            state.user_ID = user_ID;
        },
        updateGroupID(state, group_ID: string){
            state.group_ID = group_ID;
        },
        updateGroupName(state, group_name: string){
            state.group_name = group_name;
        },
        updateProfileImage(state, URL: string){
            state.group_profile_image = URL;
        },
        updateClusterID(state, cluster_ID: string){
            state.cluster_ID = cluster_ID;
        },
        updateClusterImage(state, URL: string){
            state.cluster_sample_image = URL;
        },
        updateViewUserID(state, user_ID: string){
            state.view_user_ID = user_ID;
        },
        updateViewUserName(state, user_name: string){
            state.view_user_name = user_name;
        },
        updateBrowserType(state, type: string){
            state.browser_type = type;
        },
    },
    // tell to store to save
    actions: {
        setUserID(context, payload:string){
            context.commit('updateUserID', payload)
        },
        setGroupID(context, payload:string){
            context.commit('updateGroupID', payload)
        },
        setGroupName(context, payload:string){
            context.commit('updateGroupName', payload)
        },
        setGroupProfileImage(context, payload:string){
            context.commit('updateProfileImage', payload)
        },
        setClusterID(context, payload:string){
            context.commit('updateClusterID', payload)
        },
        setClusterImage(context, payload:string){
            context.commit('updateClusterImage', payload)
        },
        setViewUserID(context, payload:string){
            context.commit('updateViewUserID', payload)
        },
        setViewUserName(context, payload:string){
            context.commit('updateViewUserName', payload)
        },
        setBrowserType(context, payload:string){
            context.commit('updateBrowserType', payload)
        },
    },
});