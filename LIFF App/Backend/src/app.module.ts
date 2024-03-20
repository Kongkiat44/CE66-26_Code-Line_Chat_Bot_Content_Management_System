import { Module } from '@nestjs/common';
import { DataMainModule } from './data/data.module';
import { GraphModule } from './graph/graph.module';
import { ConfigModule } from '@nestjs/config';
import prodConfiguration from './config/prod-configuration';

@Module({
  imports: [DataMainModule,
    GraphModule,
    ConfigModule.forRoot({
      load: [prodConfiguration],
      isGlobal: true,
    }),
  ],
})
export class AppModule {}
