from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User,EmergencyContact,FakeCall,Geofence
from ..dependencies import current_user
router=APIRouter(tags=["Contacts, fake calls and geofences"])
class ContactIn(BaseModel): name:str=Field(min_length=2);phone:str=Field(min_length=5);email:str|None=None;relationship:str|None=None;group_name:str|None=None;priority:int=Field(default=1,ge=1,le=10);is_primary:bool=False;is_active:bool=True
class FakeCallIn(BaseModel): caller_name:str;caller_number:str;ringtone:str="default";delay_seconds:int=Field(default=10,ge=0,le=3600)
class FenceIn(BaseModel): name:str;latitude:float;longitude:float;radius_meters:float=Field(gt=0,le=100000)
def owned(db,model,id,u):
    x=db.query(model).filter_by(id=id,user_id=u.id).first()
    if not x:raise HTTPException(404,"Resource not found")
    return x
def save(db,obj,data):
    for k,v in data.model_dump().items():setattr(obj,k,v)
    db.add(obj);db.commit();db.refresh(obj);return {"success":True,"data":obj}
@router.get("/emergency-contacts")
def contacts(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(EmergencyContact).filter_by(user_id=u.id).order_by(EmergencyContact.priority).all()}
@router.post("/emergency-contacts",status_code=201)
def add_contact(data:ContactIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,EmergencyContact(user_id=u.id,**data.model_dump()),data)
@router.get("/emergency-contacts/{id}")
def get_contact(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":owned(db,EmergencyContact,id,u)}
@router.put("/emergency-contacts/{id}")
def update_contact(id:str,data:ContactIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,owned(db,EmergencyContact,id,u),data)
@router.delete("/emergency-contacts/{id}")
def delete_contact(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):db.delete(owned(db,EmergencyContact,id,u));db.commit();return {"success":True,"message":"Contact deleted"}
@router.patch("/emergency-contacts/{id}/priority")
def priority(id:str,priority:int,u:User=Depends(current_user),db:Session=Depends(get_db)): x=owned(db,EmergencyContact,id,u);x.priority=priority;db.commit();return {"success":True,"data":x}
@router.patch("/emergency-contacts/{id}/primary")
def primary(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
    for c in db.query(EmergencyContact).filter_by(user_id=u.id):c.is_primary=False
    x=owned(db,EmergencyContact,id,u);x.is_primary=True;db.commit();return {"success":True,"data":x}
@router.get("/fake-calls")
def calls(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(FakeCall).filter_by(user_id=u.id).all()}
@router.post("/fake-calls",status_code=201)
def add_call(data:FakeCallIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,FakeCall(user_id=u.id,**data.model_dump()),data)
@router.get("/fake-calls/{id}")
def get_call(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":owned(db,FakeCall,id,u)}
@router.put("/fake-calls/{id}")
def update_call(id:str,data:FakeCallIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,owned(db,FakeCall,id,u),data)
@router.delete("/fake-calls/{id}")
def del_call(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):db.delete(owned(db,FakeCall,id,u));db.commit();return {"success":True,"message":"Fake call deleted"}
@router.post("/fake-calls/{id}/trigger")
def trigger_call(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):x=owned(db,FakeCall,id,u);x.status="RINGING";db.commit();return {"success":True,"data":x,"message":"Simulated call triggered"}
@router.get("/geofences")
def fences(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(Geofence).filter_by(user_id=u.id).all()}
@router.post("/geofences",status_code=201)
def add_fence(data:FenceIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,Geofence(user_id=u.id,**data.model_dump()),data)
@router.put("/geofences/{id}")
def update_fence(id:str,data:FenceIn,u:User=Depends(current_user),db:Session=Depends(get_db)):return save(db,owned(db,Geofence,id,u),data)
@router.delete("/geofences/{id}")
def delete_fence(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):db.delete(owned(db,Geofence,id,u));db.commit();return {"success":True,"message":"Geofence deleted"}
