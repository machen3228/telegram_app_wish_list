-- Modify "gift_reservations" table
ALTER TABLE "gift_reservations" ADD CONSTRAINT "uk_gift_reservations_gift_id" UNIQUE ("gift_id");
