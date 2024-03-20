import { Module } from "@nestjs/common";
import { DatabaseModule } from "../database.module";
import { HttpModule } from "@nestjs/axios";
import { DataFaceService } from "./data.face.service";

@Module({
    imports: [DatabaseModule, HttpModule],
    providers: [DataFaceService],
    exports: [DataFaceService],
})
export class DataFaceModule {}