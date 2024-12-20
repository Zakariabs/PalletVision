from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float, DateTime, JSON
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
    request_id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('Station.id'), nullable=False)
    initial_image_path  = Column(String(256), unique=True, nullable=False)
    inferred_image_path  = Column(String(256), unique=True)
    request_creation = Column(TIMESTAMP, nullable=False)
    answer_time = Column(TIMESTAMP)
    status_id = Column(Integer, ForeignKey('Status.id'), nullable=False)
    confidence_level = Column(Float)
    pallet_type_id = Column(Integer, ForeignKey('PalletType.id'))

    station = relationship('Station')
    status = relationship('Status')
    pallet_type = relationship('PalletType')

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
            'pallet_type': self.pallet_type.name if self.pallet_type else None
        }

class LogEntry(Base):
    __tablename__ = 'LogEntry'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    timestamp = Column(DateTime)
    detections = Column(JSON)
    initial_image = Column(String(255))
    message = Column(String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'category':self.category,
            'timestamp':self.timestamp,
            'detections':self.detections,
            'initial_image':self.initial_image,
            'message':self.message
        }