import { Module } from "@nestjs/common";
import { Db, MongoClient } from "mongodb";

// get string variable from environment variables (from docker environment section)
const MONGOSTR = process.env.MONGOSTR || "mongodb://mongoservice:27017/LineCMS";
const DBNAME = process.env.DBNAME || "LineCMS";

// create connection to MongoDB database and export as provider to be able to access by other module
@Module({
    providers: [
        {
            provide: "DATABASE_CONNECTION",
            useFactory: async (): Promise<Db> => {
                try {
                    const client = await MongoClient.connect(MONGOSTR, {appName: "LIFF Backend"});
                    return client.db(DBNAME);
                } catch (e) {
                    throw e;
                }
            }
        },
    ],
    exports: ["DATABASE_CONNECTION"],
})
export class DatabaseModule {}