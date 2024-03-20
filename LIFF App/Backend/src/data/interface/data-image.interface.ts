// interfaces for receiving api response data 
export interface InnerImageDataLong {
    imageId: string;
    imageLink: string;
    senderId: string;
    savedTime: Date;
    senderUserName: string;
}

export interface InnerImageSearchByGroupAndUser {
    imageId: string;
    imageLink: string;
    savedTime: Date;
}

export interface ResponseImageSearchByFace {
    imageLinkList: string[];
}

export interface ResponseImageSearchByGroupAndUser {
    userImageList: InnerImageSearchByGroupAndUser[];
}

export interface ResponseImageSortLatest {
    sortLatest: InnerImageDataLong[];
}
