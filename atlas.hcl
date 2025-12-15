variable "envfile" {
    type    = string
    default = ".env"
}

locals {
    envfile = {
        for line in split("\n", file(var.envfile)): split("=", line)[0] => regex("=(.*)", line)[0]
        if !startswith(line, "#") && length(split("=", line)) > 1
    }
}

env "local" {
  url = "postgres://${local.envfile["DB_USER"]}:${local.envfile["DB_PASSWORD"]}@${local.envfile["DB_HOST"]}:${local.envfile["DB_PORT"]}/${local.envfile["DB_NAME"]}?sslmode=disable"
  dev = "docker://postgres/15/dev?search_path=public"
  src = "file://app/database_schema/"

  migration {
    dir = "file://app/migrations"
  }

  schemas = ["public"]
}
