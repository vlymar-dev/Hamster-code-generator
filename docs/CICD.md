# Continuous Integration/Continuous Deployment (CI/CD)

This project uses **GitHub Actions** for continuous integration and deployment.

### Workflows:
- **Linting**: Runs Ruff on every push to ensure code quality.
- **Unit Testing**: Executes pytest to verify functionality.
- **Build and Push**: Builds Docker images and pushes them to [ghcr.io](https://ghcr.io/) on main branch updates.
