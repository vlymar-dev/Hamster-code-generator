# Project Structure

Below is the directory structure for **Hamster Keys Generator**.

```
.
├── bot/                                # Telegram bot logic
│   ├── bot.py                          # Main bot entry point
│   ├── handlers/                       # Command and message handlers
│   ├── locales/                        # Multilingual translations
│   ├── middlewares/                    # Bot middleware for request processing
│   ├── filters/                        # Custom filters for handlers
│   └── keyboards/                      # Inline and reply keyboards
├── keygen/                             # Promo code generation logic
│   ├── main.py                         # Keygen entry point
│   ├── game_promo_manager.py           # Manages promo code generation
│   └── games.py                        # Game-specific API logic
├── infrastructure/                     # Configuration and utilities
│   ├── logging.py                      # Logging configuration
│   ├── db/                             # Database DAO and models
│   ├── schemas/                        # Pydantic schemas for validation
│   ├── services/                       # Business logic services
│   ├── utils/                          # Utility functions
│   └── config.py                       # Environment variable parsing
├── alembic/                            # Database migrations
│   ├── versions/                       # Migration scripts
│   └── env.py                          # Alembic configuration
├── tests/                              # Unit tests and fixtures
│   ├── conftest.py                     # Test configuration
│   ├── fixtures/                       # Test data fixtures
│   └── unit/                           # Unit test cases
├── var/                                # Logs and storage
│   ├── logs/                           # Application logs
│   └── storage/                        # Image storage
│       ├── handlers_images/            # Images for handlers
│       └── announcement_images/        # Images for notifications
├── docker_compose/                     # Docker Compose configurations
│   ├── docker-compose.services.yaml    # Service definitions (bot, migrations)
│   ├── docker-compose.storages.yaml    # Storage services (Postgres, Redis)
│   └── local.yaml                      # Local development database setup
├── main.py                             # Application entry point (bot, keygen, or both)
├── entrypoint.sh                       # Script for migrations, locale builds, and startup
├── Makefile                            # Development and deployment commands
├── redis.conf                          # Redis configuration
├── pyproject.toml                      # Linting and testing configuration
├── .pre-commit-config.yaml             # Pre-commit hook configuration
├── requirements.txt                    # Project dependencies
├── requirements-dev.txt                # Development dependencies
├── .env                                # Environment configuration
├── proxies.txt                         # Proxy list for API requests
└── README.md                           # Project overview
```

### Key Directories

- `bot/`: Contains Telegram bot logic, including command handlers, translations, and UI components.
- `keygen/`: Implements promo code generation for games, with API interaction logic.
- `infrastructure/`: Houses configuration, database access, and utility functions.
- `alembic/`: Manages database migrations.
- `tests/`: Includes unit tests and test fixtures.
- `var/`: Stores logs and images for handlers and notifications.
- `docker_compose/`: Defines Docker Compose configurations for services and databases.

### Key Files
- `main.py`: Entry point to run the bot, keygen, or both, based on STARTUP_METHOD.
- `entrypoint.sh`: Script for applying migrations, building locales, and starting the application.
- `Makefile`: Provides commands for development, testing, and deployment. See Makefile Commands.
- `.pre-commit-config.yaml`: Configures pre-commit hooks for linting and formatting.
- `requirements.txt`: Lists production dependencies.
- `requirements-dev.txt`: Lists development dependencies (includes testing and linting tools).
- `.env`: Stores environment variables. See Environment Setup.
- `proxies.txt`: Lists proxies for API requests. See Proxy Setup.
