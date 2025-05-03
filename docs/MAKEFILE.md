# Makefile Commands
The `Makefile` provides shortcuts for common development, testing, and deployment tasks in Hamster Keys Generator.

## Usage
Run `make <command>` from the project root. Use make help to list all available commands:
```cmd
make help
```

## Commands

### Development
- `make local-up`: Start local development databases (Postgres, Redis) in detached mode.
- `make local-down`: Stop local development databases.
- `make lint`: Run code quality checks (Ruff linting, formatting, and pre-commit hooks).
- `make tests-run`: Run tests with coverage. Use `make tests-run HTML=true` for an HTML coverage report.
- `make run-main`: Run the main application (bot, keygen, or both) via main.py.

### Database
- `make migrate-apply`: Apply all pending database migrations using Alembic.

### Localization
- `make babel-input`: Extract translatable strings into messages.pot.
- `make babel-init LANG=<lang>`: Initialize a new language catalog (e.g., `make babel-init LANG=fr`).
- `make babel-update`: Update all language catalogs with new messages.
- `make babel-compile`: Compile translation files to MO format.

### Production
- `make prod-build`: Build and start production services with Docker Compose.
- `make prod-up`: Start production services without rebuilding.
- `make prod-down`: Stop production services.
- `make prod-clear-all`: Stop and remove production services, including volumes and orphaned containers.

### Services
- `make services-up`: Start all services (Postgres, Redis, migrations, bot) without keygen.
- `make services-down`: Stop all services.
- `make storages-clear`: Remove storage containers and volumes (warning: deletes all data).

### Examples
*Start a local development environment:*
```sh
make local-up && make migrate-apply && make run-main
```

*Run tests with coverage:*
```sh
make tests-run
```

*Add a new language (e.g., French):*
```sh
make babel-init LANG=fr
```

### Adding New Commands
Edit the Makefile to add custom tasks. Ensure commands are portable and include a description with ## for make help:
```sh
.PHONY: my-task  ## Description of my task
my-task:
echo "Running my task"
```

### Related Documentation
Testing for details on running and writing tests.
Environment Setup for configuring .env variables.
