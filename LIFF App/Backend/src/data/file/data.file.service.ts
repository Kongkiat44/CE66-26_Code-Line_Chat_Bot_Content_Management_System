import { HttpService } from "@nestjs/axios";
import { Inject, Injectable } from "@nestjs/common";
import { Db, Document, WithId } from "mongodb";
import { DeleteFileDto } from "../dto/delete-file.dto";
import { catchError, firstValueFrom } from "rxjs";
import { AxiosError } from "axios";
import { GetFileSizeByteDto } from "../dto/get-fileSizeByte.dto";
import { ConfigService } from "@nestjs/config";

@Injectable({})
export class DataFileService {
    constructor(
        @Inject("DATABASE_CONNECTION") private database: Db,
        private readonly httpService: HttpService,
        private configService: ConfigService
    ) {}

    // get variable string from config variable (from docker environment variables)
    private CMS_BACKEND_DELETE_FILE = this.configService.get<string>("cmsbackend.api.delete_file");
    private CMS_BACKEND_TOTAL_FILE_SIZE = this.configService.get<string>("cmsbackend.api.total_file_size");
    private CMS_BACKEND_FETCH_FILE = this.configService.get<string>("cmsbackend.api.fetch_file");

    // function for query all file documents in database
    async findAll(): Promise<WithId<Document>[]> {
        return await this.database.collection("Files").find().toArray();
    }

    // function for query file documents with group id in database
    async findByGroupId(groupId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Files").find({"group_id":groupId}).toArray();
    }

    // function for query file documents with group id and user id in database
    async findByGroupAndUser(groupId: string, userId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Files").find({"group_id":groupId, "sender_id":userId}).toArray();
    }

    // function for request to flask backend for delete a file in server
    async deleteOne(docFileId: string, userId: string): Promise<boolean> {
        // send POST request
        const deleteFile: DeleteFileDto = {
            fileType: "doc",
            fileId: docFileId,
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
            console.log("There is error with post delete file: "+data["errorMessage"]);
        }
        return responseData;
    }

    // function for request to flask backend for total file size of the group
    async getTotalSizeByte(groupId: string): Promise<number> {
        // create data to send
        const getImageSize: GetFileSizeByteDto = {
            fileType: "doc",
            groupId: groupId
        };

        // send POST request and get response
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_TOTAL_FILE_SIZE,getImageSize).pipe(
                catchError((error: AxiosError) => {
                    throw new Error("There is an error when posting to flask backend\n"+error.response.status+"\n"+error.response.data);
                }),
            ),
        );
        
        const responseData: number = data["fileTotalSize"];
        return responseData;
    }

    // function for request to flask backend for send a file to user when user tap 'send to chat' button
    async fetchOneFile(docFileId: string, userId: string): Promise<boolean> {
        // note: use same DTO with delete file function
        const fetchFile: DeleteFileDto = {
            fileType: "doc",
            fileId: docFileId,
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