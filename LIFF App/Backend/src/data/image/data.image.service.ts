import { HttpService } from "@nestjs/axios";
import { BadRequestException, Inject, Injectable } from "@nestjs/common";
import { Db, Document, ObjectId, WithId } from "mongodb";
import { catchError, firstValueFrom } from "rxjs";
import { AxiosError } from "axios";
import { GetFileSizeByteDto } from "../dto/get-fileSizeByte.dto";
import { DeleteFileDto } from "../dto/delete-file.dto";
import { ConfigService } from "@nestjs/config";

@Injectable({})
export class DataImageService {
    constructor(
        @Inject("DATABASE_CONNECTION") private database: Db,
        private readonly httpService: HttpService,
        private configService: ConfigService
    ) {}

    // get variable string from config variable (from docker environment variables)
    private CMS_BACKEND_DELETE_FILE = this.configService.get<string>("cmsbackend.api.delete_file");
    private CMS_BACKEND_TOTAL_FILE_SIZE = this.configService.get<string>("cmsbackend.api.total_file_size");
    private CMS_BACKEND_FETCH_FILE = this.configService.get<string>("cmsbackend.api.fetch_file");

    // function for query all image documents in database
    async findAll(): Promise<WithId<Document>[]> {
        return await this.database.collection("Images").find().toArray();
    }

    // function for query image documents with group id in database
    async findByGroupId(groupId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Images").find({"group_id":groupId}).toArray();
    }

    // function for query image documents and select only image that are saved after given time
    async findByTimeFrom(groupId: string, startDay: number, startMonth: number, startYear: number): Promise<WithId<Document>[]> {
        const currentTime = new Date();

        // check number of given parameters
        if ((startDay < 1) || (startDay > 31)) {
            throw new Error("The day must be between 1 to 31");
        }
        if ((startMonth < 1) || (startMonth > 12)) {
            throw new Error("The month must be between 1 to 12");
        }
        if ((startYear < 2000) || (startYear > currentTime.getFullYear())) {
            throw new Error(`The year must not be lower than 2000 or greater than ${currentTime.getFullYear()}`);
        }

        const timeStr = `${startYear}-${startMonth}-${startDay}`;
        const startTime = new Date(timeStr);

        let selImageDocs: Array<WithId<Document>> = [];

        // query images with group id
        const imageDocs = await this.findByGroupId(groupId);

        // loop through each image documents and filter only that are in between selected time and current time
        for (let image in imageDocs) {
            let saveTime = new Date(imageDocs[image]["saved_time"]);
            if (saveTime.getTime() >= startTime.getTime()) {
                selImageDocs.push(imageDocs[image]);
            }
        }

        return selImageDocs;
    }

    // function for request to flask backend for delete an image in server
    async deleteOne(imageId: string, userId: string): Promise<boolean> {
        // send POST request
        const deleteFile: DeleteFileDto = {
            fileType: "image",
            fileId: imageId,
            reqUserId: userId
        };
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_DELETE_FILE, deleteFile).pipe(
                catchError((error: AxiosError) => {
                    throw new Error(`There is an error when posting to flask backend. ${error.response.status}, ${error.response.data}`);
                }),
            ),
        );
        
        // get data from response
        const responseData: boolean = data["isDeleteComplete"];
        if (!responseData) {
            console.log("There is error with post delete image: "+data["errorMessage"]);
        }
        return responseData;
    }

    // function for query image documents with group id and cluster id in database
    async findByGroupAndCluster(groupId: string, clusterId: string): Promise<WithId<Document>[]> {
        if (!ObjectId.isValid(clusterId)) {
            throw new BadRequestException(`Cluster id from the request is not valid; id=${clusterId}`);
        }
        return await this.database.collection("Images").find({"group_id":groupId, "cluster_ids": {$all: [new ObjectId(clusterId)]}}).toArray();
    }

    // function for query image documents with group id and user id in database
    async findByGroupAndUser(groupId: string, userId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Images").find({"group_id":groupId, "sender_id":userId}).toArray();
    }

    // function for request to flask backend for total image file size of the group
    async getTotalSizeByte(groupId: string): Promise<number> {
        // create data to send
        const getImageSize: GetFileSizeByteDto = {
            fileType: "image",
            groupId: groupId
        };

        // send POST request and get response
        const { data } = await firstValueFrom( // Note: get URL from docker container env var instead
            this.httpService.post(this.CMS_BACKEND_TOTAL_FILE_SIZE,getImageSize).pipe(
                catchError((error: AxiosError) => {
                    throw new Error("There is an error when posting to flask backend\n"+error.response.status+"\n"+error.response.data);
                }),
            ),
        );
        
        const responseData: number = data["fileTotalSize"]; // need to check, may gives error
        return responseData;
    }

    // function for request to flask backend for send an image to user when user tap 'send to chat' button
    async fetchOneImage(imageId: string, userId: string): Promise<boolean> {
        // note: use same DTO with delete file function
        const fetchFile: DeleteFileDto = {
            fileType: "image",
            fileId: imageId,
            reqUserId: userId
        };

        // send POST request and get response
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_FETCH_FILE, fetchFile).pipe(
                catchError((error: AxiosError) => {
                    throw new Error(`There is an error when posting to flask backend. ${error.response.status}, ${error.response.data}`);
                }),
            ),
        );
        
        const responseData: boolean = data["sendSuccess"];
        if (!responseData) {
            console.log("There is error with post delete image: "+data["errorMessage"]);
        }
        return responseData;
    }
}