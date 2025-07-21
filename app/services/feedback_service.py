from app.ai.openai_client import openai

def generate_candidate_feedback(job_description: str, candidate_cv: str) -> str:

    try:
        prompt = f"""
        Você é um consultor de RH especializado em fornecer feedback construtivo e respeitoso para candidatos.
        
        Analise o perfil do candidato em relação à vaga e forneça um feedback que seja:
        - Construtivo e encorajador
        - Específico sobre áreas de desenvolvimento
        - Respeitoso e profissional
        - Focado no crescimento profissional
        
        DESCRIÇÃO DA VAGA:
        {job_description}
        
        PERFIL DO CANDIDATO:
        {candidate_cv}
        
        Forneça um feedback estruturado seguindo este formato:
        
        **PONTOS FORTES IDENTIFICADOS:**
        [Liste as qualificações e experiências positivas do candidato]
        
        **OPORTUNIDADES DE DESENVOLVIMENTO:**
        [Identifique áreas específicas onde o candidato pode se desenvolver para se alinhar melhor com este tipo de vaga]
        
        **SUGESTÕES DE CRESCIMENTO:**
        [Forneça recomendações práticas e específicas para o desenvolvimento profissional]
        
        **MENSAGEM FINAL:**
        [Uma mensagem encorajadora sobre o potencial do candidato e próximos passos]
        
        Mantenha um tom profissional, respeitoso e construtivo. O objetivo é ajudar o candidato a crescer profissionalmente.
        """
        
        resposta = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um consultor de RH especializado em feedback construtivo para candidatos."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1200
        )
        
        return resposta.choices[0].message.content.strip()
        
    except Exception as erro:
        raise Exception(f"Erro ao gerar feedback: {str(erro)}")