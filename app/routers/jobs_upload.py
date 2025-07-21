from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import json
from app.db.database import get_db
from app.db.models import Vaga

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobUploadResponse(BaseModel):
    message: str
    total_jobs_arquivo: int
    jobs_processados: int
    jobs_adicionados: List[Dict]

def processar_vagas(dados_vagas: List[Dict], db_session) -> List[Dict]:

    vagas_processadas = []
    
    for dados_vaga in dados_vagas:
        try:

            vaga_existente = db_session.query(Vaga).filter(
                Vaga.titulo == dados_vaga['title']
            ).first()
            
            if vaga_existente:
                continue  

            vaga = Vaga(
                titulo=dados_vaga['title'],
                descricao=dados_vaga['description'],
                descricao_estruturada=dados_vaga.get('structured_description', {})
            )
            
            # Salva no banco de dados
            db_session.add(vaga)
            db_session.commit()
            db_session.refresh(vaga)
            
            # Adiciona aos dados processados
            vagas_processadas.append({
                'id': vaga.id,
                'titulo': vaga.titulo,
                'descricao': vaga.descricao[:100] + "..." if len(vaga.descricao) > 100 else vaga.descricao
            })
            
        except Exception as erro:
            db_session.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao processar vaga {dados_vaga.get('title', 'Desconhecida')}: {str(erro)}"
            )
    
    return vagas_processadas

@router.post("/upload", response_model=JobUploadResponse)
def upload_jobs(
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
        
        if 'jobs' not in dados:
            raise HTTPException(
                status_code=400, 
                detail="Arquivo deve conter um array 'jobs'"
            )
        
        vagas_dados = dados['jobs']
        
        if not isinstance(vagas_dados, list):
            raise HTTPException(
                status_code=400, 
                detail="'jobs' deve ser um array"
            )
        
        # Processa vagas
        vagas_processadas = processar_vagas(vagas_dados, db)
        
        return JobUploadResponse(
            message="Vagas processadas com sucesso",
            total_jobs_arquivo=len(vagas_dados),
            jobs_processados=len(vagas_processadas),
            jobs_adicionados=vagas_processadas
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

@router.get("/")
def list_jobs(db: Session = Depends(get_db)):

    try:
        vagas = db.query(Vaga).all()
        
        return {
            "total_vagas": len(vagas),
            "vagas": [
                {
                    "id": vaga.id,
                    "titulo": vaga.titulo,
                    "descricao_resumida": vaga.descricao[:150] + "..." if len(vaga.descricao) > 150 else vaga.descricao,
                    "tem_descricao_estruturada": bool(vaga.descricao_estruturada)
                }
                for vaga in vagas
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno: {str(e)}"
        )