from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
from ..database import get_db
from ..models import User,SOSIncident,Location,ThreatAssessment,Recording,ChatSession,ChatMessage,RouteRequest
from ..dependencies import current_user
from ..config import BASE_DIR,settings
router=APIRouter(tags=["Safety modules"])
class Point(BaseModel): latitude:float;longitude:float;accuracy:float|None=None;speed:float|None=None
class ThreatIn(Point): route_deviation:bool=False;duration_minutes:int=0;hour:int|None=None
class ChatIn(BaseModel): message:str=Field(min_length=1,max_length=2000);session_id:str|None=None
class RouteIn(BaseModel): origin:str;destination:str;origin_lat:float|None=None;origin_lng:float|None=None;destination_lat:float|None=None;destination_lng:float|None=None
def owned(db,model,id,u):
    x=db.query(model).filter_by(id=id,user_id=u.id).first()
    if not x: raise HTTPException(404,"Resource not found")
    return x
@router.post("/sos/activate",status_code=201)
def activate(data:Point,u:User=Depends(current_user),db:Session=Depends(get_db)):
    x=SOSIncident(user_id=u.id,latitude=data.latitude,longitude=data.longitude);db.add(x);db.commit();db.refresh(x);return {"success":True,"data":x,"message":"SOS activated. Contact notifications are simulated locally."}
@router.post("/sos/cancel")
def cancel(u:User=Depends(current_user),db:Session=Depends(get_db)):
    x=db.query(SOSIncident).filter_by(user_id=u.id,status="ACTIVE").order_by(SOSIncident.created_at.desc()).first()
    if not x:raise HTTPException(404,"No active SOS incident")
    x.status="CANCELLED";db.commit();return {"success":True,"data":x}
