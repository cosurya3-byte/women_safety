import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

def uid(): return str(uuid.uuid4())
class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class User(Base, Timestamped):
    __tablename__="users"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); email: Mapped[str]=mapped_column(String(255), unique=True, index=True); mobile_number: Mapped[str]=mapped_column(String(30), unique=True, index=True); password_hash: Mapped[str]=mapped_column(String(255)); is_verified: Mapped[bool]=mapped_column(Boolean, default=False); refresh_token: Mapped[str|None]=mapped_column(String(512), nullable=True)
class Profile(Base, Timestamped):
    __tablename__="user_profiles"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"), unique=True, index=True); full_name: Mapped[str]=mapped_column(String(120), default=""); date_of_birth: Mapped[str|None]=mapped_column(String(20)); address: Mapped[str|None]=mapped_column(Text); emergency_details: Mapped[str|None]=mapped_column(Text)
class MedicalInfo(Base, Timestamped):
    __tablename__="medical_information"; id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"), unique=True, index=True); blood_group: Mapped[str|None]=mapped_column(String(10)); allergies: Mapped[str|None]=mapped_column(Text); medications: Mapped[str|None]=mapped_column(Text); conditions: Mapped[str|None]=mapped_column(Text)
class OTPVerification(Base, Timestamped):
    __tablename__="otp_verifications"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); otp_code: Mapped[str]=mapped_column(String(8)); expires_at: Mapped[datetime]=mapped_column(DateTime); verified: Mapped[bool]=mapped_column(Boolean,default=False)
class EmergencyContact(Base, Timestamped):
    __tablename__="emergency_contacts"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); name: Mapped[str]=mapped_column(String(120)); phone: Mapped[str]=mapped_column(String(30)); email: Mapped[str|None]=mapped_column(String(255)); relationship: Mapped[str|None]=mapped_column(String(80)); group_name: Mapped[str|None]=mapped_column(String(80)); priority: Mapped[int]=mapped_column(Integer,default=1); is_primary: Mapped[bool]=mapped_column(Boolean,default=False); is_active: Mapped[bool]=mapped_column(Boolean,default=True)
class SOSIncident(Base, Timestamped):
    __tablename__="sos_incidents"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); status: Mapped[str]=mapped_column(String(30),default="ACTIVE"); latitude: Mapped[float|None]=mapped_column(Float); longitude: Mapped[float|None]=mapped_column(Float); notes: Mapped[str|None]=mapped_column(Text)
class Location(Base, Timestamped):
    __tablename__="locations"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); latitude: Mapped[float]=mapped_column(Float); longitude: Mapped[float]=mapped_column(Float); accuracy: Mapped[float|None]=mapped_column(Float); speed: Mapped[float|None]=mapped_column(Float); tracking_active: Mapped[bool]=mapped_column(Boolean,default=False)
class Geofence(Base, Timestamped):
    __tablename__="geofences"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); name: Mapped[str]=mapped_column(String(100)); latitude: Mapped[float]=mapped_column(Float); longitude: Mapped[float]=mapped_column(Float); radius_meters: Mapped[float]=mapped_column(Float)
class ThreatAssessment(Base, Timestamped):
    __tablename__="threat_assessments"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); risk_score: Mapped[int]=mapped_column(Integer); risk_level: Mapped[str]=mapped_column(String(20)); risk_factors: Mapped[list]=mapped_column(JSON,default=list); recommendation: Mapped[str]=mapped_column(Text)
class Recording(Base, Timestamped):
    __tablename__="recordings"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); sos_incident_id: Mapped[str|None]=mapped_column(ForeignKey("sos_incidents.id")); kind: Mapped[str]=mapped_column(String(10)); file_path: Mapped[str]=mapped_column(String(255)); content_type: Mapped[str]=mapped_column(String(100)); duration_seconds: Mapped[float|None]=mapped_column(Float); size_bytes: Mapped[int]=mapped_column(Integer)
class FakeCall(Base, Timestamped):
    __tablename__="fake_calls"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); caller_name: Mapped[str]=mapped_column(String(120)); caller_number: Mapped[str]=mapped_column(String(30)); ringtone: Mapped[str]=mapped_column(String(80),default="default"); delay_seconds: Mapped[int]=mapped_column(Integer,default=10); status: Mapped[str]=mapped_column(String(20),default="SCHEDULED")
class ChatSession(Base, Timestamped):
    __tablename__="chat_sessions"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); title: Mapped[str]=mapped_column(String(150),default="Safety assistant")
class ChatMessage(Base, Timestamped):
    __tablename__="chat_messages"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); session_id: Mapped[str]=mapped_column(ForeignKey("chat_sessions.id"),index=True); role: Mapped[str]=mapped_column(String(20)); content: Mapped[str]=mapped_column(Text)
class RouteRequest(Base, Timestamped):
    __tablename__="route_requests"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); origin: Mapped[str]=mapped_column(String(255)); destination: Mapped[str]=mapped_column(String(255)); risk_score: Mapped[int]=mapped_column(Integer); route_data: Mapped[dict]=mapped_column(JSON,default=dict)
class Notification(Base, Timestamped):
    __tablename__="notifications"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str]=mapped_column(ForeignKey("users.id"),index=True); channel: Mapped[str]=mapped_column(String(30)); status: Mapped[str]=mapped_column(String(30)); message: Mapped[str]=mapped_column(Text)
class AuditLog(Base, Timestamped):
    __tablename__="audit_logs"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id: Mapped[str|None]=mapped_column(ForeignKey("users.id"),index=True); action: Mapped[str]=mapped_column(String(100)); resource_type: Mapped[str]=mapped_column(String(80)); resource_id: Mapped[str|None]=mapped_column(String(36)); details: Mapped[dict]=mapped_column(JSON,default=dict)
