from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Vaga, Candidato, Candidatura
from app.ai.faiss_manager import load_index, search_index
from app.ai.openai_client import get_embedding, generate_justification

CAMINHO_INDICE_FAISS = "data/faiss_index.bin"

def _gerar_descricao_vaga_texto(vaga: Vaga) -> str:

    texto_vaga = [f"Título: {vaga.titulo}"]
    
    if vaga.descricao:
        texto_vaga.append(f"Descrição: {vaga.descricao}")
    
    if vaga.descricao_estruturada:
        estrutura = vaga.descricao_estruturada
        
        if 'summary' in estrutura:
            texto_vaga.append(f"Resumo: {estrutura['summary']}")
        
        if 'responsibilities' in estrutura:
            responsabilidades = "; ".join(estrutura['responsibilities'])
            texto_vaga.append(f"Responsabilidades: {responsabilidades}")
        
        if 'technical_requirements' in estrutura:
            requisitos = "; ".join(estrutura['technical_requirements'])
            texto_vaga.append(f"Requisitos Técnicos: {requisitos}")
        
        if 'cultural_fit' in estrutura:
            cultura = "; ".join(estrutura['cultural_fit'])
            texto_vaga.append(f"Perfil Cultural: {cultura}")
    
    return "\n".join(texto_vaga)

def rank_candidates_for_job(job_id: int, db: Session, top_k: int = 10) -> Dict[str, Any]:
    try:
        vaga = db.query(Vaga).filter(Vaga.id == job_id).first()
        if not vaga:
            raise ValueError(f"Vaga com ID {job_id} não encontrada")

        indice_faiss = load_index(CAMINHO_INDICE_FAISS)
        descricao_vaga_texto = _gerar_descricao_vaga_texto(vaga)
        embedding_vaga = get_embedding(descricao_vaga_texto)

        candidatos_ids = search_index(indice_faiss, embedding_vaga, top_k*5) 

        candidatos_ids_filtrados = []
        for candidato_id in candidatos_ids:
            vinculo = db.query(Candidatura).filter(
                Candidatura.vaga_id == job_id,
                Candidatura.candidato_id == candidato_id
            ).first()
            if vinculo:
                candidatos_ids_filtrados.append(candidato_id)
            if len(candidatos_ids_filtrados) >= top_k:
                break

        candidatos_ranqueados = []
        for posicao, candidato_id in enumerate(candidatos_ids_filtrados, 1):
            candidato = db.query(Candidato).filter(Candidato.id == candidato_id).first()
            if candidato:
                justificativa = generate_justification(
                    descricao_vaga=descricao_vaga_texto,
                    cv_candidato=candidato.curriculo_texto
                )
                candidato_ranqueado = {
                    "posicao": posicao,
                    "candidato_id": candidato.id,
                    "nome": candidato.nome,
                    "email": candidato.email,
                    "dados_perfil": candidato.dados_perfil,
                    "justificativa": justificativa
                }
                candidatos_ranqueados.append(candidato_ranqueado)

        resposta = {
            "vaga": {
                "id": vaga.id,
                "titulo": vaga.titulo,
                "descricao": vaga.descricao,
                "descricao_estruturada": vaga.descricao_estruturada
            },
            "total_candidatos_encontrados": len(candidatos_ranqueados),
            "candidatos_ranqueados": candidatos_ranqueados,
            "parametros_busca": {
                "top_k_solicitado": top_k,
                "embedding_model": "text-embedding-3-small",
                "justification_model": "gpt-4o-mini"
            }
        }
        return resposta
    except Exception as erro:
        raise Exception(f"Erro ao ranquear candidatos para vaga {job_id}: {str(erro)}")