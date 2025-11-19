# COMA

Computational Mathematics event of PRIME.

## Setup

The dependencies are managed with [uv](https://docs.astral.sh/uv/), go there and install it.

Install all the dependencies with:

```console
uv sync
```

Activate the virtual environment with:

```console
source .venv/bin/activate
```

Create an `.env`:

```console
cp .env.sample .env
```

## Usage

Activate the virtual environment with:

```console
source .venv/bin/activate
```

#### Run the api server:

```console
./scripts/run_dev.sh
```

This will start a local development server on port `8000`

To see and interact with the available endpoints, see `http://localhost:8000/docs`

## Dev

### To format the python code in place

```console
./scripts/format.sh
```
