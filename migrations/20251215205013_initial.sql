-- Create "users" table
CREATE TABLE "users" (
  "tg_id" bigint NOT NULL,
  "tg_username" character varying(30) NOT NULL,
  "first_name" character varying(30) NOT NULL,
  "last_name" character varying(30) NULL,
  "birthday" date NULL,
  "created_at" timestamp NOT NULL DEFAULT now(),
  "updated_at" timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY ("tg_id")
);
-- Create index "idx_tg_username" to table: "users"
CREATE UNIQUE INDEX "idx_tg_username" ON "users" ("tg_username");
-- Create "friends" table
CREATE TABLE "friends" (
  "user_tg_id" bigint NOT NULL,
  "friend_tg_id" bigint NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY ("user_tg_id", "friend_tg_id"),
  CONSTRAINT "fk_friends_friend" FOREIGN KEY ("friend_tg_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT "fk_friends_user" FOREIGN KEY ("user_tg_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT "chk_no_self_friendship" CHECK (user_tg_id <> friend_tg_id)
);
-- Create index "idx_friends_friend_id" to table: "friends"
CREATE INDEX "idx_friends_friend_id" ON "friends" ("friend_tg_id");
-- Create "gifts" table
CREATE TABLE "gifts" (
  "id" bigserial NOT NULL,
  "user_id" bigint NOT NULL,
  "name" character varying(100) NOT NULL,
  "url" character varying(500) NULL,
  "wish_rate" smallint NULL,
  "created_at" timestamp NOT NULL DEFAULT now(),
  "updated_at" timestamp NOT NULL DEFAULT now(),
  PRIMARY KEY ("id"),
  CONSTRAINT "fk_gifts_user" FOREIGN KEY ("user_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE
);
-- Create index "idx_gifts_user_id" to table: "gifts"
CREATE INDEX "idx_gifts_user_id" ON "gifts" ("user_id");
