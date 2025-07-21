from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import json
from app.db.database import get_db
from app.db.models import Candidato, Vaga, Candidatura
from app.ai.openai_client import get_embedding
from app.ai.faiss_manager import load_index, save_index, add_to_index

router = APIRouter(prefix="/candidates", tags=["candidates"])

class FeedbackRequest(BaseModel):
    job_description: str

class CandidateUploadResponse(BaseModel):
    message: str
    job_id: int
    job_title: str
    total_candidatos_arquivo: int
    candidatos_processados: int
    candidatos_adicionados: List[Dict]

def gerar_curriculo_texto(dados_perfil: dict) -> str:

    curriculo_partes = []
    
    if 'name' in dados_perfil:
        curriculo_partes.append(f"Nome: {dados_perfil['name']}")
    
    if 'email' in dados_perfil:
        curriculo_partes.append(f"Email: {dados_perfil['email']}")

    if 'experience' in dados_perfil:
        curriculo_partes.append("\nExperiência Profissional:")
        for exp in dados_perfil['experience']:
            curriculo_partes.append(f"- {exp.get('position', 'Posição não informada')} na {exp.get('company', 'Empresa não informada')}")
            if 'duration' in exp:
                curriculo_partes.append(f"  Duração: {exp['duration']}")
            if 'description' in exp:
                curriculo_partes.append(f"  Descrição: {exp['description']}")

    if 'skills' in dados_perfil:
        curriculo_partes.append(f"\nHabilidades: {', '.join(dados_perfil['skills'])}")

    if 'education' in dados_perfil:
        curriculo_partes.append("\nEducação:")
        for edu in dados_perfil['education']:
            curriculo_partes.append(f"- {edu.get('degree', 'Curso não informado')} em {edu.get('field', 'Área não informada')}")
            if 'institution' in edu:
                curriculo_partes.append(f"  Instituição: {edu['institution']}")
    
    return "\n".join(curriculo_partes)

def processar_candidatos(dados_candidatos: List[Dict], job_id: int, db_session) -> List[Dict]:

    candidatos_processados = []
    
    for dados_candidato in dados_candidatos:
        try:
            candidato_existente = db_session.query(Candidato).filter(
                Candidato.email == dados_candidato['email']
            ).first()
            
            if candidato_existente:
                candidatura_existente = db_session.query(Candidatura).filter(
                    Candidatura.candidato_id == candidato_existente.id,
                    Candidatura.vaga_id == job_id
                ).first()
                
                if candidatura_existente:
                    continue 

                candidatura = Candidatura(
                    vaga_id=job_id,
                    candidato_id=candidato_existente.id,
                    status='pendente'
                )
                db_session.add(candidatura)
                db_session.commit()
                
                candidatos_processados.append({
                    'id': candidato_existente.id,
                    'nome': candidato_existente.nome,
                    'email': candidato_existente.email,
                    'job_id': job_id,
                    'status': 'candidatura_criada'
                })
                continue

            curriculo_texto = gerar_curriculo_texto(dados_candidato)

            candidato = Candidato(
                nome=dados_candidato['name'],
                email=dados_candidato['email'],
                curriculo_texto=curriculo_texto,
                dados_perfil=dados_candidato
            )

            db_session.add(candidato)
            db_session.commit()
            db_session.refresh(candidato)

            candidatura = Candidatura(
                vaga_id=job_id,
                candidato_id=candidato.id,
                status='pendente'
            )
            db_session.add(candidatura)
            db_session.commit()

            candidatos_processados.append({
                'id': candidato.id,
                'nome': candidato.nome,
                'email': candidato.email,
                'job_id': job_id,
                'status': 'novo_candidato'
            })
            
        except Exception as erro:
            db_session.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao processar candidato {dados_candidato.get('name', 'Desconhecido')}: {str(erro)}"
            )
    
    return candidatos_processados

def atualizar_indice_faiss(candidatos_processados: List[Dict], db_session):
    if not candidatos_processados:
        return
    
    try:
        indice = load_index("data/faiss_index.bin")
        
        for candidato_data in candidatos_processados:
            if candidato_data['status'] == 'novo_candidato':
                candidato = db_session.query(Candidato).filter(
                    Candidato.id == candidato_data['id']
                ).first()
                
                if candidato and candidato.curriculo_texto:
                    embedding = get_embedding(candidato.curriculo_texto)
                    add_to_index(indice, [embedding], [candidato.id])

        save_index(indice, "data/faiss_index.bin")
        
    except Exception as erro:
        print(f"Erro ao atualizar índice FAISS: {erro}")

@router.post("/upload/{job_id}", response_model=CandidateUploadResponse)
def upload_candidates_to_job(
    job_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:
        vaga = db.query(Vaga).filter(Vaga.id == job_id).first()
        if not vaga:
            raise HTTPException(
                status_code=404, 
                detail=f"Vaga com ID {job_id} não encontrada"
            )
        
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
        
        candidatos_processados = processar_candidatos(candidatos_dados, job_id, db)

        atualizar_indice_faiss(candidatos_processados, db)
        
        return CandidateUploadResponse(
            message="Candidatos processados com sucesso",
            job_id=job_id,
            job_title=vaga.titulo,
            total_candidatos_arquivo=len(candidatos_dados),
            candidatos_processados=len(candidatos_processados),
            candidatos_adicionados=candidatos_processados
        )
        
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

@router.post("/upload")
def upload_candidates_legacy(
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

        if 'job' not in dados or 'candidates' not in dados:
            raise HTTPException(
                status_code=400, 
                detail="Arquivo deve conter 'job' e 'candidates'"
            )

        job_data = dados['job']
        vaga_existente = db.query(Vaga).filter(
            Vaga.titulo == job_data['title']
        ).first()
        
        if not vaga_existente:
            vaga = Vaga(
                titulo=job_data['title'],
                descricao=job_data['description'],
                descricao_estruturada=job_data.get('structured_description', {})
            )
            db.add(vaga)
            db.commit()
            db.refresh(vaga)
            job_id = vaga.id
        else:
            job_id = vaga_existente.id

        candidatos_dados = dados['candidates']
        candidatos_processados = processar_candidatos(candidatos_dados, job_id, db)

        atualizar_indice_faiss(candidatos_processados, db)
        
        return {
            "message": "Candidatos processados com sucesso (modo legado)",
            "total_candidatos_arquivo": len(candidatos_dados),
            "candidatos_processados": len(candidatos_processados),
            "candidatos_adicionados": candidatos_processados
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/{candidate_id}/feedback")
def generate_feedback(
    candidate_id: int,
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):

    try:

        candidato = db.query(Candidato).filter(Candidato.id == candidate_id).first()
        
        if not candidato:
            raise HTTPException(
                status_code=404, 
                detail="Candidato não encontrado"
            )
        

        from app.services.feedback_service import generate_candidate_feedback

        # Gera o feedback
        feedback = generate_candidate_feedback(
            candidato.curriculo_texto,
            request.job_description
        )
        
        return {
            "candidate_id": candidato.id,
            "candidate_name": candidato.nome,
            "candidate_email": candidato.email,
            "feedback": feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno: {str(e)}"
        )