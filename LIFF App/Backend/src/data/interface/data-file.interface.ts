// interfaces for receiving api response data 
export interface InnerFileDataLong {
    fileId: string;
    fileLink: string;
    senderId: string;
    savedTime: Date;
    savedFileName: string;
    senderUserName: string;
}

export interface InnerFileSearchByGroupAndUser {
    fileId: string;
    fileLink: string;
    savedTime: Date;
    savedFileName: string;
}

// note: also used in image delete one
export interface ResponseFileDeleteOne {
    deleteSuccess: boolean;
}

export interface ResponseFileSearchByGroupAndUser {
    userFileList: InnerFileSearchByGroupAndUser[];
}

export interface ResponseFileSortLatest {
    sortLatest: InnerFileDataLong[];
}

export interface ResponseFileFetch {
    fetchSuccess: boolean;
}