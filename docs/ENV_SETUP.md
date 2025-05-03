# Environment Configuration Guide

## All Environment Variables

### Bot Configuration
| Variable                     | Description                        | Example Value           | Required |
|------------------------------|------------------------------------|-------------------------|----------|
| `BOT_TOKEN`                  | Telegram bot token from @BotFather | `123456:ABC-DEF1234ghI` | Yes      |
| `BOT_ADMIN_ACCESS_IDS`       | Admin user IDs (JSON array)        | `[12345678, 87654321]`  | Yes      |
| `BOT_SUPPORT_LINK`           | Support chat URL                   | `https://t.me/...`      | No       |
| `BOT_NAME`                   | Bot display name                   | `MySuperBot`            | Yes      |
| `BOT_DEFAULT_LANGUAGE`       | Default language (ISO 639-1)       | `en`, `ru`              | Yes      |
| `BOT_POPULARITY_COEFFICIENT` | Popularity metric multiplier       | `1.0`                   | Yes      |
| `BOT_REFERRAL_THRESHOLD`     | Minimum referrals for rewards      | `5`                     | Yes      |

### Database Configuration
| Variable          | Description              | Default              | Production Guidelines         |
|-------------------|--------------------------|----------------------|-------------------------------|
| `DB_NAME`         | PostgreSQL database name | `hamster`            | Use project-specific name     |
| `DB_USER`         | Database username        | `postgres`           | Create dedicated user         |
| `DB_PASSWORD`     | Database password        | `postgres`           | 12+ chars, special characters |
| `DB_PORT`         | PostgreSQL port          | `5432`               | Keep default                  |
| `DB_HOST`         | Database host            | `0.0.0.0`            | Use internal DNS              |
| `DB_LOCAL_PORT`   | Local machine port       | `5432`               | Avoid conflict with services  |
| `DB_OUT_PORT`     | External exposed port    | `5432`               | Different from local port     |
| `DATABASE_DRIVER` | SQLAlchemy async driver  | `postgresql+asyncpg` | Do not change                 |

### Redis Configuration
| Variable         | Description                | Default     | Valid Range                 |
|------------------|----------------------------|-------------|-----------------------------|
| `REDIS_HOST`     | Redis server address       | `localhost` | -                           |
| `REDIS_PORT`     | Redis port                 | `6379`      | 0-65535                     |
| `REDIS_DB`       | Redis database index       | `0`         | 0-15                        |
| `REDIS_PASSWORD` | Authentication password    | `-`         | **Mandatory in production** |
| `REDIS_TTL`      | Default key TTL (seconds)  | `3600`      | ≥60                         |
| `REDIS_FSM_TTL`  | FSM data TTL (seconds)     | `3600`      | ≥300                        |
| `REDIS_DATA_TTL` | Regular data TTL (seconds) | `7200`      | ≥600                        |

### Payment Configuration
| Variable      | Description           | Format Example              |
|---------------|-----------------------|-----------------------------|
| `WALLET_TRC`  | TRON (TRC20) address  | `TAbc123...` (34 chars)     |
| `WALLET_TON`  | TON wallet address    | `EQAbc123...` (48 chars)    |

### Deployment Configuration
| Variable           | Description                 | Values           | Default   | Usage Example                   |
|--------------------|-----------------------------|------------------|-----------|---------------------------------|
| `PRODUCTION_MODE`  | Enable production settings  | `True/False`     | `False`   | `PRODUCTION_MODE=True`          |
| `IMAGE_TAG`        | Docker image version        | `latest`, `v1.2` | `latest`  | Use fixed tags in production    |
| `STARTUP_METHOD`   | Service initialization mode | `0-2`            | `2`       | `0=Keygen+Bot, 1=Keygen, 2=Bot` |


## Security Best Practices
1. Never commit actual `.env` to version control
2. Use different credentials for development/production
3. Rotate secrets every 90 days
4. In production:
   - Set `PRODUCTION_MODE=True`
   - Use 16+ character passwords
   - Prefer internal DNS over IP addresses
   - Enable 2FA for wallet access
