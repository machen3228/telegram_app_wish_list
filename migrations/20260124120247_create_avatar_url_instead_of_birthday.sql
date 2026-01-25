-- Modify "users" table
ALTER TABLE "users" DROP COLUMN "birthday", ADD COLUMN "avatar_url" character varying(100) NULL;
