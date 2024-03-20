import { BadRequestException, Controller, Get, Post, Req } from "@nestjs/common";
import { DataImageService } from "./image/data.image.service";
import { Request } from "express";
import { Document, WithId } from "mongodb";
import { DataGroupService } from "./group/data.group.service";
import { InnerImageDataLong, InnerImageSearchByGroupAndUser, ResponseImageSearchByFace, ResponseImageSearchByGroupAndUser, ResponseImageSortLatest } from "./interface/data-image.interface";
import { InnerFileDataLong, InnerFileSearchByGroupAndUser, ResponseFileDeleteOne, ResponseFileFetch, ResponseFileSearchByGroupAndUser, ResponseFileSortLatest } from "./interface/data-file.interface";
import { InnerGroupSearchAll, ResponseGroupFileInfo, ResponseGroupMemberInfo, ResponseGroupSearchAll, ResponseGroupUserInfo } from "./interface/data-group.interface";
import { DataFileService } from "./file/data.file.service";
import { DataFaceService } from "./face/data.face.service";
import { InnerFaceSearchAll, ResponseFaceSearchAll } from "./interface/data-face.interface";
import { ConfigService } from "@nestjs/config";

@Controller("data")
export class DataMainController {
    constructor(
        private imageService: DataImageService,
        private groupService: DataGroupService,
        private fileService: DataFileService,
        private faceService: DataFaceService,
        private configService: ConfigService
    ) {}

    // get variable string from config variable (from docker environment variables)
    private LINK_TO_IMAGE = this.configService.get<string>("fileserver.link.image");
    private LINK_TO_FACE = this.configService.get<string>("fileserver.link.face");
    private LINK_TO_FILE = this.configService.get<string>("fileserver.link.file");
    private TEST_ENV_DUMMY = this.configService.get<string>("dummyvalue");

    // api function for testing nestjs when run the app
    @Get("testenv")
    async testDummyEnvVar(): Promise<string> {
        return `Result: ${this.TEST_ENV_DUMMY}`;
    }

