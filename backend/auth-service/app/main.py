import random
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from botocore.exceptions import ClientError

from .dynamodb import (
    create_table_if_not_exists,
    create_otp_table_if_not_exists,
    get_user,
    create_user,
    store_pending_otp,
    get_pending_otp,
    delete_pending_otp,
)
from .security import hash_password, verify_password, create_access_token, decode_access_token
from .email_sender import send_otp_email
from .models import SignupRequest, LoginRequest, VerifyOtpRequest, TokenResponse, UserResponse, MessageResponse
from .config import settings

_executor = ThreadPoolExecutor(max_workers=4)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table_if_not_exists()
    create_otp_table_if_not_exists()
    yield


app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)
bearer_scheme = HTTPBearer()


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@app.post("/signup", response_model=MessageResponse, status_code=202)
def signup(body: SignupRequest):
    if get_user(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    otp = str(random.randint(100000, 999999))
    hashed_otp = hash_password(otp)
    hashed_pw = hash_password(body.password)
    expires_at = int(time.time()) + settings.otp_expire_minutes * 60

    store_pending_otp(
        email=body.email,
        hashed_otp=hashed_otp,
        hashed_password=hashed_pw,
        full_name=body.full_name,
        expires_at=expires_at,
    )

    try:
        send_otp_email(to_email=body.email, otp=otp)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Check SMTP settings.")

    return MessageResponse(message=f"OTP sent to {body.email}. It expires in {settings.otp_expire_minutes} minutes.")


@app.post("/verify-otp", response_model=UserResponse, status_code=201)
def verify_otp(body: VerifyOtpRequest):
    pending = get_pending_otp(body.email)

    if not pending:
        raise HTTPException(status_code=404, detail="No pending signup for this email. Please sign up first.")

    if int(time.time()) > int(pending["expires_at"]):
        delete_pending_otp(body.email)
        raise HTTPException(status_code=410, detail="OTP has expired. Please sign up again.")

    if not verify_password(body.otp, pending["hashed_otp"]):
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    delete_pending_otp(body.email)

    created_at = datetime.now(timezone.utc).isoformat()
    try:
        user = create_user(
            email=body.email,
            hashed_password=pending["hashed_password"],
            full_name=pending["full_name"],
            created_at=created_at,
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail="Could not create user")

    return UserResponse(email=user["email"], full_name=user["full_name"], created_at=user["created_at"])


@app.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = get_user(body.email)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user["email"]})
    return TokenResponse(access_token=token)


@app.get("/me", response_model=UserResponse)
def me(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = decode_access_token(credentials.credentials)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(email=user["email"], full_name=user["full_name"], created_at=user["created_at"])
