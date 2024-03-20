import { Inject, Injectable } from "@nestjs/common";
import { Db, Document, WithId } from "mongodb";

@Injectable({})
export class DataFaceService {
    // Note: use collection 'Clusters' in database
    constructor(
        @Inject("DATABASE_CONNECTION") private database: Db,
    ) {}

    // function for query all cluster documents in database
    async findAllCluster(): Promise<WithId<Document>[]> {
        return await this.database.collection("Clusters").find().toArray();
    }

    // function for query cluster documents with group id in database
    async findByGroupId(groupId: string): Promise<WithId<Document>[]> {
        return await this.database.collection("Clusters").find({"group_id":groupId}).toArray();
    }
}