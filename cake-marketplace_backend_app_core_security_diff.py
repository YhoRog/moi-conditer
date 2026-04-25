--- cake-marketplace/backend/app/core/security.py (原始)


+++ cake-marketplace/backend/app/core/security.py (修改后)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)