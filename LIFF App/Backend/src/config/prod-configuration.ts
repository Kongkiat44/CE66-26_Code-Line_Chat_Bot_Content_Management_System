// set configuration values with default values if cannot find value from docker environment variables (environment section)
export default () => ({
    database: {
        mongostr: process.env.MONGOSTR || "mongodb://mongoservice:27017/LineCMS",
        name: process.env.DBNAME || "LineCMS"
    },
    cmsbackend: {
        api: {
            delete_file: process.env.CMS_API_DELETE_FILE || "https://analytics02.kmitl.ac.th/cms/api/liff/delete_file",
            member_profile: process.env.CMS_API_MEMBER_PROFILE || "https://analytics02.kmitl.ac.th/cms/api/liff/member_profile",
            total_file_size: process.env.CMS_API_TOTAL_FILE_SIZE || "https://analytics02.kmitl.ac.th/cms/api/liff/total_file_size",
            create_graph: process.env.CMS_API_CREATE_GRAPH || "https://analytics02.kmitl.ac.th/cms/api/liff/create_graph",
            fetch_file: process.env.CMS_API_FETCH_FILE || "https://analytics02.kmitl.ac.th/cms/api/liff/fetch_file",
        }
    },
    fileserver: {
        link: {
            file: process.env.FILE_SERVER_LINK_FILE || "https://analytics02.kmitl.ac.th/linecms/file/",
            face: process.env.FILE_SERVER_LINK_FACE || "https://analytics02.kmitl.ac.th/linecms/face/",
            image: process.env.FILE_SERVER_LINK_IMAGE || "https://analytics02.kmitl.ac.th/linecms/image/",
        }
    },
    dummyvalue: process.env.DUMMYTEST || "ThisIsDefaultValue",
});