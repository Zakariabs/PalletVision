from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)

class InferenceRequest(Base):
    __tablename__ = 'InferenceRequest'
    request_id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('Station.id'), nullable=False)
    initial_image_id = Column(Integer, ForeignKey('Image.id'), nullable=False)
    inferred_image_id = Column(Integer, ForeignKey('Image.id'))
    request_creation = Column(TIMESTAMP, nullable=False)
    answer_time = Column(TIMESTAMP, nullable=False)
    status_id = Column(Integer, ForeignKey('Status.id'), nullable=False)
    confidence_level = Column(Float)
    pallet_type = Column(Integer, ForeignKey('PalletType.id'))

    station = relationship('Station')
    initial_image = relationship('Image', foreign_keys=[initial_image_id])
    inferred_image = relationship('Image', foreign_keys=[inferred_image_id])
    status = relationship('Status')
    pallet_type_rel = relationship('PalletType')
