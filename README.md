## Overview
This is a FastAPI implementation with in-memory user management and rate limiting capabilities. The API allows creating users, making requests on their behalf, and checking their current quota usage.

## Architecture Decisions

### 1. **Modular Structure**
Aiming to promote code maintainability, scalability and reusability, I seek guidance on how to better structure FastAPI projects and adopted a structured approach to organize the project, separating concerns into different modules ensuring clear boundaries. The two following sources were used as inspiration:

- https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://fastapi.tiangolo.com/tutorial/bigger-applications/&ved=2ahUKEwjDqsrbv4STAxVmzwIHHZm0ALMQFnoECAwQAQ&usg=AOvVaw1bYv9jXhifnyGLyHmhKt32
- https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6

As a result, the project was structured as follows, with a clean architecture pattern with separation of concerns:

```
app/
├── main.py              # Application entry point
├── models/              # Define data models (domain entities) 
├── schemas/             # Pydantic schemas for data validation (DTOs, Serialization/Deserialization)
├── routers/             # Handling the different API endpoints
└── services/            # Business logic separated from API routes

tests/                   # Automated Basic tests
```

### 2. **Data Models vs Schemas**

In order to allow different validation rules for input/output and to separate internal representation (User information) from API contracts, I decided to differentiate between Data Models and Schemas:

- **`models/user.py`**: Internal representation of domain entities (User)
- **`schemas/users_schemas.py`**: Pydantic models for serializing User endpoint responses (UserResponse, QuotaResponse)
- **`schemas/requests_schema.py`**: Pydantic models for serializing request endpoint response (RequestResponse)

### 3. **Router Pattern for Endpoint Organization**

To maintain a clean and scalable API structure, endpoints are organized using FastAPI's `APIRouter` into logical groups based on resources:

```
app/routers/
├── users.py      # User-related endpoints (/users/)
└── requests.py   # Request-related endpoints (/request/)
```

### 4. **User Identification via Header**

**Design Decision:**

Authentication is not required by the assignment, but we need to identify users for per-user rate limiting. 

**Approach: `X-User-ID` Header**

```bash
curl -X POST http://localhost:8000/request/ \
  -H "X-User-ID: 123e4567-e89b-12d3-a456-426614174000"
```

The reasons behind this decision is that headers are the HTTP-standard location for authentication/identification (e.g. JTW or API Keys), thus I wanted to propose a similar approach that eases future migration to real authentication while keeping it simple.

### 5. **Service Layer Pattern**
Two main services (Instantiated classes) handle business logic:

#### **`user_service.py`**
- Manages user CRUD operations
- In-memory storage using a dictionary (`users_db`)
- Thread-safe operations (important for async contexts)

**Rationale:**
- Centralized user management
- Easy to swap storage implementation later (Redis, PostgreSQL, etc.)
- Single source of truth for user data

#### **`quota_service.py`**
- Implements rolling window rate limiting
- Tracks requests per user with timestamps with in-memory storage using a dictionary (`request_log`)
- Auto-cleanup of expired requests

**Rationale:**
- Decouples rate limiting logic from request handling
- Reusable across different endpoints
- Easy to modify rate limiting algorithm

### 6. **Rate Limiting Strategy**

#### **Rolling Window Approach**
```python
request_log[user_id] = [
    timestamp1,  # Request 1
    timestamp2,  # Request 2
    ...
]
```

**Algorithm:**
1. Filter out timestamps older than 60 seconds from the moment of the current request
2. Count remaining valid requests
3. Allow/deny based on threshold (10 requests/minute)

**Advantages:**
- More accurate than fixed windows
- No sudden quota resets
- Natural cleanup of old data

**Why not Fixed Windows?**
- Assignment description asked directly for rolling-window
- Fixed windows can allow 20 requests in 2 seconds (at window boundary)
- Rolling window provides smoother rate limiting

### 7. **Quota Auto-Reset Mechanism**

#### **On-Access Cleanup**
In order to maintain quotas, I decided to clean-up requests_log following an on-access approach instead of using a background task. The reasons are the following:
- **Memory Efficient**: 
    - Only processes active users requests_log
    - Quota service does work only when needed (**Lazy evaluation**), saving resources  when no requests are being received.
- **Simplicity**: No threading/async complexity from having a background task.

As a result, expired requests are removed from the request_log upon arrival of each request, together with:
- Checking if user can make a request
- Retrieving current quota

### 8. **HTTP Codes and Error Handling**

#### **HTTP Status Codes Used:**

In order to achieve clear communication of request successes and errors, REST conventions were followed to handle different cases:

- **200 OK**: Successful GET/POST operations
- **201 Created**: User successfully created
- **404 Not Found**: User doesn't exist
- **422 Unprocessable Entity**: Invalid data format (invalid UUID or missing headers)
- **429 Too Many Requests**: Quota exceeded (10 requests per 60-second window)

### 9. **Input Validation Strategy**

Using **Pydantic** for automatic validation and serialization of responses.

```python
class QuotaResponse(BaseModel):
    user_id: UUID = Field(description="User ID")
    requests_made: int = Field(description="Requests made in current 60-second window")
    max_requests: int = Field(default=10, description="Maximum allowed requests per window")
    window_seconds: int = Field(default=60, description="Time window in seconds")
    remaining_requests: int = Field(description="Remaining requests in current window")
```

**Rationale:**
- Declarative validation (readable and maintainable)
- Automatic OpenAPI schema generation
- Standardized error responses
- No manual validation code needed

### 10. **OpenAPI Documentation**

#### **Automatic Generation Through Annotations/Metadata:**

In order to leverage FastAPI framework and its self-documenting API, I used annotations, functions descriptions and parameters metadata where possible to provide a rich API documentation to API users. This approach eases documentation maintenance.

```python
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user with username and email"
)
```

**Documentation includes:**
- Endpoint descriptions
- Request/response schemas
- Example payloads
- Status codes
- Error responses

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
fastapi dev app/main.py
```

## Testing

```bash
# Run all tests
python -m pytest -v
```

