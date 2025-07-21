from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Vaga(Base):
    __tablename__ = 'vagas'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    descricao_estruturada = Column(JSON) 

    candidaturas = relationship('Candidatura', back_populates='vaga')

class Candidato(Base):
    __tablename__ = 'candidatos'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    dados_perfil = Column(JSON)  
    curriculo_texto = Column(Text)  

    candidaturas = relationship('Candidatura', back_populates='candidato')

class Candidatura(Base):
    __tablename__ = 'candidaturas'
    id = Column(Integer, primary_key=True, index=True)
    vaga_id = Column(Integer, ForeignKey('vagas.id'), nullable=False)
    candidato_id = Column(Integer, ForeignKey('candidatos.id'), nullable=False)
    status = Column(String(50), default='pendente')
    justificativa = Column(Text) 

    vaga = relationship('Vaga', back_populates='candidaturas')
    candidato = relationship('Candidato', back_populates='candidaturas')