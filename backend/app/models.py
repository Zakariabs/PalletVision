from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

class StationStatus(Base):
    __tablename__ = 'StationStatus'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))

class Status(Base):
    __tablename__ = 'Status'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)

class PalletType(Base):
    __tablename__ = 'PalletType'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)

class Image(Base):
    __tablename__ = 'Image'
    id = Column(Integer, primary_key=True)
    path = Column(String(256), unique=True, nullable=False)

class Station(Base):
    __tablename__ = 'Station'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    location = Column(String(256))
    station_status_id = Column(Integer, ForeignKey('StationStatus.id'))
    station_status = relationship('StationStatus')

class User(Base):
    __tablename__ = 'users'
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
    initial_image_id = Column(Integer, ForeignKey('Image.id'), nullable=False)
    inferred_image_id = Column(Integer, ForeignKey('Image.id'))
    request_creation = Column(TIMESTAMP, nullable=False)
    answer_time = Column(TIMESTAMP)
    status_id = Column(Integer, ForeignKey('Status.id'), nullable=False)
    confidence_level = Column(Float)
    pallet_type = Column(Integer, ForeignKey('PalletType.id'))

    station = relationship('Station')
    initial_image = relationship('Image', foreign_keys=[initial_image_id])
    inferred_image = relationship('Image', foreign_keys=[inferred_image_id])
    status = relationship('Status')
    pallet_type_rel = relationship('PalletType')

    def to_dict(self):
        """Convert model instance to dictionary excluding SQLAlchemy internals."""
        return {
            'request_id': self.request_id,
            'station_id': self.station_id,
            'initial_image_id': self.initial_image_id,
            'inferred_image_id': self.inferred_image_id,
            'request_creation': self.request_creation.isoformat() if self.request_creation else None,
            'answer_time': self.answer_time.isoformat() if self.answer_time else None,
            'status_id': self.status_id,
            'confidence_level': self.confidence_level,
            'pallet_type': self.pallet_type
        }