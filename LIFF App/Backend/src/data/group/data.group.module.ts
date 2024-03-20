import { Module } from "@nestjs/common";
import { DatabaseModule } from "../database.module";
import { HttpModule } from "@nestjs/axios";
import { DataGroupService } from "./data.group.service";
import { ConfigModule } from "@nestjs/config";

@Module({
    imports: [DatabaseModule, HttpModule, ConfigModule],
    providers: [DataGroupService],
    exports: [DataGroupService],
})
export class DataGroupModule {}