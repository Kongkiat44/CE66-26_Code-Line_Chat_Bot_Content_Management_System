import { BadRequestException, Controller, Post, Req } from "@nestjs/common";
import { GraphService } from "./graph.service";
import { ResponseCreateGraph } from "./interface/graph.interface";

@Controller("graph")
export class GraphController {
    constructor(
        private graphService: GraphService
    ) {}

    // api function for return result of request create graph to flask backend
    @Post("create_graph")
    async requestGraph(@Req() request: Request): Promise<ResponseCreateGraph> {
        // check type of data property
        if (typeof(request.body["userId"])!=="string") {
            throw new BadRequestException(`Request body 'userId' is missing or not data type 'string'`);
        }
        if (typeof(request.body["clusterId"])!=="string") {
            throw new BadRequestException(`Request body 'clusterId' is missing or not data type 'string'`);
        }
        
        const userid = request.body["userId"];
        const clusterid = request.body["clusterId"];
        const postResult = await this.graphService.postCreate(userid,clusterid);
        const returnData: ResponseCreateGraph = {
            requestSuccess: postResult
        };
        return returnData;
    }
}