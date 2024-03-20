// interfaces for receiving api response data 
export interface InnerGroupSearchAll {
    groupId: string;
    groupName: string;
    groupProfileLink: string;
    lastUsedTime: Date;
}

export interface InnerGroupMemberInfo {
    userId: string;
    userName: string;
    userProfileLink: string;
    imageCount: number;
    fileCount: number;
}

export interface ResponseGroupSearchAll {
    responseData: InnerGroupSearchAll[];
}

export interface ResponseGroupMemberInfo {
    memberList: InnerGroupMemberInfo[];
}

export interface ResponseGroupUserInfo {
    userName: string;
    userProfileLink: string;
    imageCount: number;
    fileCount: number;
}

export interface ResponseGroupFileInfo {
    imageTotalCount: number;
    imageTotalSizeByte: number;
    fileTotalCount: number;
    fileTotalSizeByte: number;
}