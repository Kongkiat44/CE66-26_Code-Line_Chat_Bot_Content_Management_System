import { Module } from "@nestjs/common";
import { GraphController } from "./graph.controller";
import { GraphService } from "./graph.service";
import { HttpModule } from "@nestjs/axios";
import { ConfigModule } from "@nestjs/config";

@Module({
    imports: [HttpModule, ConfigModule],
    controllers: [GraphController],
    providers: [GraphService],
})
export class GraphModule {}