import { HttpService } from "@nestjs/axios";
import { Injectable } from "@nestjs/common";
import { CreateGraphDto } from "./dto/create-graph.dto";
import { catchError, firstValueFrom } from "rxjs";
import { AxiosError } from "axios";
import { ConfigService } from "@nestjs/config";

@Injectable({})
export class GraphService {
    constructor(
        private readonly httpService: HttpService,
        private configService: ConfigService
    ) {}

    // get variable string from config variable (from docker environment variables)
    private CMS_BACKEND_CREATE_GRAPH = this.configService.get<string>("cmsbackend.api.create_graph");

    // function for send request to flask backend to create graph
    async postCreate(userId: string, clusterId: string): Promise<boolean> {
        // create data to send
        const requestGraph: CreateGraphDto = {
            userId: userId,
            clusterId: clusterId
        };

        // send request and get response
        const { data } = await firstValueFrom(
            this.httpService.post(this.CMS_BACKEND_CREATE_GRAPH, requestGraph).pipe(
                catchError((error: AxiosError) => {
                    throw new Error(`There is an error when posting to flask backend. ${error.response.status}, ${error.response.data}`);
                }),
            ),
        );
        
        const responseData: boolean = data["isPostComplete"];
        return responseData;
    }
}