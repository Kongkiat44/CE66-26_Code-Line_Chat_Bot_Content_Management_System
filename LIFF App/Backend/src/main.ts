import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from 'node:fs';

async function bootstrap() {
  // run service in http and enable CORS
  const app = await NestFactory.create(AppModule);
  app.enableCors();
  await app.listen(3333);
}
bootstrap();
