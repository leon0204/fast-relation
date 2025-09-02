from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "entity" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(20) NOT NULL UNIQUE /* 用户名称 */,
    "alias" VARCHAR(30)   /* 姓名 */,
    "email" VARCHAR(255) NOT NULL UNIQUE /* 邮箱 */,
    "phone" VARCHAR(20)   /* 电话 */
);
CREATE INDEX IF NOT EXISTS "idx_entity_created_7e8581" ON "entity" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_entity_updated_dbd1fd" ON "entity" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_entity_usernam_3e6f6f" ON "entity" ("username");
CREATE INDEX IF NOT EXISTS "idx_entity_alias_9c450a" ON "entity" ("alias");
CREATE INDEX IF NOT EXISTS "idx_entity_email_6f5b1b" ON "entity" ("email");
CREATE INDEX IF NOT EXISTS "idx_entity_phone_8eaf4f" ON "entity" ("phone");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "entity";"""
