from fastapi import HTTPException, Depends, APIRouter, Header
from sqlalchemy.orm import Session
import bcrypt
import uuid
from models.user import User
from pydantic_schemas.user_create import UserCreate
from database import get_db
from sqlalchemy.orm import Session
from pydantic_schemas.user_login import UserLogin
import jwt as jwt
from middleware.auth_middleware import auth_middleware
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post('/signup', status_code=201)
def signup_user(user: UserCreate, db: Session = Depends(get_db)):  # Inject DB session
    user_db = db.query(User).filter(User.email == user.email).first()

    if user_db:
        raise HTTPException(status_code=400, detail="User with the same email already exists!")

    # Hash password before storing
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

    user_db = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
        password=hashed_pw  # Store hashed password
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)  # Refresh to return updated data

    return {"message": "User created successfully!", "user_id": user_db.id}

@router.post('/login')
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()

    if not user_db:
        raise HTTPException(status_code=400, detail="User not found!")

    # Ensure the stored password is in bytes for bcrypt comparison
    if not bcrypt.checkpw(user.password.encode(), user_db.password.encode() if isinstance(user_db.password, str) else user_db.password):
        raise HTTPException(status_code=400, detail="Invalid password!")

    # Specify an algorithm when encoding the JWT token
    token = jwt.encode({'id': user_db.id}, 'password_key', algorithm='HS256')

    return {"token": token, "user": {"id": user_db.id, "email": user_db.email, "name": user_db.name}}

@router.get('/')
def current_user_data(db: Session = Depends(get_db),
                    user_dict = Depends(auth_middleware)):
    user = db.query(User).filter(User.id == user_dict.get['uid']).options(
        joinedload(user.favorites)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return user