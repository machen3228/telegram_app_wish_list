-- Modify "friends" table
ALTER TABLE "friends" ALTER COLUMN "created_at" TYPE timestamptz;
-- Modify "gifts" table
ALTER TABLE "gifts" ALTER COLUMN "created_at" TYPE timestamptz, ALTER COLUMN "updated_at" TYPE timestamptz;
-- Modify "users" table
ALTER TABLE "users" ALTER COLUMN "created_at" TYPE timestamptz, ALTER COLUMN "updated_at" TYPE timestamptz;
