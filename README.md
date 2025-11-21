# COMA

Computational Mathematics event of PRIME.

## Development

### Locally

The python dependencies are managed with [uv](https://docs.astral.sh/uv/) go there and install it.

(If you have asdf, you can also run `sh .asdf-plugins`, `asdf install`, and `asdf reshim` instead.)

Install all the dependencies with:

```console
uv sync
npm i
```

Activate the virtual environment with:

```console
source .venv/bin/activate
```

Create an `.env` file:

```console
cp .env.sample .env
```

The defaults should suffice for development.

#### Run the api server:

```console
./scripts/run_dev.sh
```

This will start a local development server on port `8000`.

#### Database

For a development database, either install Postgres, or use `docker compose -f docker-compose.dev.yml up -d dev-db` as mentioned below.

### Using docker

If you have `docker compose` installed, you can also use the `docker-compose.dev.yml` file.

Create it's own .env file:

```console
cp .docker-env-dev.sample .docker-env-dev
```

Start the database using:

```console
docker compose -f docker-compose.dev.yml up -d dev-db
```

Start the development webserver with:

```console
docker compose -f docker-compose.dev.yml up --build -d dev-backend
docker compose -f docker-compose.dev.yml logs -f dev-backend
```

You can also start a development shell using:

```console
docker compose -f docker-compose.dev.yml exec dev-backend bash
```

This will start a local development server on port `8000` (port `80` within the container).

### OpenAPI

To see and interact with the available endpoints, see `http://localhost:8000/docs`.

### Formatting

To format the python code in place, run:

```console
./scripts/format.sh
```

### Migrations

After changing a model (for example, adding a column), create a revision:

```console
alembic revision --autogenerate -m "Add column ..."
```

After creating the revision, run the migration in the database (this is what will actually change the database):

```console
alembic upgrade head
```

Or in docker compose:

```console
docker compose -f docker-compose.dev.yml exec dev-backend alembic upgrade head
```

### Admin

To create an admin user in the dev database, run:

```console
podman compose -f docker-compose.dev.yml exec dev-db psql coma coma -c"INSERT INTO team (name, password, admin) VALUES ('admin', 'admin', true);"
```