    // api function for return image documents filter be group id
    @Post("image/search_by_group_id")
    async searchImageByGroup(@Req() request: Request): Promise<WithId<Document>[]> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        const gid = request.body["groupId"];
        return this.imageService.findByGroupId(gid);
    }

    // api function for return all image documents in database
    @Get("image/find_all")
    async searchAllImage(): Promise<WithId<Document>[]> {
        return this.imageService.findAll();
    }


    // API calls for frontend
    // Image section

    // api function for return image links from select group id and cluster id
    @Post("image/search_by_face")
    async searchImageByFace(@Req() request: Request): Promise<ResponseImageSearchByFace> {
        // check data type of json body
        if (typeof(request.body["clusterId"])!=="string") {
            throw new BadRequestException(`Request body 'clusterId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }

        const clusterid = request.body["clusterId"];
        const gid = request.body["groupId"];
        const imageResult = await this.imageService.findByGroupAndCluster(gid,clusterid);
        let imagelinklist: string[] = [];
        for (let i in imageResult) {
            let imageFileName = imageResult[i]["_id"];
            imagelinklist.push(this.LINK_TO_IMAGE+imageFileName.toString());
        }
        const returnData: ResponseImageSearchByFace = {
            imageLinkList: imagelinklist
        };
        return returnData;
    }

    // api function for return image links from select group id and time
    @Post("image/search_by_groupAndTime")
    async searchImageByTime(@Req() request: Request): Promise<ResponseImageSearchByFace> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["startDay"])!=="number") {
            throw new BadRequestException(`Request body 'startDay' is missing or not data type 'number'`);
        }
        if (typeof(request.body["startMonth"])!=="number") {
            throw new BadRequestException(`Request body 'startMonth' is missing or not data type 'number'`);
        }
        if (typeof(request.body["startYear"])!=="number") {
            throw new BadRequestException(`Request body 'startYear' is missing or not data type 'number'`);
        }

        const gid = request.body["groupId"];
        const day = request.body["startDay"];
        const month = request.body["startMonth"];
        const year = request.body["startYear"];
        const imageResult = await this.imageService.findByTimeFrom(gid,day,month,year);
        
        let imagelinklist: string[] = [];
        for (let i in imageResult) {
            let imageFileName = imageResult[i]["_id"];
            imagelinklist.push(this.LINK_TO_IMAGE+imageFileName.toString());
        }
        const returnData: ResponseImageSearchByFace = {
            imageLinkList: imagelinklist
        };
        return returnData;
    }

    // api function for return result of delete an image in server and database
    @Post("image/delete_one")
    async deleteOneImage(@Req() request: Request): Promise<ResponseFileDeleteOne> {
        // check data type of json body
        if (typeof(request.body["imageId"])!=="string") {
            throw new BadRequestException(`Request body 'imageId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const imageid = request.body["imageId"];
        const userid = request.body["userId"];
        const delResult = await this.imageService.deleteOne(imageid,userid);
        const returnData: ResponseFileDeleteOne = {
            deleteSuccess: delResult
        };
        return returnData;
    }

    // api function for return image links from select group id and user id
    @Post("image/search_by_groupAndUser")
    async searchImageByUser(@Req() request: Request): Promise<ResponseImageSearchByGroupAndUser> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const userid = request.body["userId"];
        const gid = request.body["groupId"];
        const imageResult = await this.imageService.findByGroupAndUser(gid,userid);
        let imageDataList: InnerImageSearchByGroupAndUser[] = [];
        for (let i in imageResult) {
            let imgid = imageResult[i]["_id"].toString();
            const imgData: InnerImageSearchByGroupAndUser = {
                imageId: imgid, 
                imageLink: this.LINK_TO_IMAGE+imgid,
                savedTime: imageResult[i]["saved_time"]
            };
            imageDataList.push(imgData);
        }
        const returnData: ResponseImageSearchByGroupAndUser = {
            userImageList: imageDataList
        };
        return returnData;
    }

    // api function for return list of image data which sorted by saved time
    @Post("image/sort_latest")
    async sortImageLatest(@Req() request: Request): Promise<ResponseImageSortLatest> {
        let imageList: InnerImageDataLong[] = [];
        
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="undefined") {
            if (typeof(request.body["userId"])!=="string") {
                throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
            }
            // get image data from group id and user id (use in 'personal file management' page)
            const userid = request.body["userId"];
            const groupid = request.body["groupId"];
            const imageResult = await this.imageService.findByGroupAndUser(groupid,userid);

            // get username from user id
            const userInfo = await this.groupService.getSingleMemberInfo(groupid,userid);
            
            for (let i in imageResult) {
                let imgid = imageResult[i]["_id"].toString();
                const imgDataLong: InnerImageDataLong = {
                    imageId: imgid,
                    imageLink: this.LINK_TO_IMAGE+imgid,
                    senderId: imageResult[i]["sender_id"],
                    savedTime: new Date(imageResult[i]["saved_time"]),
                    senderUserName: userInfo.userName
                };
                imageList.push(imgDataLong);
            }
        } else {
            // get image data from group id (use in 'Gallery' page)
            const groupid = request.body["groupId"];
            const imageResult = await this.imageService.findByGroupId(groupid);

            // get all username of member from group id
            const allMemberInfo = await this.groupService.getMemberInfo(groupid);
            
            for (let i in imageResult) {
                let userName = "";
                for (let j in allMemberInfo) {
                    if (allMemberInfo[j]["userId"] == imageResult[i]["sender_id"]) {
                        userName = allMemberInfo[j]["userName"];
                        break;
                    }
                }
                let imgid = imageResult[i]["_id"].toString();
                const imgDataLong: InnerImageDataLong = {
                    imageId: imgid,
                    imageLink: this.LINK_TO_IMAGE+imgid,
                    senderId: imageResult[i]["sender_id"],
                    savedTime: new Date(imageResult[i]["saved_time"]),
                    senderUserName: userName
                };
                imageList.push(imgDataLong);
            }
        }

        // sort image from latest with saved time
        imageList.sort((a, b) => a.savedTime.getTime() - b.savedTime.getTime());
        imageList.reverse();

        // return final data
        const data: ResponseImageSortLatest = {
            sortLatest: imageList
        };
        return data;
    }

    // api function for return result of send image to user in LineCMS Official chat
    @Post("image/fetch_one")
    async fetchImagetoChat(@Req() request: Request): Promise<ResponseFileFetch> {
        // check data type of json body
        if (typeof(request.body["imageId"])!=="string") {
            throw new BadRequestException(`Request body 'imageId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const imageid = request.body["imageId"];
        const userid = request.body["userId"];
        const postSuccess = await this.imageService.fetchOneImage(imageid, userid);
        const data: ResponseFileFetch = {
            fetchSuccess: postSuccess
        };
        return data;
    }
    

    // Group section

    // api function for return list of group data which sorted by name
    @Post("group/search_all")
    async searchAllGroup(@Req() request: Request): Promise<ResponseGroupSearchAll> {
        // check data type of json body
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const userid = request.body["userId"];

        // get group data with user id
        const groupResult = await this.groupService.findByUserId(userid);

        let groupDataList: InnerGroupSearchAll[] = [];
        for (let i in groupResult) {
            const groupData: InnerGroupSearchAll = {
                groupId: groupResult[i]["_id"].toString(),
                groupName: groupResult[i]["group_name"],
                groupProfileLink: groupResult[i]["group_image_link"],
                lastUsedTime: new Date(groupResult[i]["last_used"])
            };
            groupDataList.push(groupData);
        }

        // sort data list by groupName (also Uppercase letter comes before Lowercase letter)
        groupDataList.sort((a, b) => {
            if (a.groupName < b.groupName) {
                return -1;
            }
            if (a.groupName > b.groupName) {
                return 1;
            }
            return 0;
        });
        
        const returnData: ResponseGroupSearchAll = {
            responseData: groupDataList
        };
        return returnData;
    }

    // api function for return list of member data which sorted by username
    @Post("group/member_info")
    async searchGroupMemberInfo(@Req() request: Request): Promise<ResponseGroupMemberInfo> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }

        const gid = request.body["groupId"]; 
        let memberResult = await this.groupService.getMemberInfo(gid);

        // sort data list by username (also Uppercase letter comes before Lowercase letter)
        memberResult.sort((a, b) => {
            if (a.userName < b.userName) {
                return -1;
            }
            if (a.userName > b.userName) {
                return 1;
            }
            return 0;
        });
        
        const returnData: ResponseGroupMemberInfo = {
            memberList: memberResult
        };
        return returnData;
    }

    // api function for return file and image data of select group
    @Post("group/file_info")
    async fetchGroupFileInfo(@Req() request: Request): Promise<ResponseGroupFileInfo> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }

        const gid = request.body["groupId"];
        const imageResult = await this.imageService.findByGroupId(gid);
        const totalImageSize = await this.imageService.getTotalSizeByte(gid);
        const totalImageCount = imageResult.length;
        const fileResult = await this.fileService.findByGroupId(gid);
        const totalFileSize = await this.fileService.getTotalSizeByte(gid);
        const totalFileCount = fileResult.length;
        
        const data: ResponseGroupFileInfo = {
            imageTotalCount: totalImageCount,
            imageTotalSizeByte: totalImageSize,
            fileTotalCount: totalFileCount,
            fileTotalSizeByte: totalFileSize
        };
        return data;
    }

    // api function for return user data in select group
    @Post("group/user_info")
    async searchGroupSingleUserInfo(@Req() request: Request): Promise<ResponseGroupUserInfo> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const userid = request.body["userId"];
        const gid = request.body["groupId"];
        const singleMemberResult = await this.groupService.getSingleMemberInfo(gid,userid);
        const returnData: ResponseGroupUserInfo = {
            userName: singleMemberResult.userName,
            userProfileLink: singleMemberResult.userProfileLink,
            imageCount: singleMemberResult.imageCount,
            fileCount: singleMemberResult.fileCount
        };
        return returnData;
    }

    
    // File section

    // api function for return result of delete a file in server and database
    @Post("file/delete_one")
    async deleteOneFile(@Req() request: Request): Promise<ResponseFileDeleteOne> {
        // check data type of json body
        if (typeof(request.body["fileId"])!=="string") {
            throw new BadRequestException(`Request body 'fileId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const fileid = request.body["fileId"];
        const userid = request.body["userId"];
        const delResult = await this.fileService.deleteOne(fileid, userid);
        const returnData: ResponseFileDeleteOne = {
            deleteSuccess: delResult
        };
        return returnData;
    }

    // api function for return list of file data from select user id and group id
    @Post("file/search_by_groupAndUser")
    async searchFileByUser(@Req() request: Request): Promise<ResponseFileSearchByGroupAndUser> {
        // check data type of json body
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }

        const userid = request.body["userId"];
        const gid = request.body["groupId"];
        const fileResult = await this.fileService.findByGroupAndUser(gid,userid);
        let fileDataList: InnerFileSearchByGroupAndUser[] = [];
        for (let i in fileResult) {
            let fid = fileResult[i]["_id"].toString();
            const fileData: InnerFileSearchByGroupAndUser = {
                fileId: fid,
                fileLink: this.LINK_TO_FILE+fid,
                savedTime: fileResult[i]["saved_time"],
                savedFileName: fileResult[i]["file_name"]
            };
            fileDataList.push(fileData);
        }
        const returnData: ResponseFileSearchByGroupAndUser = {
            userFileList: fileDataList
        };
        return returnData;
    }

    // api function for return list of file data which sorted by saved time
    @Post("file/sort_latest")
    async sortFileLatest(@Req() request: Request): Promise<ResponseFileSortLatest> {
        let fileList: InnerFileDataLong[] = [];

        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="undefined") {
            if (typeof(request.body["userId"])!=="string") {
                throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
            }

            // get file data from group id and user id (use in 'personal file management' page)
            const userid = request.body["userId"];
            const groupid = request.body["groupId"];
            const fileResult = await this.fileService.findByGroupAndUser(groupid,userid);

            // get username from user id
            const userInfo = await this.groupService.getSingleMemberInfo(groupid,userid);

            for (let i in fileResult) {
                let fileid = fileResult[i]["_id"].toString();
                const fileDataLong: InnerFileDataLong = {
                    fileId: fileid,
                    fileLink: this.LINK_TO_FILE+fileid,
                    senderId: fileResult[i]["sender_id"],
                    savedTime: new Date(fileResult[i]["saved_time"]),
                    savedFileName: fileResult[i]["file_name"],
                    senderUserName: userInfo.userName
                };
                fileList.push(fileDataLong);
            }
        } else {
            // get file data from groupId (use in 'Gallery' page)
            const groupid = request.body["groupId"];
            const fileResult = await this.fileService.findByGroupId(groupid);

            // get all username of member from group id
            const allMemberInfo = await this.groupService.getMemberInfo(groupid);

            for (let i in fileResult) {
                let userName = "";
                for (let j in allMemberInfo) {
                    if (allMemberInfo[j]["userId"] == fileResult[i]["sender_id"]) {
                        userName = allMemberInfo[j]["userName"];
                        break;
                    }
                }
                let fileid = fileResult[i]["_id"].toString();
                const fileDataLong: InnerFileDataLong = {
                    fileId: fileid,
                    fileLink: this.LINK_TO_FILE+fileid,
                    senderId: fileResult[i]["sender_id"],
                    savedTime: new Date(fileResult[i]["saved_time"]),
                    savedFileName: fileResult[i]["file_name"],
                    senderUserName: userName
                };
                fileList.push(fileDataLong);
            }
        }
        
        // sort file from latest with saved time
        fileList.sort((a, b) => a.savedTime.getTime() - b.savedTime.getTime());
        fileList.reverse();

        // return final data
        const data: ResponseFileSortLatest = {
            sortLatest: fileList
        };
        return data;
    }

    // api function for return result of send file to user in LineCMS Official chat
    @Post("file/fetch_one")
    async fetchFiletoChat(@Req() request: Request): Promise<ResponseFileFetch> {
        // check data type of json body
        if (typeof(request.body["fileId"])!=="string") {
            throw new BadRequestException(`Request body 'fileId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }

        const fileid = request.body["fileId"];
        const userid = request.body["userId"];
        const postSuccess = await this.fileService.fetchOneFile(fileid, userid);
        const data: ResponseFileFetch = {
            fetchSuccess: postSuccess
        };
        return data;
    }


    // Face section

    // api function for return list of face data from select group
    @Post("face/search_all")
    async searchAllFaceCluster(@Req() request: Request): Promise<ResponseFaceSearchAll> {
        // check data type of json body
        if (typeof(request.body["groupId"])!=="string") {
            throw new BadRequestException(`Request body 'groupId' is missing or not data type 'string'`);
        }

        const gid = request.body["groupId"];
        const clusterResult = await this.faceService.findByGroupId(gid);
        let clusterDataList: InnerFaceSearchAll[] = [];
        for (let i in clusterResult) {
            const clusterData: InnerFaceSearchAll = {
                clusterId: clusterResult[i]["_id"].toString(),
                faceLink: this.LINK_TO_FACE+clusterResult[i]["face_link"]
            };
            clusterDataList.push(clusterData);
        }
        const returnData: ResponseFaceSearchAll = {
            responseData: clusterDataList
        };
        return returnData;
    }

    // Note: Graph section is in another controller file
}