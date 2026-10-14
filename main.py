
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, Customer, Service
from schemas import (
    UserCreate,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    ServiceCreate,
    ServiceResponse,
)
from auth import create_access_token, get_current_user


app = FastAPI(
    title="Business Operations API",
    description="API for managing business operations",
    version="1.0.0",
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
    return {"message": "Business Operations API is running!"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )


@app.post("/users/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(
        email=user.email,
        hashed_password=password_hash.hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
    }


@app.post("/users/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user or not password_hash.verify(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/users/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "message": "You are authenticated",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        },
    }


@app.post("/customers", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        owner_id=current_user.id,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@app.get("/customers", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Customer)
        .filter(Customer.owner_id == current_user.id)
        .all()
    )


@app.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.owner_id == current_user.id,
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    if customer_data.name is not None:
        customer.name = customer_data.name

    if customer_data.email is not None:
        customer.email = customer_data.email

    if customer_data.phone is not None:
        customer.phone = customer_data.phone

    db.commit()
    db.refresh(customer)

    return customer


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.owner_id == current_user.id,
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


@app.post("/services", response_model=ServiceResponse)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_service = Service(
        name=service_data.name,
        description=service_data.description,
        price=service_data.price,
        owner_id=current_user.id,
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


@app.get("/services", response_model=list[ServiceResponse])
def get_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Service)
        .filter(Service.owner_id == current_user.id)
        .all()
    )
 