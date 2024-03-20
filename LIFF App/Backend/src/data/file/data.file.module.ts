import { Module } from "@nestjs/common";
import { DatabaseModule } from "../database.module";
import { HttpModule } from "@nestjs/axios";
import { DataFileService } from "./data.file.service";
import { ConfigModule } from "@nestjs/config";

@Module({
    imports: [DatabaseModule, HttpModule, ConfigModule],
    providers: [DataFileService],
    exports: [DataFileService],
})
export class DataFileModule {}