@router.get("/sos/status")
def sos_status(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(SOSIncident).filter_by(user_id=u.id,status="ACTIVE").order_by(SOSIncident.created_at.desc()).first()}
@router.get("/sos/history")
def sos_history(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(SOSIncident).filter_by(user_id=u.id).order_by(SOSIncident.created_at.desc()).all()}
@router.get("/sos/{id}")
def sos_get(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":owned(db,SOSIncident,id,u)}
@router.post("/sos/{id}/resolve")
def sos_resolve(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):x=owned(db,SOSIncident,id,u);x.status="RESOLVED";db.commit();return {"success":True,"data":x}
@router.post("/sos/{id}/notify-contacts")
def notify(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):owned(db,SOSIncident,id,u);return {"success":True,"message":"Mock SMS, call and push notifications recorded; no real contact was called."}
@router.post("/location")
def post_location(data:Point,u:User=Depends(current_user),db:Session=Depends(get_db)):x=Location(user_id=u.id,**data.model_dump());db.add(x);db.commit();db.refresh(x);return {"success":True,"data":x}
@router.get("/location/current")
def current_location(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(Location).filter_by(user_id=u.id).order_by(Location.created_at.desc()).first()}
@router.get("/location/history")
def location_history(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(Location).filter_by(user_id=u.id).order_by(Location.created_at.desc()).limit(200).all()}
@router.post("/location/start-tracking")
def start_tracking(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"message":"Browser tracking can now send location samples."}
@router.post("/location/stop-tracking")
def stop_tracking(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"message":"Tracking stopped in the client."}
def assess(data:ThreatIn):
    score=0; factors=[];hour=data.hour if data.hour is not None else datetime.now().hour
    if hour>=22 or hour<5:score+=30;factors.append("Late night travel")
    if data.route_deviation:score+=25;factors.append("Sudden route deviation")
    if data.speed is not None and (data.speed>20 or (data.speed==0 and data.duration_minutes>=20)):score+=20;factors.append("Unusual speed or prolonged inactivity")
    if data.duration_minutes>=45:score+=15;factors.append("Prolonged inactivity")
    score=min(score,100);level="LOW" if score<=30 else "MODERATE" if score<=60 else "HIGH" if score<=80 else "CRITICAL"
    return score,level,factors,"Consider moving toward a populated, well-lit area." if score>30 else "Continue sharing your location with trusted contacts."
@router.post("/threat/analyze")
def threat(data:ThreatIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    score,level,factors,recommendation=assess(data);x=ThreatAssessment(user_id=u.id,risk_score=score,risk_level=level,risk_factors=factors,recommendation=recommendation);db.add(x);db.commit();db.refresh(x);return {"success":True,"data":x}
@router.get("/threat/current-risk")
def current_risk(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(ThreatAssessment).filter_by(user_id=u.id).order_by(ThreatAssessment.created_at.desc()).first()}
@router.get("/threat/history")
def risk_history(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(ThreatAssessment).filter_by(user_id=u.id).order_by(ThreatAssessment.created_at.desc()).all()}
@router.post("/recordings/{kind}/start")
@router.post("/recordings/{kind}/stop")
def recording_state(kind:str,u:User=Depends(current_user)):
    if kind not in {"audio","video"}:raise HTTPException(404,"Unknown recording type")
    return {"success":True,"message":"Recording state is managed by the browser MediaRecorder."}
@router.post("/recordings/{kind}/upload",status_code=201)
async def upload(kind:str,file:UploadFile=File(...),u:User=Depends(current_user),db:Session=Depends(get_db)):
    if kind not in {"audio","video"} or not (file.content_type or "").startswith(kind+"/"):raise HTTPException(400,"Invalid media type")
    content=await file.read()
    if len(content)>25*1024*1024:raise HTTPException(413,"File exceeds 25 MB limit")
    ext={"audio":"webm","video":"webm"}[kind];safe=f"{uuid.uuid4()}.{ext}";target=BASE_DIR/settings.upload_dir/kind;target.mkdir(parents=True,exist_ok=True);(target/safe).write_bytes(content)
    x=Recording(user_id=u.id,kind=kind,file_path=f"{kind}/{safe}",content_type=file.content_type,size_bytes=len(content));db.add(x);db.commit();db.refresh(x);return {"success":True,"data":x}
@router.get("/recordings/{kind}")
def recordings(kind:str,u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(Recording).filter_by(user_id=u.id,kind=kind).all()}
@router.get("/recordings/{kind}/{id}")
def recording(kind:str,id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):x=owned(db,Recording,id,u);return {"success":True,"data":x}
@router.delete("/recordings/{kind}/{id}")
def delete_recording(kind:str,id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
    x=owned(db,Recording,id,u);p=BASE_DIR/settings.upload_dir/x.file_path
    if p.exists():p.unlink()
    db.delete(x);db.commit();return {"success":True,"message":"Recording deleted"}
def bot_reply(message):
    m=message.lower()
    if any(w in m for w in ["attack","help","unsafe","emergency","danger"]):return "If you are in immediate danger, activate SOS now and call your local emergency services. Move to a populated, well-lit place if safe to do so."
    if "first aid" in m:return "For serious bleeding, apply firm pressure with clean cloth and seek urgent medical help. Do not delay emergency care."
    if "legal" in m:return "Document dates, messages and evidence safely. A local women’s legal-aid organization can explain options confidentially."
    return "I can offer safety planning, basic first-aid guidance, and emergency preparation. I am not a replacement for emergency services."
@router.post("/chatbot/message")
def chat(data:ChatIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    s=db.query(ChatSession).filter_by(id=data.session_id,user_id=u.id).first() if data.session_id else None
    if not s:s=ChatSession(user_id=u.id);db.add(s);db.flush()
    answer=bot_reply(data.message);db.add_all([ChatMessage(session_id=s.id,role="user",content=data.message),ChatMessage(session_id=s.id,role="assistant",content=answer)]);db.commit();return {"success":True,"data":{"session_id":s.id,"message":answer}}
@router.get("/chatbot/history")
def chat_history(u:User=Depends(current_user),db:Session=Depends(get_db)):
    sessions=db.query(ChatSession).filter_by(user_id=u.id).all();ids=[s.id for s in sessions];return {"success":True,"data":db.query(ChatMessage).filter(ChatMessage.session_id.in_(ids)).order_by(ChatMessage.created_at).all() if ids else []}
@router.delete("/chatbot/history")
@router.post("/chatbot/clear")
def clear_chat(u:User=Depends(current_user),db:Session=Depends(get_db)):
    ids=[x.id for x in db.query(ChatSession).filter_by(user_id=u.id)];db.query(ChatMessage).filter(ChatMessage.session_id.in_(ids)).delete(synchronize_session=False) if ids else None;db.query(ChatSession).filter_by(user_id=u.id).delete();db.commit();return {"success":True,"message":"Chat history cleared"}
@router.post("/routes/recommend",status_code=201)
@router.post("/routes/alternative",status_code=201)
def route(data:RouteIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
    result={"route_type":"recommended","note":"Local placeholder route. OpenStreetMap tiles provide visual context; routing provider is integration-ready.","safety_features":["Prefer well-lit, populated roads when available"],"coordinates":[[data.origin_lat,data.origin_lng],[data.destination_lat,data.destination_lng]]};x=RouteRequest(user_id=u.id,origin=data.origin,destination=data.destination,risk_score=25,route_data=result);db.add(x);db.commit();db.refresh(x);return {"success":True,"data":x}
@router.get("/routes/history")
def routes(u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":db.query(RouteRequest).filter_by(user_id=u.id).all()}
@router.get("/routes/{id}")
def route_get(id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):return {"success":True,"data":owned(db,RouteRequest,id,u)}
