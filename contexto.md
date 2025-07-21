# Contexto da Aplicação - Sistema de Seleção Inteligente de Candidatos

## Visão Geral

Sistema inteligente de seleção de candidatos desenvolvido em Python 3.12 com FastAPI, que utiliza IA (OpenAI GPT-4o-mini) para análise e ranking de candidatos, busca vetorial com FAISS para similaridade semântica, e interface web com Streamlit.

## Arquitetura e Tecnologias

### Backend (FastAPI)
- **Python 3.12** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **Pydantic** - Validação de dados e serialização
- **MySQL** - Banco de dados relacional
- **Docker Compose** - Orquestração do MySQL

### Inteligência Artificial
- **OpenAI GPT-4o-mini** - Geração de justificativas e feedback
- **text-embedding-3-small** - Geração de embeddings para busca semântica
- **FAISS** - Biblioteca para busca vetorial eficiente

### Frontend
- **Streamlit** - Interface web interativa e responsiva
- **Pandas** - Manipulação de dados para visualização

## Estrutura do Projeto

```
TalentFlow/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Aplicação FastAPI principal
│   ├── config.py                  # Configurações e variáveis de ambiente
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py            # Configuração SQLAlchemy
│   │   └── models.py              # Modelos de dados (Vaga, Candidato, Candidatura)
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_client.py       # Cliente OpenAI para embeddings e justificativas
│   │   └── faiss_manager.py       # Gerenciamento do índice FAISS
│   ├── services/
│   │   ├── __init__.py
│   │   └── ranking_service.py     # Lógica de ranking e feedback
│   └── routers/
│       ├── __init__.py
│       ├── jobs.py                # Endpoints de ranking e health check
│       ├── candidates.py          # Endpoints legados de candidatos
│       ├── jobs_upload.py         # Novos endpoints para upload de vagas
│       └── candidates_upload.py   # Novos endpoints para upload de candidatos
├── frontend/
│   ├── app.py                     # Aplicação Streamlit
│   ├── requirements.txt           # Dependências do frontend
│   └── README.md                  # Documentação do frontend
├── data/
│   ├── faiss_index.bin           # Índice FAISS persistido
│   ├── sample_jobs.json          # Exemplo de arquivo de vagas
│   ├── sample_candidates_frontend.json # Exemplo de candidatos
│   └── [outros arquivos de dados]
├── docker-compose.yml            # Configuração MySQL
├── requirements.txt              # Dependências do backend
└── seed.py                       # Script de inicialização de dados
```

## Componentes Principais

### 1. Configuração (`app/config.py`)
Gerencia configurações usando Pydantic BaseSettings:
- Credenciais MySQL (host, porta, usuário, senha, database)
- Chave da API OpenAI
- Modelos de IA (embedding e justificação)
- Configurações do ambiente

### 2. Modelos de Dados (`app/db/models.py`)
**Vaga (Vagas)**:
- `id`, `titulo`, `descricao`, `descricao_estruturada`
- Relacionamento com candidaturas

**Candidato (Candidatos)**:
- `id`, `nome`, `email`, `dados_perfil`, `curriculo_texto`
- Relacionamento com candidaturas

**Candidatura (Candidaturas)**:
- `id`, `vaga_id`, `candidato_id`, `status`, `justificativa`
- Tabela de relacionamento entre vagas e candidatos

### 3. Cliente OpenAI (`app/ai/openai_client.py`)
- `get_embedding(texto)` - Gera embeddings usando text-embedding-3-small
- `generate_justification(descricao_vaga, cv_candidato)` - Gera justificativas com GPT-4o-mini
- `generate_candidate_feedback(cv_candidato, descricao_vaga)` - Gera feedback personalizado

### 4. Gerenciador FAISS (`app/ai/faiss_manager.py`)
- `load_index(caminho)` - Carrega índice do disco
- `save_index(indice, caminho)` - Salva índice no disco
- `add_to_index(indice, embeddings, ids)` - Adiciona vetores ao índice
- `search_similar(indice, query_embedding, k)` - Busca candidatos similares

### 5. Serviço de Ranking (`app/services/ranking_service.py`)
- Implementa lógica principal de ranking
- Integra busca vetorial com geração de justificativas
- Gera feedback personalizado para candidatos

## Endpoints da API

### Gerenciamento de Vagas
- `POST /jobs/upload` - Upload de arquivo JSON com vagas
- `GET /jobs/` - Lista todas as vagas cadastradas
- `GET /jobs/health` - Health check da API

### Gerenciamento de Candidatos
- `POST /candidates/upload/{job_id}` - Upload de candidatos para vaga específica
- `POST /candidates/upload` - Upload legado (vaga + candidatos juntos)
- `POST /candidates/{candidate_id}/feedback` - Gera feedback personalizado

### Ranking e Análise
- `GET /jobs/{job_id}/rank?top_k={n}` - Gera ranking de candidatos para uma vaga

## Fluxo de Dados Atualizado

### 1. Upload de Vagas
1. Upload de arquivo JSON com array de vagas
2. Validação da estrutura do arquivo
3. Processamento e salvamento no banco de dados
4. Prevenção de duplicatas por título
5. Retorno de vagas processadas

### 2. Upload de Candidatos
1. Seleção de vaga existente
2. Upload de arquivo JSON com array de candidatos
3. Processamento de dados do candidato
4. Geração de texto do currículo
5. Criação de embedding com OpenAI
6. Salvamento no banco de dados
7. Criação de candidatura (vínculo vaga-candidato)
8. Atualização do índice FAISS
9. Retorno de candidatos processados

