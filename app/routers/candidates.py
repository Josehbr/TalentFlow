from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import json
from app.db.database import get_db
from app.db.models import Candidato, Vaga, Candidatura
from app.ai.openai_client import get_embedding
from app.ai.faiss_manager import load_index, save_index, add_to_index
from app.services.feedback_service import generate_candidate_feedback

router = APIRouter(prefix="/candidates", tags=["candidates"])

class FeedbackRequest(BaseModel):
    job_description: str

def gerar_curriculo_texto(dados_perfil: Dict) -> str:

    texto_curriculo = []
    

    if 'summary' in dados_perfil:
        texto_curriculo.append(f"Resumo: {dados_perfil['summary']}")
    

    if 'experience' in dados_perfil:
        texto_curriculo.append("\nExperiências:")
        for exp in dados_perfil['experience']:
            texto_exp = f"- {exp.get('title', '')} na {exp.get('company', '')} ({exp.get('period', '')})"
            if 'description' in exp:
                texto_exp += f": {exp['description']}"
            texto_curriculo.append(texto_exp)
    
    if 'skills' in dados_perfil:
        habilidades = ", ".join(dados_perfil['skills'])
        texto_curriculo.append(f"\nHabilidades: {habilidades}")
    
    return "\n".join(texto_curriculo)

def processar_candidatos(dados_candidatos: List[Dict], db_session) -> List[Dict]:

    candidatos_processados = []
    
    for dados_candidato in dados_candidatos:
        try:

            candidato_existente = db_session.query(Candidato).filter(
                Candidato.email == dados_candidato['email']
            ).first()
            
            if candidato_existente:
                continue 

            curriculo_texto = gerar_curriculo_texto(dados_candidato['profile_data'])

            embedding = get_embedding(curriculo_texto)

            candidato = Candidato(
                nome=dados_candidato['name'],
                email=dados_candidato['email'],
                dados_perfil=dados_candidato['profile_data'],
                curriculo_texto=curriculo_texto
            )

            db_session.add(candidato)
            db_session.commit()
            db_session.refresh(candidato)

            candidatos_processados.append({
                'id': candidato.id,
                'embedding': embedding,
                'nome': candidato.nome
            })
            
        except Exception as erro:
            db_session.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao processar candidato {dados_candidato.get('name', 'Desconhecido')}: {str(erro)}"
            )
    
    return candidatos_processados

def adicionar_ao_indice_faiss(candidatos_processados: List[Dict]):

    if not candidatos_processados:
        return
    
    indice = load_index("data/faiss_index.bin")

    vetores = [candidato['embedding'] for candidato in candidatos_processados]
    ids = [candidato['id'] for candidato in candidatos_processados]

    add_to_index(indice, vetores, ids)

    save_index(indice, "data/faiss_index.bin")

@router.post("/upload")
def upload_candidates(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    try:

        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400, 
                detail="Arquivo deve ser do tipo JSON"
            )
        
        conteudo = file.file.read()
        dados = json.loads(conteudo.decode('utf-8'))
        
        if 'candidates' not in dados:
            raise HTTPException(
                status_code=400, 
                detail="Arquivo deve conter um array 'candidates'"
            )
        
        candidatos_dados = dados['candidates']
        
        if not isinstance(candidatos_dados, list):
            raise HTTPException(
                status_code=400, 
                detail="'candidates' deve ser um array"
            )

        candidatos_processados = processar_candidatos(candidatos_dados, db)

        adicionar_ao_indice_faiss(candidatos_processados)
        
        return {
            "message": "Candidatos processados com sucesso",
            "total_candidatos_arquivo": len(candidatos_dados),
            "candidatos_processados": len(candidatos_processados),
            "candidatos_adicionados": [
                {
                    "id": candidato['id'],
                    "nome": candidato['nome']
                } for candidato in candidatos_processados
            ]
        }
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Arquivo JSON inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/")
def list_all_candidates(db: Session = Depends(get_db)):

    try:
        candidatos = db.query(Candidato).all()

        candidatos_list = []
        for candidato in candidatos:

            candidaturas = db.query(Candidatura).filter(Candidatura.candidato_id == candidato.id).all()

            vaga_info = None
            if candidaturas:
                primeira_candidatura = candidaturas[0]
                vaga_info = {
                    "vaga_id": primeira_candidatura.vaga_id,
                    "vaga_titulo": primeira_candidatura.vaga.titulo if primeira_candidatura.vaga else None
                }

            candidato_data = {
                "id": candidato.id,
                "nome": candidato.nome,
                "email": candidato.email,
                "dados_perfil": candidato.dados_perfil,
                "total_candidaturas": len(candidaturas)
            }

            if vaga_info:
                candidato_data.update(vaga_info)

            candidatos_list.append(candidato_data)

        return {
            "candidatos": candidatos_list,
            "total_candidatos": len(candidatos_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar candidatos: {str(e)}"
        )

@router.get("/{candidate_id}")
def get_candidate_details(candidate_id: int, db: Session = Depends(get_db)):

    try:
        candidato = db.query(Candidato).filter(Candidato.id == candidate_id).first()

        if not candidato:
            raise HTTPException(
                status_code=404,
                detail=f"Candidato com ID {candidate_id} não encontrado"
            )

        candidaturas = db.query(Candidatura).filter(Candidatura.candidato_id == candidate_id).all()
        candidaturas_info = []
        for candidatura in candidaturas:
            candidaturas_info.append({
                "vaga_id": candidatura.vaga_id,
                "vaga_titulo": candidatura.vaga.titulo if candidatura.vaga else None,
                "status": candidatura.status
            })

        return {
            "id": candidato.id,
            "nome": candidato.nome,
            "email": candidato.email,
            "dados_perfil": candidato.dados_perfil,
            "curriculo_texto": candidato.curriculo_texto,
            "candidaturas": candidaturas_info
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar candidato: {str(e)}"
        )