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
  url = "postgres://${local.envfile["APP__DB__USER"]}:${local.envfile["APP__DB__PASSWORD"]}@${local.envfile["APP__DB__HOST"]}:${local.envfile["APP__DB__PORT"]}/${local.envfile["APP__DB__NAME"]}?sslmode=disable"
  dev = "docker://postgres/15/dev?search_path=public"
  src = "file://database_schema/"

  migration {
    dir = "file://migrations"
  }

  schemas = ["public"]
}

env "local_test" {
  url = "postgres://${local.envfile["APP__DB__USER"]}:${local.envfile["APP__DB__PASSWORD"]}@${local.envfile["APP__DB__HOST"]}:${local.envfile["APP__DB__PORT"]}/${local.envfile["APP__DB__NAME"]}_test?sslmode=disable"
  dev = "docker://postgres/15/dev?search_path=public"
  src = "file://database_schema/"

  migration {
    dir = "file://migrations"
  }

  schemas = ["public"]
}
