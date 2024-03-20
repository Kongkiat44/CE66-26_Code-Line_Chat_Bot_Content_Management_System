// data transfer object for send data to flask backend
export class SingleUserInfoDto {
    userId: string;
    userName: string;
    userProfileLink: string;
    imageCount: number;
    fileCount: number;
}