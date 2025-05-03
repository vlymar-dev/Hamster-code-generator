# Testing

**Hamster Keys Generator** uses pytest for unit testing.

## Running Tests
1. Install development dependencies:
   ```sh
   pip install -r requirements-dev.txt
   ```
2. Run tests with coverage:
   ```sh
   make tests-run
   ```
3. View HTML coverage report:
   ```sh
   make tests-run HTML=true
   ```

## Writing Tests
- Place tests in `tests/unit/`.
- Use fixtures in `tests/fixtures/` for reusable test data.
- Follow naming conventions: `test_<module>_<function>.py`.

## Example Test
```python
import pytest
from bot.handlers import start_handler

@pytest.fixture
def mock_user():
    return {"id": 123, "username": "testuser"}

def test_start_handler(mock_user):
    response = start_handler(mock_user)
    assert response == "Welcome to Hamster Keys Generator!"
```
