// data transfer object for send data to flask backend
export class DeleteFileDto {
    fileType: string;
    fileId: string;
    reqUserId: string;
}