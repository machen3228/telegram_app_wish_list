-- Create "gift_reservations" table
CREATE TABLE "gift_reservations" (
  "gift_id" bigint NOT NULL,
  "reserved_by_tg_id" bigint NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY ("gift_id"),
  CONSTRAINT "fk_gift_reservations_gift" FOREIGN KEY ("gift_id") REFERENCES "gifts" ("id") ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT "fk_gift_reservations_reserved_by" FOREIGN KEY ("reserved_by_tg_id") REFERENCES "users" ("tg_id") ON UPDATE NO ACTION ON DELETE CASCADE
);
