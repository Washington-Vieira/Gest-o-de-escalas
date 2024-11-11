from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    funcionarios = relationship("Funcionario", back_populates="empresa", cascade="all, delete-orphan")

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    matricula = Column(String(20), unique=True, nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    empresa = relationship("Empresa", back_populates="funcionarios")
    ferias = relationship("Ferias", back_populates="funcionario", cascade="all, delete-orphan")
    escalas = relationship("Escala", back_populates="funcionario", cascade="all, delete-orphan")

class Ferias(Base):
    __tablename__ = 'ferias'
    id = Column(Integer, primary_key=True)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    funcionario = relationship("Funcionario", back_populates="ferias")

class Escala(Base):
    __tablename__ = 'escalas'
    id = Column(Integer, primary_key=True)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    data = Column(Date, nullable=False)
    turno = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    funcionario = relationship("Funcionario", back_populates="escalas") 