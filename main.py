from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash

from database import SessionLocal
from models import User
from schemas import UserCreate, UserLogin
from auth import create_access_token, get_current_user


app = FastAPI(
    title="Business Operations API",
    description="API for managing business operations",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


password_hash = PasswordHash.recommended()


@app.get("/")
def home():
    return {
        "message": "Business Operations API is running!"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }


@app.post("/users/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        form_data.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "role": existing_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user
    }