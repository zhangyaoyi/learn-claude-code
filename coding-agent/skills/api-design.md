# API Design Best Practices

Domain expertise for designing robust, scalable APIs.

## RESTful Principles

### Resource-Oriented Design
```
# Good: Resources are nouns
GET    /users/123           # Get user
POST   /users               # Create user
PUT    /users/123           # Update user
DELETE /users/123           # Delete user
GET    /users/123/orders    # Get user's orders

# Bad: Actions are verbs
GET    /getUser?id=123
POST   /createUser
POST   /updateUser
POST   /deleteUser
```

### HTTP Methods
```
GET     - Retrieve (safe, idempotent)
POST    - Create (not idempotent)
PUT     - Replace (idempotent)
PATCH   - Partial update (idempotent)
DELETE  - Remove (idempotent)
```

### Status Codes
```
# Success
200 OK           - General success
201 Created      - Resource created
204 No Content   - Success, no body

# Client Errors
400 Bad Request      - Invalid input
401 Unauthorized     - Not authenticated
403 Forbidden        - Not authorized
404 Not Found        - Resource doesn't exist
409 Conflict         - State conflict
422 Unprocessable    - Validation error
429 Too Many Requests - Rate limited

# Server Errors
500 Internal Error   - Unexpected failure
502 Bad Gateway      - Upstream failure
503 Unavailable      - Service down
```

## Request/Response Patterns

### Pagination
```json
// Request
GET /orders?page=2&limit=20

// Response
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}

// Better: Cursor pagination (stable)
GET /orders?cursor=abc123&limit=20

{
  "data": [...],
  "pagination": {
    "next_cursor": "def456",
    "has_more": true
  }
}
```

### Filtering & Sorting
```
GET /orders?status=active&sort=created_at:desc

// Multiple filters
GET /orders?status=active&priority=high&customer_id=123

// Range filters
GET /orders?created_after=2024-01-01&created_before=2024-12-31
```

### Field Selection
```
// Request only needed fields
GET /users/123?fields=id,name,email

// Response
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
  // Other fields omitted
}
```

## Error Handling

### Structured Errors
```json
// Single error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "field": "email",
    "details": {
      "expected": "email format",
      "received": "not-an-email"
    }
  }
}

// Multiple errors
{
  "errors": [
    {
      "code": "REQUIRED_FIELD",
      "field": "email",
      "message": "Email is required"
    },
    {
      "code": "INVALID_FORMAT",
      "field": "phone",
      "message": "Invalid phone number format"
    }
  ]
}
```

### Error Codes
```
VALIDATION_ERROR    - Invalid input
AUTH_REQUIRED       - Authentication needed
FORBIDDEN           - Not authorized
NOT_FOUND           - Resource not found
CONFLICT            - State conflict
RATE_LIMITED        - Too many requests
INTERNAL_ERROR      - Server error
```

## Versioning

### URL Path Versioning
```
/api/v1/users
/api/v2/users
```

### Header Versioning
```
GET /users
Accept: application/vnd.myapi.v2+json
```

### Version Lifecycle
```
v1 (deprecated)  -> v2 (current) -> v3 (beta)
    6 months          2 years          preview
```

## Authentication & Authorization

### JWT Pattern
```json
// Request
POST /auth/login
{
  "email": "user@example.com",
  "password": "secret"
}

// Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600
}

// Authenticated Request
GET /users/me
Authorization: Bearer eyJ...
```

### API Key Pattern
```
// Header
GET /api/users
X-API-Key: your-api-key

// Query param (less secure)
GET /api/users?api_key=your-api-key
```

## Rate Limiting

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200

// When limited
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

### Rate Limit Strategies
```
// Fixed window
100 requests per minute

// Sliding window
100 requests per rolling 60 seconds

// Token bucket
Burst of 20, then 10/second
```

## Caching

### Cache Headers
```
Cache-Control: max-age=3600, public
ETag: "abc123"
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT

// Conditional requests
If-None-Match: "abc123"
If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT
```

### Cache Strategies
```
// Immutable resources
Cache-Control: max-age=31536000, immutable

// Frequently updated
Cache-Control: max-age=60, stale-while-revalidate=300

// Private data
Cache-Control: max-age=3600, private
```

## Documentation

### OpenAPI/Swagger
```yaml
openapi: 3.0.0
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### Example Requests
```json
// Always include examples
{
  "example": {
    "request": {
      "email": "user@example.com",
      "name": "John Doe"
    },
    "response": {
      "id": 123,
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

## Security Best Practices

### Input Validation
```python
# Always validate
{
  "email": "string (email format)",
  "age": "integer (0-150)",
  "role": "string (enum: admin, user, guest)"
}
```

### Rate Limiting
```python
# Per-user and global limits
{
  "anonymous": "10/hour",
  "authenticated": "100/hour",
  "admin": "1000/hour"
}
```

### HTTPS Everywhere
```
// Redirect HTTP to HTTPS
HTTP 301 -> HTTPS

// HSTS header
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Monitoring

### Health Check
```
GET /health
{
  "status": "healthy",
  "version": "2.1.0",
  "uptime": 86400,
  "dependencies": {
    "database": "healthy",
    "cache": "healthy",
    "queue": "degraded"
  }
}
```

### Metrics
```
// Response times
response_time_ms{endpoint="/users", method="GET"}

// Error rates
error_rate{endpoint="/users", status="500"}

// Request volume
request_count{endpoint="/users", method="POST"}
```