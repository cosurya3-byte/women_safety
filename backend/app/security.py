from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash_password(value:str): return pwd_context.hash(value)
def verify_password(value:str, hashed:str): return pwd_context.verify(value,hashed)
def create_token(subject:str, refresh=False):
    expires=datetime.now(timezone.utc)+timedelta(days=settings.refresh_token_expire_days if refresh else 0,minutes=0 if refresh else settings.access_token_expire_minutes)
    return jwt.encode({"sub":subject,"type":"refresh" if refresh else "access","exp":expires},settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
def decode_token(token:str):
    try:return jwt.decode(token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm])
    except JWTError:return None
