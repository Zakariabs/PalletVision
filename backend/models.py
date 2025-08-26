from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float, DateTime, JSON, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Station(Base):
    __tablename__ = 'Station'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    location = Column(String(256))
    status = Column(String(50), default='Offline')  # Simplified: Ready, Processing, Offline
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'status': self.status
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

class InferenceRequest(Base):
    __tablename__ = 'InferenceRequest'
    
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey('Station.id'), nullable=False)
    initial_image_path = Column(Text, nullable=False)
    inferred_image_path = Column(Text)
    request_creation = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    answer_time = Column(TIMESTAMP(timezone=True))
    status = Column(String(50), default='Processing')  # Simplified: Done, Processing, Error
    confidence_level = Column(Float)
    pallet_type_id = Column(Integer, ForeignKey('PalletType.id'))
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    station = relationship('Station')
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
            'status': self.status,
            'confidence_level': self.confidence_level,
            'pallet_type': self.pallet_type.name if self.pallet_type else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

class LogEntry(Base):
    __tablename__ = 'LogEntry'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    detections = Column(JSON, nullable=True)
    initial_image = Column(Text, nullable=True)
    message = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'detections': self.detections,
            'initial_image': self.initial_image,
            'message': self.message
        }