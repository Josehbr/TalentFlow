from typing import List
import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

def get_embedding(texto: str) -> List[float]:

    try:
        resposta = openai.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texto
        )
        return resposta.data[0].embedding
    except Exception as erro:
        raise Exception(f"Erro ao gerar embedding: {str(erro)}")

def generate_justification(descricao_vaga: str, cv_candidato: str) -> str:

    try:
        prompt = f"""
        Analise o seguinte candidato para a vaga descrita e forneça uma justificativa profissional estruturada.

        DESCRIÇÃO DA VAGA:
        {descricao_vaga}

        CV DO CANDIDATO:
        {cv_candidato}

        Por favor, forneça uma análise estruturada com:

        **PONTOS POSITIVOS:**
        - Liste as qualificações, experiências e competências que se alinham com a vaga

        **ÁREAS DE MELHORIA:**
        - Identifique gaps ou áreas onde o candidato poderia se desenvolver para melhor adequação à vaga

        **CONCLUSÃO:**
        - Forneça uma avaliação geral sobre a adequação do candidato à vaga

        Mantenha um tom profissional, construtivo e respeitoso.
        """

        resposta = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em recursos humanos que analisa candidatos de forma profissional e construtiva."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return resposta.choices[0].message.content
        
    except Exception as erro:
        raise Exception(f"Erro ao gerar justificativa: {str(erro)}")