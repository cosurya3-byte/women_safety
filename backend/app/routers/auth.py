from datetime import datetime,timedelta
from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User,Profile,OTPVerification
from ..security import hash_password,verify_password,create_token,decode_token
from ..dependencies import current_user
from ..config import settings
router=APIRouter(prefix="/auth",tags=["Authentication"])
class RegisterIn(BaseModel): email:EmailStr; mobile_number:str=Field(min_length=7,max_length=30); password:str=Field(min_length=8,max_length=128); full_name:str=Field(min_length=2,max_length=120)
class LoginIn(BaseModel): email:EmailStr; password:str
class OTPIn(BaseModel): email:EmailStr; otp_code:str=Field(min_length=4,max_length=8)
class RefreshIn(BaseModel): refresh_token:str
def token_payload(u):
    access=create_token(u.id); refresh=create_token(u.id,True); u.refresh_token=refresh
    return {"access_token":access,"refresh_token":refresh,"token_type":"bearer"}
@router.post("/register",status_code=201)
def register(data:RegisterIn,db:Session=Depends(get_db)):
    if db.query(User).filter((User.email==data.email)|(User.mobile_number==data.mobile_number)).first(): raise HTTPException(409,"Email or mobile number already registered")
    user=User(email=data.email,mobile_number=data.mobile_number,password_hash=hash_password(data.password)); db.add(user); db.flush(); db.add(Profile(user_id=user.id,full_name=data.full_name)); db.add(OTPVerification(user_id=user.id,otp_code="123456",expires_at=datetime.utcnow()+timedelta(minutes=10))); db.commit()
    response={"user_id":user.id,"message":"Registration created. Use development OTP 123456."}
    if settings.dev_otp_mode: response["development_otp"]="123456"
    return {"success":True,"data":response,"message":"OTP generated in development mode"}
@router.post("/verify-otp")
def verify_otp(data:OTPIn,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=data.email).first()
    otp=db.query(OTPVerification).filter_by(user_id=u.id if u else None,otp_code=data.otp_code,verified=False).order_by(OTPVerification.created_at.desc()).first()
    if not u or not otp or otp.expires_at<datetime.utcnow(): raise HTTPException(400,"Invalid or expired OTP")
    otp.verified=True;u.is_verified=True;tokens=token_payload(u);db.commit();return {"success":True,"data":tokens,"message":"Account verified"}
@router.post("/login")
def login(data:LoginIn,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=data.email).first()
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid email or password")
    if not u.is_verified: raise HTTPException(403,"Verify OTP before logging in")
    payload=token_payload(u);db.commit();return {"success":True,"data":payload,"message":"Logged in"}
@router.post("/refresh")
def refresh(data:RefreshIn,db:Session=Depends(get_db)):
    p=decode_token(data.refresh_token);u=db.get(User,p.get("sub")) if p else None
    if not p or p.get("type")!="refresh" or not u or u.refresh_token!=data.refresh_token: raise HTTPException(401,"Invalid refresh token")
    return {"success":True,"data":token_payload(u)}
@router.post("/logout")
def logout(u:User=Depends(current_user),db:Session=Depends(get_db)):
    u.refresh_token=None;db.commit();return {"success":True,"message":"Logged out"}
@router.get("/me")
def me(u:User=Depends(current_user),db:Session=Depends(get_db)):
    return {"success":True,"data":{"id":u.id,"email":u.email,"mobile_number":u.mobile_number,"is_verified":u.is_verified}}
