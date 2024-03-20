import { Module } from "@nestjs/common";
import { DataImageService } from "./data.image.service";
import { DatabaseModule } from "../database.module";
import { HttpModule } from "@nestjs/axios";
import { ConfigModule } from "@nestjs/config";

@Module({
    imports: [DatabaseModule, HttpModule, ConfigModule],
    providers: [DataImageService],
    exports: [DataImageService],
})
export class DataImageModule {}