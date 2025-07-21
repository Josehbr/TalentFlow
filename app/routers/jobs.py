from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Candidato, Vaga, Candidatura
from app.services.ranking_service import rank_candidates_for_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/health")
def health_check():

    return {"status": "healthy", "message": "API funcionando corretamente"}

@router.get("/")
def list_jobs(db: Session = Depends(get_db)):

    try:
        vagas = db.query(Vaga).all()
        
        vagas_list = []
        for vaga in vagas:
            # Contar candidatos para esta vaga
            total_candidatos = db.query(Candidatura).filter(Candidatura.vaga_id == vaga.id).count()
            
            vaga_data = {
                "id": vaga.id,
                "titulo": vaga.titulo,
                "descricao": vaga.descricao,
                "descricao_resumida": vaga.descricao[:200] + "..." if len(vaga.descricao) > 200 else vaga.descricao,
                "descricao_estruturada": vaga.descricao_estruturada,
                "tem_descricao_estruturada": bool(vaga.descricao_estruturada),
                "total_candidatos": total_candidatos
            }
            vagas_list.append(vaga_data)
        
        return {
            "vagas": vagas_list,
            "total_vagas": len(vagas_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar vagas: {str(e)}"
        )

@router.get("/{job_id}/candidates")
def list_job_candidates(job_id: int, db: Session = Depends(get_db)):

    try:
        vaga = db.query(Vaga).filter(Vaga.id == job_id).first()
        if not vaga:
            raise HTTPException(
                status_code=404,
                detail=f"Vaga com ID {job_id} não encontrada"
            )

        candidaturas = db.query(Candidatura).filter(Candidatura.vaga_id == job_id).all()
        
        candidatos_list = []
        for candidatura in candidaturas:
            candidato = candidatura.candidato
            candidato_data = {
                "id": candidato.id,
                "nome": candidato.nome,
                "email": candidato.email,
                "vaga_id": candidatura.vaga_id,
                "vaga_titulo": vaga.titulo,
                "dados_perfil": candidato.dados_perfil,
                "status_candidatura": candidatura.status
            }
            candidatos_list.append(candidato_data)
        
        return {
            "vaga": {
                "id": vaga.id,
                "titulo": vaga.titulo,
                "descricao": vaga.descricao
            },
            "candidatos": candidatos_list,
            "total_candidatos": len(candidatos_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar candidatos da vaga: {str(e)}"
        )

@router.get("/{job_id}/rank")
def get_job_candidates_ranking(
    job_id: int,
    top_k: int = 10,
    db: Session = Depends(get_db)
):
    try:
        resultado = rank_candidates_for_job(job_id=job_id, db=db, top_k=top_k)
        return resultado
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")