from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token
bearer=HTTPBearer()
def current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db)):
    payload=decode_token(credentials.credentials)
    if not payload or payload.get("type")!="access": raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid or expired token")
    user=db.get(User,payload["sub"])
    if not user: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"User not found")
    return user
