## Commands to start Postgres in Local(Mac)

# PostgreSQL with Docker on Mac - Quick Start Guide

## Prerequisites

```bash
# Install Docker Desktop for Mac if you haven't
# Download from: https://www.docker.com/products/docker-desktop
```

## Minimum Commands

### 1. Pull PostgreSQL image

```bash
docker pull postgres:latest
```

### 2. Run PostgreSQL container with volume

```bash
docker run --name my-postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql \
  -d postgres
```

That's it! PostgreSQL is now running with persistent storage.

## What Each Flag Means

- `--name my-postgres` - Names your container
- `-e POSTGRES_PASSWORD=mypassword` - Sets the password for user `postgres`
- `-p 5432:5432` - Maps port 5432 (host:container)
- `-v postgres-data:/var/lib/postgresql` - Creates a named volume for data persistence
- `-d` - Runs in detached mode (background)
- `postgres` - The image name

## Connection Details

```
Host: localhost
Port: 5432
Database: postgres
Username: postgres
Password: mypassword
```

### Recreate container using same volume (data restored)

```bash
docker run --name my-postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -d postgres
```

## Quick Test

After starting the container, test the connection:

```bash
docker exec -it my-postgres psql -U postgres -c "SELECT version();"
```

You should see PostgreSQL version information printed out.

## Database management tool
### Dbeaver - Free cross-platform Open-Source Database Management Tool

https://dbeaver.io/

### TablePlus
Modern Free Mac app
https://tableplus.com/