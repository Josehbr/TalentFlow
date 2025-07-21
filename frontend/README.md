# Frontend TalentFlow

Frontend simples em Streamlit para a aplicação TalentFlow.

## Como executar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o frontend:
```bash
streamlit run app.py
```

3. Acesse: http://localhost:8501

## Funcionalidades

- **Home**: Status da API e informações gerais
- **Upload Candidatos**: Upload de arquivos JSON com candidatos
- **Ranking**: Visualização do ranking de candidatos para vagas
- **Feedback**: Geração de feedback personalizado para candidatos

## Pré-requisitos

- API TalentFlow rodando em http://localhost:8000
- Python 3.8+