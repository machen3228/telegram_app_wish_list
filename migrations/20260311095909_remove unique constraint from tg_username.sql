-- Drop index "idx_tg_username" from table: "users"
DROP INDEX "idx_tg_username";
-- Create index "idx_tg_username" to table: "users"
CREATE INDEX "idx_tg_username" ON "users" ("tg_username");