### 3. Geração de Ranking
1. Recebimento do ID da vaga e parâmetro top_k
2. Recuperação da descrição da vaga do banco
3. Geração de embedding da descrição da vaga
4. Busca vetorial no FAISS por candidatos similares
5. Para cada candidato encontrado:
   - Geração de justificativa com GPT-4o-mini
   - Compilação de dados do perfil
6. Ordenação e retorno do ranking

### 4. Geração de Feedback
1. Recebimento do ID do candidato e descrição da vaga
2. Recuperação dos dados do candidato
3. Geração de feedback personalizado com GPT-4o-mini
4. Retorno do feedback estruturado

## Interface Frontend (Streamlit)

### Páginas Principais

**🏠 Home**
- Status da API em tempo real
- Informações sobre funcionalidades
- Guia do novo fluxo de trabalho

**🎯 Gerenciar Vagas**
- Upload de arquivos JSON com vagas
- Visualização de vagas cadastradas
- Métricas de processamento

**👥 Gerenciar Candidatos**
- Seleção de vaga existente
- Upload de candidatos para vaga específica
- Visualização de candidatos processados

**🏆 Ranking**
- Seleção de vaga e número de candidatos
- Geração de ranking inteligente
- Visualização de justificativas detalhadas

**💬 Feedback**
- Seleção de candidato
- Geração de feedback personalizado
- Visualização formatada do feedback

## Formatos de Arquivo

### Arquivo de Vagas (`jobs.json`)
```json
{
  "jobs": [
    {
      "title": "Desenvolvedor Frontend React",
      "description": "Descrição detalhada da vaga...",
      "structured_description": {
        "required_skills": ["React", "TypeScript"],
        "preferred_skills": ["Next.js", "Jest"],
        "experience_level": "Pleno",
        "years_required": 2
      }
    }
  ]
}
```

### Arquivo de Candidatos (`candidates.json`)
```json
{
  "candidates": [
    {
      "name": "Ana Costa",
      "email": "ana.costa@exemplo.com",
      "experience": [
        {
          "position": "Desenvolvedora Frontend",
          "company": "TechCorp",
          "duration": "2 anos",
          "description": "Desenvolvimento com React e TypeScript"
        }
      ],
      "skills": ["React", "TypeScript", "JavaScript"],
      "education": [
        {
          "degree": "Bacharelado",
          "field": "Ciência da Computação",
          "institution": "UFMG"
        }
      ]
    }
  ]
}
```

## Configuração e Execução

### Variáveis de Ambiente
```env
MYSQL_HOST=localhost
MYSQL_PORT=3302
MYSQL_USER=talentflow_user
MYSQL_PASSWORD=talentflow_password
MYSQL_DATABASE=talentflow_db
OPENAI_API_KEY=sua_chave_openai
EMBEDDING_MODEL=text-embedding-3-small
JUSTIFICATION_MODEL=gpt-4o-mini
```

### Execução dos Serviços

**1. Banco de Dados:**
```bash
docker-compose up -d
```

**2. Backend API:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**3. Frontend:**
```bash
cd frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### URLs de Acesso
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501

## Funcionalidades Implementadas

### ✅ Core Features
- [x] Upload separado de vagas e candidatos
- [x] Busca vetorial com FAISS
- [x] Ranking inteligente com IA
- [x] Geração de justificativas
- [x] Feedback personalizado para candidatos
- [x] Interface web completa
- [x] Prevenção de duplicatas
- [x] Compatibilidade com sistema legado

### ✅ Melhorias Técnicas
- [x] Arquitetura modular e escalável
- [x] Validação robusta de dados
- [x] Tratamento de erros abrangente
- [x] Documentação automática da API
- [x] Configuração via variáveis de ambiente
- [x] Containerização do banco de dados

## Próximas Funcionalidades (Roadmap)

### 🔄 Em Desenvolvimento
- [ ] Sistema de autenticação e autorização
- [ ] CRUD completo para vagas e candidatos
- [ ] Sistema de notificações
- [ ] Métricas e analytics
- [ ] Testes automatizados abrangentes

### 🚀 Futuras Melhorias
- [ ] Deploy em produção
- [ ] Cache Redis para performance
- [ ] Processamento assíncrono
- [ ] API de webhooks
- [ ] Dashboard executivo
- [ ] Integração com sistemas de RH

## Vantagens da Arquitetura Atual

### 🎯 Flexibilidade
- Upload independente de vagas e candidatos
- Reutilização de vagas para múltiplos processos
- Suporte a diferentes formatos de dados

### ⚡ Performance
- Busca vetorial otimizada com FAISS
- Índice persistente em disco
- Processamento eficiente de embeddings

### 🔧 Manutenibilidade
- Código modular e bem estruturado
- Separação clara de responsabilidades
- Documentação abrangente

### 🚀 Escalabilidade
- Arquitetura preparada para crescimento
- Suporte a grandes volumes de dados
- Processamento distribuído futuro

## Status Atual

**✅ SISTEMA TOTALMENTE FUNCIONAL**

Todas as funcionalidades principais estão implementadas e testadas:
- Backend API completo
- Frontend interativo
- Integração com IA
- Busca vetorial
- Banco de dados configurado
- Documentação atualizada

O sistema está pronto para uso em ambiente de desenvolvimento e pode ser facilmente adaptado para produção.