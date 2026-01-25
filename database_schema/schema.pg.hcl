schema "public" {
  comment = "standard public schema"
}

table "users" {
  schema = schema.public
  column "tg_id" {
    null = false
    type = bigint
  }
  column "tg_username" {
    null = false
    type = varchar(30)
  }
  column "first_name" {
    null = false
    type = varchar(30)
  }
  column "last_name" {
    null = true
    type = varchar(30)
  }
  column "avatar_url" {
    null = true
    type = varchar(100)
  }
  column "created_at" {
    null = false
    type = timestamptz
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamptz
    default = sql("now()")
  }
  primary_key {
    columns = [column.tg_id]
  }
  index "idx_tg_username" {
    columns = [column.tg_username]
    unique = true
  }
}

table "gifts" {
  schema = schema.public
  column "id" {
    null = false
    type = bigserial
  }
  column "user_id" {
    null = false
    type = bigint
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "url" {
    null = true
    type = varchar(500)
  }
  column "wish_rate" {
    null = true
    type = smallint
  }
  column "price" {
    null = true
    type = numeric(10, 2)
  }
  column "note" {
    null = true
    type = text
  }
  column "created_at" {
    null = false
    type = timestamptz
    default = sql("now()")
  }
  column "updated_at" {
    null = false
    type = timestamptz
    default = sql("now()")
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "fk_gifts_user" {
    columns = [column.user_id]
    ref_columns = [table.users.column.tg_id]
    on_delete = CASCADE
    on_update = NO_ACTION
  }

  index "idx_gifts_user_id" {
    columns = [column.user_id]
  }
}

table "friends" {
  schema = schema.public
  column "user_tg_id" {
    null = false
    type = bigint
  }
  column "friend_tg_id" {
    null = false
    type = bigint
  }
  column "created_at" {
    null = false
    type = timestamptz
    default = sql("now()")
  }
  primary_key {
    columns = [column.user_tg_id, column.friend_tg_id]
  }
  foreign_key "fk_friends_user" {
    columns = [column.user_tg_id]
    ref_columns = [table.users.column.tg_id]
    on_delete = CASCADE
    on_update = NO_ACTION
  }
  foreign_key "fk_friends_friend" {
    columns = [column.friend_tg_id]
    ref_columns = [table.users.column.tg_id]
    on_delete = CASCADE
    on_update = NO_ACTION
  }
  index "idx_friends_friend_id" {
    columns = [column.friend_tg_id]
  }
  check "chk_no_self_friendship" {
    expr = "user_tg_id != friend_tg_id"
  }
}
