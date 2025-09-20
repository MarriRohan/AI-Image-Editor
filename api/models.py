from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from api.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="admin")
    active = Column(Boolean, default=True)

class StreamSource(Base):
    __tablename__ = "streams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    rtsp_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ViolationEvent(Base):
    __tablename__ = "violation_events"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    score = Column(Float)
    plate_text = Column(String)
    plate_conf = Column(Float)
    speed_kph = Column(Float)
    evidence_path = Column(String)
    evidence_plate_path = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
