import { Module } from "@nestjs/common";
import { DataImageModule } from "./image/data.image.module";
import { DataMainController } from "./data.controller";
import { DataGroupModule } from "./group/data.group.module";
import { DataFileModule } from "./file/data.file.module";
import { DataFaceModule } from "./face/data.face.module";
import { ConfigModule } from "@nestjs/config";

@Module({
    imports: [DataImageModule, DataGroupModule, DataFileModule, DataFaceModule, ConfigModule],
    controllers: [DataMainController],
})
export class DataMainModule {}