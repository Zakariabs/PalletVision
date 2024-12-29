from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float, DateTime, JSON, Text, \
    PrimaryKeyConstraint, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

class StationStatus(Base):
    __tablename__ = 'StationStatus'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
class Status(Base):
    __tablename__ = 'Status'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
class PalletType(Base):
    __tablename__ = 'PalletType'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
class Station(Base):
    __tablename__ = 'Station'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    location = Column(String(256))
    station_status_id = Column(Integer, ForeignKey('StationStatus.id'))
    station_status = relationship('StationStatus')
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location':self.location,
            'status': self.station_status.name if self.station_status else "Unknown"
        }
class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class InferenceRequest(Base):
    __tablename__ = 'InferenceRequest'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey('Station.id'), nullable=False)
    initial_image_path = Column(Text, unique=True, nullable=False)
    inferred_image_path = Column(Text, unique=True)
    request_creation = Column(TIMESTAMP(timezone=True), nullable=False)
    answer_time = Column(TIMESTAMP(timezone=True))
    status_id = Column(Integer, ForeignKey('Status.id'), nullable=False)
    confidence_level = Column(Float)
    pallet_type_id = Column(Integer, ForeignKey('PalletType.id'))
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())
    station = relationship('Station')
    status = relationship('Status')
    pallet_type = relationship('PalletType')

    __table_args__ = (
        PrimaryKeyConstraint('request_id', 'timestamp', name='inferencerequest_pkey'),
        UniqueConstraint('initial_image_path', 'timestamp', name='uq_initial_image_path'),
        UniqueConstraint('inferred_image_path', 'timestamp', name='uq_inferred_image_path')
    )


    def to_dict(self):
        return {
            'request_id': self.request_id,
            'station_id': self.station_id,
            'station_name': self.station.name if self.station else None,
            'initial_image_path': self.initial_image_path,
            'inferred_image_path': self.inferred_image_path,
            'request_creation': self.request_creation.isoformat() if self.request_creation else None,
            'answer_time': self.answer_time.isoformat() if self.answer_time else None,
            'status_id': self.status_id,
            'status_name': self.status.name if self.status else None,
            'confidence_level': self.confidence_level,
            'pallet_type': self.pallet_type.name if self.pallet_type else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

class LogEntry(Base):
    __tablename__ = 'LogEntry'
    category = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now(), primary_key=True)
    detections = Column(JSON, nullable=True)
    initial_image = Column(Text, nullable=True)
    message = Column(Text, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('timestamp', name='logentry_pkey'),
    )

    def to_dict(self):
        return {
            'category':self.category,
            'timestamp':self.timestamp,
            'detections':self.detections,
            'initial_image':self.initial_image,
            'message':self.message
        }