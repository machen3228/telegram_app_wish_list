-- Create "friend_requests" table
CREATE TABLE "friend_requests" (
  "sender_tg_id" bigint NOT NULL,
  "receiver_tg_id" bigint NOT NULL,
  "status" character varying(20) NOT NULL DEFAULT 'pending',
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "updated_at" timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY ("sender_tg_id", "receiver_tg_id"),
  CONSTRAINT "fk_friend_requests_receiver" FOREIGN KEY ("receiver_tg_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT "fk_friend_requests_sender" FOREIGN KEY ("sender_tg_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT "chk_no_self_request" CHECK (sender_tg_id <> receiver_tg_id)
);
-- Create index "idx_friend_requests_receiver" to table: "friend_requests"
CREATE INDEX "idx_friend_requests_receiver" ON "friend_requests" ("receiver_tg_id");
-- Create index "idx_friend_requests_status" to table: "friend_requests"
CREATE INDEX "idx_friend_requests_status" ON "friend_requests" ("status");
