# Hamster Keys Generator

[![Lint and Test](https://github.com/vlymar-dev/Hamster-code-generator/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/vlymar-dev/Hamster-code-generator/actions/workflows/lint-and-test.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12.5-3776AB?style=flat&logo=Python&logoColor=yellow)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.8-336791?style=flat&logo=PostgreSQL&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-5.2.1-DC382D?style=flat&logo=Redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-24.0-2496ED?style=flat&logo=Docker&logoColor=white)](https://www.docker.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.10.0-3776AB?style=flat&logo=telegram&logoColor=white)](https://aiogram.dev/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)


![Hamster code](./static/image.png)

## Table of Contents
- [Project Description](#project-description)
- [Main Features](#main-features)
- [Quick Setup and Running](#quick-setup-and-running)
- [Bot Commands](#bot-commands)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- **Additional Resources**
  - [Documentation](#documentation)


## Project Description

**Hamster Keys Generator** is an automated system for generating and managing promo codes for games,
integrated with a Telegram bot for user interaction. It leverages `PostgreSQL` for storing promo codes,
`Redis` for session management and caching, and `aiohttp` for asynchronous API requests.
Proxy support ensures reliable game API access, while a multilingual interface enhances user experience.

*⭐ Star this repository to support the project!*
> *Note: Multilingual support is currently under refactoring. Only English is available for now. Contributions are welcome!*

## Main Features

### Telegram Bot
- **Promo Code Distribution**: Users claim keys via a user-friendly multilingual interface.
- **Admin Tools**: Manage users, settings, and multilingual notifications with image support and detailed reports.
- **Rate-Limiting**: Prevents abuse by limiting promo code requests per user.
- **Donation System**: Supports Telegram Stars with fixed/custom amounts, payment confirmation, and refund options.
- **Referral Links**: Users can promote projects and earn bonuses via referral invites.
- **Achievements**: Tracks user activity and rewards progress with special bonuses.
- **Boosted Key Counts(`POPULARITY_COEFFICIENT`)**: Increases displayed key counts to enhance user engagement.


### Keygen
- **Automated Code Generation**: Generates promo codes for multiple games and stores them in PostgreSQL.
- **Reliable API Access**: Uses proxies to bypass geographical restrictions and rate limits.
- **Robust Logging**: Logs all generation stages with automatic restarts on errors.

### Flexible Startup
- Run the Telegram bot, keygen, or both using configurable startup methods.


## Quick Setup and Running
*Follow these steps to set up and run **Hamster Keys Generator** for development or production.*

### Requirements
- Python 3.12+
- PostgreSQL 16.8+
- Redis 5.2.1+
- Docker (optional for local development, recommended for production)

### Steps:
1. **Clone the Repository**:
    ```sh
    git clone https://github.com/vlymar-dev/Hamster-code-generator
    cd Hamster-code-generator

2. **Set up environment variables**:
    ```sh
    cp .env.example .env

*Edit `.env` to set database, Redis, Telegram bot token, and proxy settings. See [Environment Setup](docs/ENV_SETUP.md) for details.*

3. **Install dependencies**:
    For production:
   ```sh
   pip install -r requirements.txt
   ```
   *For development (includes testing and linting tools)*:
   ```sh
   pip install -r requirements-dev.txt
   ```

4. **Set Up Proxies** (Optional):

*Add proxy servers to `.proxies.txt` for API requests. See [Proxy Setup](docs/PROXIES.md) for formatting and usage.*

5. **Start Services**:
    ```sh
    make local-up
    ```

6. Apply database migrations:
    ```sh
    make migrate-apply

7. **Run the Application**:
Start the bot, keygen, or both:
    ```sh
    python main.py
    ```
*Configure `STARTUP_METHOD` in `.env`*:
- `0` (KeygenAndBot): Run both bot and keygen.
- `1` (OnlyKeygen): Run keygen only.
- `2` (OnlyBot): Run bot only.


### Development Setup
- **Install pre-commit hooks** for linting and formatting:
    ```sh
    pre-commit install
    ```

- **Run tests** to verify setup:
  ```sh
  make tests-run
  ```

- **Check Makefile** for additional development commands:
  ```sh
  make help
  ```

### Logging
Logs are saved in `var/logs`, rotated daily, with a 10-day retention period.

### Stopping Services
- Stop Docker services:
    ```sh
    make local-down
    ```

## Bot Commands
Configure these commands in [BotFather](https://t.me/BotFather).

### User Commands
- `/start`: Start the bot.
- `/change_language`: Switch language (English-only currently).
- `/paysupport`: Donate via Telegram Stars.

### Admin Commands
- `/admin`: Access the admin panel.


## Project Structure
  ```cmd
  .
  ├── bot/            # Telegram bot logic
  ├── keygen/         # Promo code generation logic
  ├── infrastructure/ # Config, DB, and utilities
  ├── tests/          # Unit tests
  ├── main.py         # Application entry point
  └── Makefile        # Development commands
  ```
*See [Project Structure Documentation](docs/PROJECT_STRUCTURE.md) for details.*

## Contributing
We welcome contributions to Hamster-code-generator. To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them to your branch.
4. Update your branch from the main repository:
    ```sh
    git fetch upstream
    git merge upstream/main
    ```
5. Submit a pull request.

We will review your pull request and provide feedback as needed.

## Security
- **Environment Variables**: Store sensitive data (API keys, tokens) in .env, not in code.
- **Encryption**: Promo codes and user data are encrypted in transit and at rest.
- **Access Control**: Admin commands use role-based access.
- **Proxies**: Secure API requests with proxy support.
Report security issues via [GitHub Issues](https://github.com/dev-lymar/Hamster-code-generator/issues) or email (add contact).


## License
This project is licensed under the [MIT License](LICENSE).

## Documentation
- [Environment Setup](docs/ENV_SETUP.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Proxy Setup](docs/PROXIES.md)
- [Testing](docs/TESTING.md)
- [Makefile Commands](docs/MAKEFILE.md)
- [CI/CD Configuration](docs/CICD.md)
