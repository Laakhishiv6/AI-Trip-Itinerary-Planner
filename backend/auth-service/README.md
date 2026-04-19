# Auth Service

Authentication microservice for the AI Trip Itinerary Planner.  
Runs on **port 8002**. Stores users in DynamoDB table `users` (partition key: `email`).

## Setup

```bash
cd backend/auth-service

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your AWS credentials and a strong JWT_SECRET_KEY
```

## Run

```bash
uvicorn app.main:app --reload --port 8002
```

## Endpoints

| Method | Path      | Auth     | Description                        |
|--------|-----------|----------|------------------------------------|
| GET    | /health   | No       | Health check                       |
| POST   | /signup   | No       | Register a new user                |
| POST   | /login    | No       | Login and receive JWT              |
| GET    | /me       | Bearer   | Get current user info              |

### POST /signup
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### POST /login
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
Response:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### GET /me
Header: `Authorization: Bearer <jwt>`

## Environment Variables

| Variable              | Description                        |
|-----------------------|------------------------------------|
| AWS_REGION            | AWS region (default: ap-south-1)   |
| AWS_ACCESS_KEY_ID     | AWS access key                     |
| AWS_SECRET_ACCESS_KEY | AWS secret key                     |
| JWT_SECRET_KEY        | Secret used to sign JWTs           |
| JWT_ALGORITHM         | Algorithm (default: HS256)         |
| JWT_EXPIRE_MINUTES    | Token TTL in minutes (default: 60) |
