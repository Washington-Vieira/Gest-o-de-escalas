from datetime import datetime, date
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from typing import Optional
from pydantic import Field

Base = declarative_base()

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    funcionarios = relationship("Funcionario", back_populates="empresa")

class Funcionario(Base):
    __tablename__ = "funcionarios"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    funcao = Column(String)
    familia_letras = Column(String)
    horario_turno = Column(String)
    data_inicio = Column(Date)
    turno = Column(String)
    ferias_atual = Column(JSON, nullable=True)
    historico_ferias = Column(JSON, default=list)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    empresa = relationship("Empresa", back_populates="funcionarios")

    def registrar_ferias(self, data_inicio, data_fim):
        if isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if isinstance(data_fim, str):
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        self.ferias_atual = {'inicio': data_inicio, 'fim': data_fim}
        self.historico_ferias.append(self.ferias_atual)

    def encerrar_ferias(self):
        if self.ferias_atual:
            self.ferias_atual = None

    def em_ferias(self):
        if self.ferias_atual is None:
            return False
        hoje = datetime.now().date()
        return self.ferias_atual['inicio'] <= hoje <= self.ferias_atual['fim']

    def to_dict(self):
        return {
            'nome': self.nome,
            'funcao': self.funcao,
            'familia_letras': self.familia_letras,
            'horario_turno': self.horario_turno,
            'data_inicio': self.data_inicio.strftime('%Y-%m-%d') if isinstance(self.data_inicio, date) else self.data_inicio,
            'turno': self.turno,
            'ferias_atual': self.ferias_atual_to_dict(),
            'historico_ferias': self.historico_ferias_to_dict()
        }

    def ferias_atual_to_dict(self):
        if self.ferias_atual:
            return {
                'inicio': self.ferias_atual['inicio'].strftime('%Y-%m-%d'),
                'fim': self.ferias_atual['fim'].strftime('%Y-%m-%d')
            }
        return None

    def historico_ferias_to_dict(self):
        return [
            {
                'inicio': ferias['inicio'].strftime('%Y-%m-%d'),
                'fim': ferias['fim'].strftime('%Y-%m-%d')
            }
            for ferias in self.historico_ferias
        ]
