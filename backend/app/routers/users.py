from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User,Profile,MedicalInfo
from ..dependencies import current_user
router=APIRouter(prefix="/users",tags=["Users"])
class ProfileIn(BaseModel): full_name:str="";date_of_birth:str|None=None;address:str|None=None;emergency_details:str|None=None
class MedicalIn(BaseModel): blood_group:str|None=None;allergies:str|None=None;medications:str|None=None;conditions:str|None=None
def upsert(db,model,user_id,data):
    obj=db.query(model).filter_by(user_id=user_id).first() or model(user_id=user_id);db.add(obj)
    for k,v in data.model_dump().items():setattr(obj,k,v)
    db.commit();db.refresh(obj);return obj
@router.get("/profile")
def profile(u:User=Depends(current_user),db:Session=Depends(get_db)): return {"success":True,"data":db.query(Profile).filter_by(user_id=u.id).first()}
@router.put("/profile")
def update_profile(data:ProfileIn,u:User=Depends(current_user),db:Session=Depends(get_db)): return {"success":True,"data":upsert(db,Profile,u.id,data),"message":"Profile saved"}
@router.get("/medical-info")
def medical(u:User=Depends(current_user),db:Session=Depends(get_db)): return {"success":True,"data":db.query(MedicalInfo).filter_by(user_id=u.id).first()}
@router.put("/medical-info")
def update_medical(data:MedicalIn,u:User=Depends(current_user),db:Session=Depends(get_db)): return {"success":True,"data":upsert(db,MedicalInfo,u.id,data),"message":"Medical information saved"}
