# telegram_app_wish_list
This is a Telegram-embedded app that lets users share their preferred gifts with friends. It helps people choose suitable presents, for example for birthdays, and removes the hassle of guessing what to buy

# VENV
We use uv as a package manager, so, to install this tool run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
To create venv run:
```bash
uv venv
```
Activate is
```bash
source .venv/bin/activate
```
To install dependencies run:
```bash
uv sync
```

# Start project
To launch database, run:
```bash
docker compose up --build -d
```

# Work with migrations
We work with **Atlas** to implement migrations.
So, to work with in you need Atlas to be installed on your
local machine. For instance, you can run:
```bash
curl -sSf https://atlasgo.sh | sh
```
You can implement changes in database. First, you need to
change database schema in `/database_schema/schema.pg.hcl`
Advise you to install `Atlas` plugin in Pycharm to see
syntaxis hints. Schema has extension `.pg.hcl`, so it will
help you to minimize errors while working with postgres schema.

To create migration file, fun:
```bash
atlas migrate diff {migration_name} --env local
```
To apply migration run:
```bash
atlas migrate apply --env local
```
To check migrations status, run:
```bash
atlas migrate status --env local
```
If you want to downgrade, run:
```bash
atlas migrate down --env local
```

# Run application
To set `PYTHONPATH` run:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/app
```
To run application, run:
```bash
python -m app.main
```
To get Swagger, open in browser http://localhost/schema/swagger
