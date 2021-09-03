# Quart Postgres Boilerplate

![Code Check](https://github.com/esfoobar/quart-pg-boilerplate/workflows/Code%20Checks/badge.svg)

This is a boilerplate for a Quart app that can run as a Poetry, Heroku or Docker application. Requires `python 3.7` or higher.

## Local Development

### Install PostgreSQL on Mac

- Install using HomeBrew: `brew install postgresql`
  - If you want Postgres to launch automatically whenever you power on your Mac, you can do: `brew services start postgresql`. I really don’t recommend that. Instead you can start it manually when you need it by doing `pg_ctl -D /usr/local/var/postgres start` and stopping with `pg_ctl -D /usr/local/var/postgres stop`.
  - To login to Postgres using: `psql postgres`

### Install PostgreSQL on Windows

- Install using Chocolatey: `choco install postgresql --params '/Password:rootpass'`
- To login to Postgres using: `psql postgres postgres`

### Setting up the database and user for the application

Usually, we need to create a database for the application we’re writing and a user to access the database. For this example, we will use “counter_user” for the user and “counter_password” for the password, and we will create “counter” as the database.

- Login to Postgres
- Create the user and password: `CREATE ROLE counter_user WITH LOGIN PASSWORD 'counter_password';`
- Give it database creation permissions: `ALTER ROLE counter_user CREATEDB;`
- Now list the users on the database: `\du`
- Exit using `\q`
- Now login using the new user: `psql postgres -Ucounter_user`
- Create the `counter` database: `CREATE DATABASE counter;`
- List the databases with: `\l`
- You should see the `counter` owned by `counter_user`.
- You can connect to the database using `\connect counter;` or `\c counter` and list the tables using `\dt;`.

### Install Poetry

- Install Poetry if you don't have it using `pip install poetry`
- Install the packages: `poetry install`
- To open a Quart shell, just do `poetry run quart shell`

### First Migration

- Run the first migration with `poetry run alembic upgrade head`
  - Subsequent migrations after models changes can be run with `pipenv run alembic revision --autogenerate -m "added counter table field"` with [some caveats](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).

### Running the application

- To run the application do: `poetry run quart run`
- Open `http://localhost:5000` on your browser

### Run Tests

- Run tests by doing `poetry run pytest`

## Using Docker

- Make sure your folder is being shared within Docker client (Preferences > Resources > File Sharing)
- Run `docker-compose up --build`. If there's a timeout error, you can restart the Quart container.
- To do the first migration:
  - `docker-compose run --rm web poetry run alembic upgrade head`
- Restart using docker-compose and head over to `http://localhost:5000` on your browser
- Run tests by doing `docker-compose run --rm web poetry run pytest -s`

## Production

- Use Hypercorn `hypercorn --bind 0.0.0.0:$PORT --reload wsgi:app`

## Codespaces

- Start the Codespace
- First time:
  - Run `poetry install`
  - Rebuild the Codespace container for changes to be applied
  - After rebuild:
    - Run `poetry shell` 
    - Do `which python` and set that as the Python interpreter
    - Do the first migration: `alembic upgrade head`
- To run the application: `poetry quart run`
  - The codespace will give you a private URL for your application
- To connect to Postgres Database: `psql -h localhost -Ucounter_user postgres`
