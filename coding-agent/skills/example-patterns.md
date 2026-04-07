# Example Code Patterns

This skill demonstrates domain expertise that can be loaded on-demand.

## Python Error Handling

### Use Context Managers
```python
# Good: Automatic cleanup
with open('file.txt') as f:
    content = f.read()

# Bad: Manual cleanup
f = open('file.txt')
try:
    content = f.read()
finally:
    f.close()
```

### Exception Chaining
```python
# Good: Preserve stack trace
try:
    result = api_call()
except APIError as e:
    raise CustomError(f"Failed to fetch data: {e}") from e

# Bad: Lose context
try:
    result = api_call()
except APIError:
    raise CustomError("Failed")  # Lost original error
```

### Specific Exceptions
```python
# Good: Handle specific errors
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None

# Bad: Catch everything
try:
    data = json.loads(content)
except:  # Too broad
    return None
```

## Database Patterns

### Connection Pooling
```python
# Good: Use connection pool
from db import get_connection

with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    
# Bad: New connection each time
conn = create_connection()  # Expensive!
cursor = conn.cursor()
```

### Parameterized Queries
```python
# Good: Parameterized (safe from SQL injection)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Bad: String formatting (SQL injection risk)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Transaction Management
```python
# Good: Explicit transaction
with db.transaction():
    db.execute("INSERT INTO orders ...")
    db.execute("UPDATE inventory ...")
    # Commits on success, rolls back on error

# Bad: Auto-commit (partial state possible)
db.execute("INSERT INTO orders ...")
db.execute("UPDATE inventory ...")  # If this fails, order is orphaned
```

## API Design Patterns

### RESTful Resources
```python
# Good: Resource-based
GET /users/123
GET /users/123/orders

# Bad: Action-based
GET /getUser?id=123
GET /getUserOrders?userId=123
```

### Pagination
```python
# Good: Cursor pagination (stable)
GET /orders?cursor=abc123&limit=20

# Bad: Offset pagination (unstable with changes)
GET /orders?offset=0&limit=20
```

### Error Responses
```python
# Good: Structured errors
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Email is required",
        "field": "email"
    }
}

# Bad: Unstructured
{
    "error": "Email is required"
}
```

## Testing Patterns

### Arrange-Act-Assert
```python
def test_user_creation():
    # Arrange
    user_data = {"email": "test@example.com"}
    
    # Act
    user = create_user(user_data)
    
    # Assert
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Test Fixtures
```python
# Good: Reusable fixtures
@pytest.fixture
def test_user():
    return User(email="test@example.com")

def test_login(test_user):
    result = login(test_user.email, "password")
    assert result.success
```

### Mocking External Services
```python
# Good: Mock external API
@patch('api.external_service')
def test_with_mock(mock_service):
    mock_service.return_value = {"status": "ok"}
    result = my_function()
    assert result.success
```

## Logging Patterns

### Structured Logging
```python
# Good: Structured (machine-readable)
logger.info("User logged in", extra={
    "user_id": user.id,
    "ip_address": request.ip,
    "timestamp": datetime.now()
})

# Bad: Unstructured (hard to parse)
logger.info(f"User {user.id} logged in from {request.ip}")
```

### Log Levels
```python
# DEBUG: Detailed diagnostic info
logger.debug(f"Processing item {item_id}")

# INFO: General operational info
logger.info(f"User {user_id} logged in")

# WARNING: Unexpected but handled
logger.warning(f"Rate limit reached for {api_key}")

# ERROR: Serious problem
logger.error(f"Failed to process payment: {error}")

# CRITICAL: System-level failure
logger.critical(f"Database connection lost")
```

## Concurrency Patterns

### Thread Safety
```python
# Good: Use locks for shared state
from threading import Lock

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = Lock()
    
    def increment(self):
        with self.lock:
            self.value += 1
            return self.value

# Bad: Race condition
class Counter:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1  # Not atomic!
        return self.value
```

### Async/Await
```python
# Good: Concurrent requests
async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# Bad: Sequential requests
async def fetch_all(urls):
    results = []
    for url in urls:
        results.append(await fetch(url))
    return results
```

## Security Patterns

### Input Validation
```python
# Good: Validate and sanitize
from validators import validate_email, sanitize_html

email = validate_email(user_input)
content = sanitize_html(user_content)

# Bad: Trust user input
email = user_input  # Could be anything
content = user_content  # Could contain XSS
```

### Secrets Management
```python
# Good: Environment variables
import os
api_key = os.getenv("API_KEY")

# Bad: Hardcoded
api_key = "sk-abc123"  # Never do this!
```

### Least Privilege
```python
# Good: Minimal permissions
user.grant_permission("read:own_profile")

# Bad: Excessive permissions
user.grant_permission("admin")  # Too broad
```