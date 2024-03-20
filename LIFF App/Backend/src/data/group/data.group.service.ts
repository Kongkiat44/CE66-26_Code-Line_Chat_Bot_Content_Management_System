import { HttpService } from "@nestjs/axios";
import { Inject, Injectable } from "@nestjs/common";
import { AxiosError } from "axios";
import { Db, Document, WithId } from "mongodb";
import { catchError, firstValueFrom } from "rxjs";
import { RequestUserInfoDto } from "../dto/request-userInfo.dto";
import { InnerGroupMemberInfo } from "../interface/data-group.interface";
import { ConfigService } from "@nestjs/config";

@Injectable({})
export class DataGroupService {
    constructor(
        @Inject("DATABASE_CONNECTION") private database: Db,
        private readonly httpService: HttpService,
        private configService: ConfigService
    ) {}

    // get variable string from config variable (from docker environment variables)
    private CMS_BACKEND_MEMBER_PROFILE = this.configService.get<string>("cmsbackend.api.member_profile");

    // function for query all group documents in database
    async findAll(): Promise<WithId<Document>[]> {
        return await this.database.collection("Groups").find().toArray();
    }

    // function for query group documents with user id in database
    async findByUserId(userId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Groups").find({"member_ids": {$all: [userId]}, "status":"Active"}).toArray();
    }

    // function for request to flask backend to get selected group member data
    async getMemberInfo(groupId: string): Promise<InnerGroupMemberInfo[]> {
        const selGroup = await this.database.collection<{ _id: string }>("Groups").findOne({_id:groupId});
        
        // get member ids
        const memberIds: string[] = selGroup["member_ids"]; // expected to get array of userId

        // get each member username and profileLink from flask backend
        const reqUserInfo: RequestUserInfoDto = {
            groupId: groupId,
            userIdList: memberIds 
        };
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_MEMBER_PROFILE,reqUserInfo).pipe(
                catchError((error: AxiosError) => {
                    throw new Error("There is an error when posting to flask backend\n"+error.response.status+"\n"+error.response.data);
                }),
            ),
        );
        
        const responseData: object[] = data["responseData"]; // need to check, may gives error
        
        // get image count and file count of each member
        const groupImages = await this.database.collection("Images").find({"group_id":groupId}).toArray();
        const groupFiles = await this.database.collection("Files").find({"group_id":groupId}).toArray();
        let memberInfoList: InnerGroupMemberInfo[] = [];
        
        // put all data together (username, profile, file count)
        for (let iUser in memberIds) {
            let imgCount = 0;
            let docCount = 0;
            let thisUserName: string;
            let thisUserProfile: string;

            for (let iImg in groupImages) {
                let senderId:string = groupImages[iImg]["sender_id"];
                if (memberIds[iUser] === senderId) {
                    imgCount += 1;
                }
            }

            for (let iFile in groupFiles) {
                let senderId:string = groupFiles[iFile]["sender_id"];
                if (memberIds[iUser] === senderId) {
                    docCount += 1;
                }
            }

            for (let iData in responseData) {
                if (memberIds[iUser] === responseData[iData]["userId"]) {
                    thisUserName = responseData[iData]["userName"];
                    thisUserProfile = responseData[iData]["userProfileLink"];
                    break;
                }
            }

            // put data of one member together
            const userInfo: InnerGroupMemberInfo = {
                userId: memberIds[iUser],
                userName: thisUserName,
                userProfileLink: thisUserProfile,
                imageCount: imgCount,
                fileCount: docCount
            }
            memberInfoList.push(userInfo);
        }
        const allMemberInfo = memberInfoList;
        return allMemberInfo;
            
    }

    // function for request to flask backend to get single member data of selected group
    async getSingleMemberInfo(groupId: string, userId: string): Promise<InnerGroupMemberInfo> {
        const memberIds = [userId];

        // get member username and profileLink from flask backend
        const reqUserInfo: RequestUserInfoDto = {
            groupId: groupId,
            userIdList: memberIds
        };
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_MEMBER_PROFILE,reqUserInfo).pipe(
                catchError((error: AxiosError) => {
                    throw new Error("There is an error when posting to flask backend\n"+error.response.status+"\n"+error.response.data);
                }),
            ),
        );
        const responseData: object[] = data["responseData"];

        // get image and file count of that user id
        const userImages = await this.database.collection("Images").find({"group_id":groupId, "sender_id":userId}).toArray();
        const userFiles = await this.database.collection("Files").find({"group_id":groupId, "sender_id":userId}).toArray();
        
        const userInfo: InnerGroupMemberInfo = {
            userId: userId,
            userName: responseData[0]["userName"], // need to check if it's right format to do so
            userProfileLink: responseData[0]["userProfileLink"],
            imageCount: userImages.length,
            fileCount: userFiles.length
        };
        return userInfo;
    }

}