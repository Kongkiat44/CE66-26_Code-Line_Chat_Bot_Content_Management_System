// interfaces for receiving api response data 
export interface InnerFaceSearchAll {
    clusterId: string;
    faceLink: string;
}

export interface ResponseFaceSearchAll {
    responseData: InnerFaceSearchAll[];
}