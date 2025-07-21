import streamlit as st
import requests
import json
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="TalentFlow - Seleção Inteligente",
    page_icon="",
    layout="wide"
)

# URL da API
API_URL = "http://localhost:8000"

def main():
    st.title("TalentFlow - Seleção Inteligente de Candidatos")
    
    # Sidebar para navegação
    st.sidebar.title("Menu")
    opcao = st.sidebar.selectbox(
        "Escolha uma opção:",
        ["Home", "Gerenciar Vagas", "Gerenciar Candidatos", "Ranking", "Feedback"]
    )
    
    if opcao == "Home":
        home_page()
    elif opcao == "Gerenciar Vagas":
        jobs_page()
    elif opcao == "Gerenciar Candidatos":
        candidates_page()
    elif opcao == "Ranking":
        ranking_page()
    elif opcao == "Feedback":
        feedback_page()

def home_page():
    st.header("Bem-vindo ao TalentFlow!")
    
    # Status da API
    try:
        response = requests.get(f"{API_URL}/jobs/health", timeout=5)
        if response.status_code == 200:
            st.success("API funcionando corretamente!")
        else:
            st.error("API com problemas")
    except:
        st.error("ão foi possível conectar à API")
    
    st.markdown("""
    ### Novo Fluxo de Trabalho:
    
    #### 1. **Gerenciar Vagas**
    - Upload de arquivo JSON com vagas
    - Visualizar vagas cadastradas
    - Cada vaga recebe um ID único
    
    #### 2. **Gerenciar Candidatos**
    - Upload de candidatos para uma vaga específica
    - Vincular candidatos a vagas existentes
    - Visualizar candidatos por vaga
    
    #### 3. **Ranking**
    - Gerar ranking de candidatos para uma vaga
    - Análise inteligente com IA
    
    #### 4. **Feedback**
    - Feedback personalizado para candidatos
    
    ### Vantagens do Novo Sistema:
    - **Flexibilidade**: Gerencie vagas e candidatos separadamente
    - **Reutilização**: Uma vaga pode receber múltiplos uploads de candidatos
    - **Organização**: Melhor controle e visualização dos dados
    - **Escalabilidade**: Suporte a grandes volumes de dados
    """)

def jobs_page():
    st.header("Gerenciamento de Vagas")
    
    tab1, tab2 = st.tabs(["Upload de Vagas", "Vagas Cadastradas"])
    
    with tab1:
        st.subheader("Upload de Vagas")
        
        uploaded_file = st.file_uploader(
            "Escolha um arquivo JSON com vagas",
            type=['json'],
            help="O arquivo deve conter um array 'jobs' com as vagas"
        )
        
        if uploaded_file is not None:
            if st.button("Processar Vagas"):
                try:
                    files = {"file": uploaded_file}
                    response = requests.post(f"{API_URL}/jobs/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Vagas processadas com sucesso!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total no arquivo", result["total_jobs_arquivo"])
                        with col2:
                            st.metric("Processadas", result["jobs_processados"])
                        with col3:
                            st.metric("Adicionadas", len(result["jobs_adicionados"]))
                        
                        if result["jobs_adicionados"]:
                            st.subheader("Vagas Adicionadas:")
                            df = pd.DataFrame(result["jobs_adicionados"])
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Erro: {response.text}")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
    
    with tab2:
        st.subheader("Vagas Cadastradas")
        
        if st.button("Atualizar Lista"):
            try:
                response = requests.get(f"{API_URL}/jobs/")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result["total_vagas"] > 0:
                        st.info(f"Total de vagas: {result['total_vagas']}")
                        
                        for vaga in result["vagas"]:
                            with st.expander(f"{vaga['titulo']} (ID: {vaga['id']})"):
                                st.write("**Descrição:**")
                                st.write(vaga["descricao_resumida"])
                                
                                if vaga["tem_descricao_estruturada"]:
                                    st.success("Possui descrição estruturada")
                                else:
                                    st.warning("Sem descrição estruturada")
                    else:
                        st.info("Nenhuma vaga cadastrada ainda")
                else:
                    st.error(f"Erro ao carregar vagas: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

def candidates_page():
    st.header("Gerenciamento de Candidatos")
    
    # Primeiro, carrega as vagas disponíveis
    try:
        response = requests.get(f"{API_URL}/jobs/")
        if response.status_code == 200:
            jobs_data = response.json()
            if jobs_data["total_vagas"] > 0:
                vagas_options = {f"{vaga['titulo']} (ID: {vaga['id']})": vaga['id'] 
                               for vaga in jobs_data["vagas"]}
                
                st.subheader("Upload de Candidatos para Vaga")
                
                selected_job = st.selectbox(
                    "Selecione a vaga:",
                    options=list(vagas_options.keys())
                )
                
                job_id = vagas_options[selected_job]
                
                uploaded_file = st.file_uploader(
                    "Escolha um arquivo JSON com candidatos",
                    type=['json'],
                    help="O arquivo deve conter um array 'candidates' com os candidatos"
                )
                
                if uploaded_file is not None:
                    if st.button("Processar Candidatos"):
                        try:
                            files = {"file": uploaded_file}
                            response = requests.post(f"{API_URL}/candidates/upload/{job_id}", files=files)
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.success("Candidatos processados com sucesso!")
                                
                                st.info(f"Vaga: {result['job_title']}")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total no arquivo", result["total_candidatos_arquivo"])
                                with col2:
                                    st.metric("Processados", result["candidatos_processados"])
                                with col3:
                                    st.metric("Adicionados", len(result["candidatos_adicionados"]))
                                
                                if result["candidatos_adicionados"]:
                                    st.subheader("Candidatos Adicionados:")
                                    df = pd.DataFrame(result["candidatos_adicionados"])
                                    st.dataframe(df, use_container_width=True)
                            else:
                                st.error(f"Erro: {response.text}")
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")
            else:
                st.warning("⚠️ Nenhuma vaga cadastrada. Cadastre vagas primeiro na aba 'Gerenciar Vagas'.")
        else:
            st.error("Erro ao carregar vagas")
    except Exception as e:
        st.error(f"Erro: {str(e)}")

def ranking_page():
    st.header("🏆 Ranking de Candidatos")

    # Carregar vagas disponíveis
    try:
        response = requests.get(f"{API_URL}/jobs/")
        if response.status_code == 200:
            vagas_data = response.json()
            vagas = vagas_data.get("vagas", [])

            if vagas:
                st.info("💡 Selecione uma vaga para ver o ranking de todos os candidatos cadastrados para ela.")

                # Criar dicionário para mapear título -> ID
                vaga_options = {}
                for vaga in vagas:
                    titulo_completo = f"{vaga['titulo']}"
                    if vaga.get('descricao_resumida'):
                        # Limitar descrição resumida para não ficar muito longo
                        descricao_resumida = vaga['descricao_resumida'][:100]
                        if len(vaga['descricao_resumida']) > 100:
                            descricao_resumida += "..."
                        titulo_completo += f" - {descricao_resumida}"
                    vaga_options[titulo_completo] = vaga['id']

                # Selectbox para escolher a vaga
                vaga_selecionada = st.selectbox(
                    "🎯 Selecione a Vaga:",
                    options=list(vaga_options.keys()),
                    help="Escolha a vaga para a qual deseja ver o ranking de candidatos"
                )

                if vaga_selecionada:
                    job_id = vaga_options[vaga_selecionada]

                    # Mostrar informações da vaga selecionada
                    vaga_info = next((v for v in vagas if v['id'] == job_id), None)
                    if vaga_info:
                        with st.expander("📋 Detalhes da Vaga Selecionada", expanded=False):
                            st.write(f"**ID:** {vaga_info['id']}")
                            st.write(f"**Título:** {vaga_info['titulo']}")
                            if vaga_info.get('descricao_resumida'):
                                st.write(f"**Descrição:** {vaga_info['descricao_resumida']}")
                            if vaga_info.get('tem_descricao_estruturada'):
                                st.write("✅ **Descrição estruturada:** Disponível")

                    st.markdown("---")

                    # Botão para gerar ranking
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🚀 Gerar Ranking Completo", type="primary", use_container_width=True):
                            try:
                                with st.spinner("🔄 Gerando ranking... Isso pode levar alguns segundos."):
                                    # Fazer requisição sem top_k para pegar todos os candidatos
                                    response = requests.get(f"{API_URL}/jobs/{job_id}/rank")

                                    if response.status_code == 200:
                                        result = response.json()

                                        st.success("✅ Ranking gerado com sucesso!")

                                        # Informações da vaga
                                        st.subheader(f"🎯 {result['vaga']['titulo']}")

                                        # Mostrar descrição completa se disponível
                                        if result['vaga'].get('descricao'):
                                            with st.expander("📄 Descrição Completa da Vaga"):
                                                st.write(result['vaga']['descricao'])

                                        # Métricas em cards
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric(
                                                "👥 Candidatos Encontrados",
                                                result["total_candidatos_encontrados"],
                                                help="Total de candidatos que se candidataram para esta vaga"
                                            )
                                        with col2:
                                            st.metric(
                                                "🤖 Modelo de Embedding",
                                                result["parametros_busca"]["embedding_model"].replace("text-embedding-", ""),
                                                help="Modelo usado para gerar embeddings"
                                            )
                                        with col3:
                                            st.metric(
                                                "🧠 Modelo de Justificativa",
                                                result["parametros_busca"]["justification_model"],
                                                help="Modelo de IA usado para gerar justificativas"
                                            )

                                        # Verificar se há candidatos
                                        if result["total_candidatos_encontrados"] == 0:
                                            st.warning("⚠️ Nenhum candidato encontrado para esta vaga.")
                                            st.info("💡 **Dica:** Faça upload de candidatos para esta vaga na aba 'Gerenciar Candidatos'.")
                                        else:
                                            # Ranking de candidatos
                                            st.subheader("🏆 Ranking de Candidatos")
                                            st.write(f"Mostrando **{len(result['candidatos_ranqueados'])}** candidatos ordenados por relevância:")

                                            for i, candidato in enumerate(result["candidatos_ranqueados"]):
                                                # Definir cor do badge baseado na posição
                                                if candidato['posicao'] == 1:
                                                    badge_color = "🥇"
                                                elif candidato['posicao'] == 2:
                                                    badge_color = "🥈"
                                                elif candidato['posicao'] == 3:
                                                    badge_color = "🥉"
                                                else:
                                                    badge_color = f"#{candidato['posicao']}"

                                                with st.expander(
                                                    f"{badge_color} **{candidato['nome']}** - {candidato['email']}",
                                                    expanded=(i == 0)  # Expandir apenas o primeiro
                                                ):
                                                    # Tabs para organizar informações
                                                    tab1, tab2, tab3 = st.tabs(["🤖 Justificativa IA", "👤 Perfil", "📊 Dados"])

                                                    with tab1:
                                                        st.markdown("**Análise gerada por IA:**")
                                                        st.write(candidato["justificativa"])

                                                    with tab2:
                                                        if candidato.get("dados_perfil"):
                                                            perfil = candidato["dados_perfil"]

                                                            # Habilidades
                                                            if perfil.get("skills"):
                                                                st.markdown("**🛠️ Habilidades:**")
                                                                skills_text = ", ".join(perfil["skills"])
                                                                st.write(skills_text)

                                                            # Resumo
                                                            if perfil.get("summary"):
                                                                st.markdown("**📝 Resumo:**")
                                                                st.write(perfil["summary"])

                                                            # Experiência
                                                            if perfil.get("experience"):
                                                                st.markdown("**💼 Experiência:**")
                                                                for exp in perfil["experience"]:
                                                                    if isinstance(exp, dict):
                                                                        st.write(f"• **{exp.get('title', 'N/A')}** - {exp.get('company', 'N/A')} ({exp.get('period', 'N/A')})")
                                                                        if exp.get('description'):
                                                                            st.write(f"  {exp['description']}")
                                                        else:
                                                            st.info("ℹ️ Dados do perfil não disponíveis")

                                                    with tab3:
                                                        col1, col2 = st.columns(2)
                                                        with col1:
                                                            st.metric("🆔 ID do Candidato", candidato['candidato_id'])
                                                        with col2:
                                                            st.metric("📍 Posição no Ranking", candidato['posicao'])

                                                        # Botão para gerar feedback
                                                        if st.button(
                                                            f"💬 Gerar Feedback para {candidato['nome']}",
                                                            key=f"feedback_{candidato['candidato_id']}"
                                                        ):
                                                            st.info("🔄 Redirecionando para a página de feedback...")
                                                            st.session_state.feedback_candidate_id = candidato['candidato_id']
                                                            st.session_state.feedback_candidate_name = candidato['nome']
                                                            st.session_state.feedback_job_description = result['vaga']['descricao']
                                                            st.rerun()

                                    elif response.status_code == 404:
                                        st.error("❌ Vaga não encontrada")
                                    else:
                                        st.error(f"❌ Erro ao gerar ranking: {response.text}")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
            else:
                st.warning("⚠️ Nenhuma vaga cadastrada.")
                st.info("💡 **Dica:** Cadastre vagas primeiro na aba '🎯 Gerenciar Vagas'.")
        else:
            st.error("❌ Erro ao carregar vagas")
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

def feedback_page():
    st.header("💬 Geração de Feedback")

    # Verificar se há dados da sessão (vindos do ranking)
    if hasattr(st.session_state, 'feedback_candidate_id'):
        st.info(f"🔄 Gerando feedback para: **{st.session_state.feedback_candidate_name}**")
        candidate_id = st.session_state.feedback_candidate_id
        job_description = st.session_state.feedback_job_description

        # Limpar dados da sessão
        del st.session_state.feedback_candidate_id
        del st.session_state.feedback_candidate_name
        del st.session_state.feedback_job_description

        # Gerar feedback automaticamente
        generate_feedback_for_candidate(candidate_id, job_description)

    else:
        # Interface com grid de candidatos
        st.info("💡 Selecione uma vaga para ver os candidatos e gerar feedback personalizado.")

        # Carregar vagas disponíveis
        try:
            response = requests.get(f"{API_URL}/jobs/")
            if response.status_code == 200:
                vagas_data = response.json()
                vagas = vagas_data.get("vagas", [])

                if vagas:
                    # Filtro por vaga
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Criar dicionário para mapear título -> vaga completa
                        vaga_options = {"🔍 Todas as vagas": None}
                        for vaga in vagas:
                            titulo_completo = f"🎯 {vaga['titulo']}"
                            vaga_options[titulo_completo] = vaga

                        vaga_selecionada_key = st.selectbox(
                            "📋 Filtrar por Vaga:",
                            options=list(vaga_options.keys()),
                            help="Selecione uma vaga específica para filtrar candidatos"
                        )

                        vaga_selecionada = vaga_options[vaga_selecionada_key]

                    with col2:
                        # Botão para atualizar dados
                        if st.button("🔄 Atualizar", help="Recarregar dados de candidatos"):
                            st.rerun()

                    st.markdown("---")

                    # Carregar candidatos
                    try:
                        if vaga_selecionada:
                            # Candidatos de uma vaga específica
                            response = requests.get(f"{API_URL}/jobs/{vaga_selecionada['id']}/candidates")
                            if response.status_code == 200:
                                candidatos_data = response.json()
                                candidatos = candidatos_data.get("candidatos", [])
                                st.subheader(f"👥 Candidatos da Vaga: {vaga_selecionada['titulo']}")
                            else:
                                candidatos = []
                                st.warning(f"⚠️ Erro ao carregar candidatos da vaga: {response.text}")
                        else:
                            # Todos os candidatos
                            response = requests.get(f"{API_URL}/candidates/")
                            if response.status_code == 200:
                                candidatos_data = response.json()
                                candidatos = candidatos_data.get("candidatos", [])
                                st.subheader("👥 Todos os Candidatos")
                            else:
                                candidatos = []
                                st.warning(f"⚠️ Erro ao carregar candidatos: {response.text}")

                        if candidatos:
                            # Métricas
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("👥 Total de Candidatos", len(candidatos))
                            with col2:
                                if vaga_selecionada:
                                    st.metric("🎯 Vaga Selecionada", vaga_selecionada['id'])
                                else:
                                    total_vagas = len(set(c.get('vaga_id', 'N/A') for c in candidatos))
                                    st.metric("🎯 Vagas Representadas", total_vagas)
                            with col3:
                                st.metric("📊 Status", "Ativos")

                            # Barra de pesquisa
                            search_term = st.text_input(
                                "🔍 Pesquisar candidatos:",
                                placeholder="Digite nome, email ou habilidades...",
                                help="Pesquise por nome, email ou habilidades dos candidatos"
                            )

                            # Filtrar candidatos pela pesquisa
                            if search_term:
                                candidatos_filtrados = []
                                for candidato in candidatos:
                                    search_fields = [
                                        candidato.get('nome', '').lower(),
                                        candidato.get('email', '').lower(),
                                        str(candidato.get('dados_perfil', {}).get('skills', [])).lower(),
                                        candidato.get('dados_perfil', {}).get('summary', '').lower()
                                    ]
                                    if any(search_term.lower() in field for field in search_fields):
                                        candidatos_filtrados.append(candidato)
                                candidatos = candidatos_filtrados

                                if candidatos:
                                    st.success(f"✅ {len(candidatos)} candidato(s) encontrado(s)")
                                else:
                                    st.warning("⚠️ Nenhum candidato encontrado com os critérios de pesquisa")

                            # Grid de candidatos
                            if candidatos:
                                st.markdown("### 📋 Lista de Candidatos")

                                # Configurar paginação
                                items_per_page = 5
                                total_pages = (len(candidatos) - 1) // items_per_page + 1

                                if total_pages > 1:
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    with col2:
                                        page = st.selectbox(
                                            "📄 Página:",
                                            range(1, total_pages + 1),
                                            format_func=lambda x: f"Página {x} de {total_pages}"
                                        )
                                else:
                                    page = 1

                                # Calcular índices da página
                                start_idx = (page - 1) * items_per_page
                                end_idx = min(start_idx + items_per_page, len(candidatos))
                                candidatos_pagina = candidatos[start_idx:end_idx]

                                # Mostrar candidatos da página atual
                                for i, candidato in enumerate(candidatos_pagina):
                                    with st.container():
                                        # Card do candidato
                                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                                        with col1:
                                            st.markdown(f"**👤 {candidato.get('nome', 'N/A')}**")
                                            st.markdown(f"📧 {candidato.get('email', 'N/A')}")

                                            # Mostrar vaga se não estiver filtrada
                                            if not vaga_selecionada and candidato.get('vaga_titulo'):
                                                st.markdown(f"🎯 *{candidato.get('vaga_titulo', 'N/A')}*")

                                        with col2:
                                            st.markdown(f"**🆔 ID:** {candidato.get('id', 'N/A')}")
                                            if candidato.get('vaga_id'):
                                                st.markdown(f"**🎯 Vaga ID:** {candidato.get('vaga_id', 'N/A')}")

                                        with col3:
                                            # Mostrar habilidades principais
                                            skills = candidato.get('dados_perfil', {}).get('skills', [])
                                            if skills:
                                                st.markdown("**🛠️ Habilidades:**")
                                                skills_text = ", ".join(skills[:3])  # Mostrar apenas 3 primeiras
                                                if len(skills) > 3:
                                                    skills_text += f" (+{len(skills)-3})"
                                                st.markdown(f"*{skills_text}*")
                                            else:
                                                st.markdown("*Sem habilidades cadastradas*")

                                        with col4:
                                            # Botões de ação
                                            if vaga_selecionada:
                                                # Se vaga está selecionada, usar sua descrição
                                                if st.button(
                                                    f"💬 Gerar Feedback",
                                                    key=f"feedback_auto_{candidato['id']}",
                                                    help=f"Gerar feedback para {candidato.get('nome')} na vaga {vaga_selecionada['titulo']}",
                                                    use_container_width=True
                                                ):
                                                    generate_feedback_for_candidate(
                                                        candidato['id'],
                                                        vaga_selecionada.get('descricao', ''),
                                                        candidato.get('nome', 'Candidato'),
                                                        vaga_selecionada['titulo']
                                                    )
                                            else:
                                                # Se não há vaga selecionada, mostrar botão para selecionar vaga
                                                if st.button(
                                                    f"🎯 Selecionar Vaga",
                                                    key=f"select_job_{candidato['id']}",
                                                    help=f"Selecionar vaga para gerar feedback de {candidato.get('nome')}",
                                                    use_container_width=True
                                                ):
                                                    st.session_state[f"show_job_selector_{candidato['id']}"] = True
                                                    st.rerun()

                                            # Botão para ver detalhes
                                            if st.button(
                                                f"👀 Detalhes",
                                                key=f"details_{candidato['id']}",
                                                help=f"Ver detalhes completos de {candidato.get('nome')}",
                                                use_container_width=True
                                            ):
                                                st.session_state[f"show_details_{candidato['id']}"] = True
                                                st.rerun()

                                        # Mostrar seletor de vaga se solicitado
                                        if st.session_state.get(f"show_job_selector_{candidato['id']}", False):
                                            with st.expander(f"🎯 Selecionar Vaga para {candidato.get('nome')}", expanded=True):
                                                col1, col2 = st.columns([3, 1])
                                                with col1:
                                                    vaga_para_feedback = st.selectbox(
                                                        "Escolha a vaga:",
                                                        options=vagas,
                                                        format_func=lambda x: f"{x['titulo']} (ID: {x['id']})",
                                                        key=f"job_selector_{candidato['id']}"
                                                    )
                                                with col2:
                                                    if st.button(
                                                        "✅ Confirmar",
                                                        key=f"confirm_job_{candidato['id']}",
                                                        type="primary"
                                                    ):
                                                        generate_feedback_for_candidate(
                                                            candidato['id'],
                                                            vaga_para_feedback.get('descricao', ''),
                                                            candidato.get('nome', 'Candidato'),
                                                            vaga_para_feedback['titulo']
                                                        )
                                                        del st.session_state[f"show_job_selector_{candidato['id']}"]
                                                        st.rerun()

                                                if st.button(
                                                    "❌ Cancelar",
                                                    key=f"cancel_job_{candidato['id']}"
                                                ):
                                                    del st.session_state[f"show_job_selector_{candidato['id']}"]
                                                    st.rerun()

                                        # Mostrar detalhes se solicitado
                                        if st.session_state.get(f"show_details_{candidato['id']}", False):
                                            with st.expander(f"👤 Detalhes de {candidato.get('nome')}", expanded=True):
                                                col1, col2 = st.columns(2)

                                                with col1:
                                                    st.markdown("**📋 Informações Básicas:**")
                                                    st.write(f"**ID:** {candidato.get('id', 'N/A')}")
                                                    st.write(f"**Nome:** {candidato.get('nome', 'N/A')}")
                                                    st.write(f"**Email:** {candidato.get('email', 'N/A')}")
                                                    if candidato.get('vaga_id'):
                                                        st.write(f"**Vaga ID:** {candidato.get('vaga_id', 'N/A')}")
                                                        st.write(f"**Vaga:** {candidato.get('vaga_titulo', 'N/A')}")

                                                with col2:
                                                    perfil = candidato.get('dados_perfil', {})
                                                    if perfil:
                                                        st.markdown("**🛠️ Perfil Profissional:**")

                                                        if perfil.get('skills'):
                                                            st.write(f"**Habilidades:** {', '.join(perfil['skills'])}")

                                                        if perfil.get('summary'):
                                                            st.write(f"**Resumo:** {perfil['summary']}")

                                                        if perfil.get('experience'):
                                                            st.write("**Experiência:**")
                                                            for exp in perfil['experience'][:2]:  # Mostrar apenas 2 primeiras
                                                                if isinstance(exp, dict):
                                                                    st.write(f"• {exp.get('title', 'N/A')} - {exp.get('company', 'N/A')}")
                                                    else:
                                                        st.write("*Dados do perfil não disponíveis*")

                                                if st.button(
                                                    "❌ Fechar Detalhes",
                                                    key=f"close_details_{candidato['id']}"
                                                ):
                                                    del st.session_state[f"show_details_{candidato['id']}"]
                                                    st.rerun()

                                        st.markdown("---")

                                # Informações da paginação
                                if total_pages > 1:
                                    st.info(f"📄 Mostrando {start_idx + 1}-{end_idx} de {len(candidatos)} candidatos (Página {page} de {total_pages})")

                        else:
                            if vaga_selecionada:
                                st.warning(f"⚠️ Nenhum candidato encontrado para a vaga: **{vaga_selecionada['titulo']}**")
                                st.info("💡 **Dica:** Faça upload de candidatos para esta vaga na aba 'Gerenciar Candidatos'.")
                            else:
                                st.warning("⚠️ Nenhum candidato cadastrado no sistema.")
                                st.info("💡 **Dica:** Cadastre candidatos primeiro na aba 'Gerenciar Candidatos'.")

                    except Exception as e:
                        st.error(f"❌ Erro ao carregar candidatos: {str(e)}")

                else:
                    st.warning("⚠️ Nenhuma vaga cadastrada.")
                    st.info("💡 **Dica:** Cadastre vagas primeiro na aba 'Gerenciar Vagas'.")

            else:
                st.error("❌ Erro ao carregar vagas")

        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

def generate_feedback_for_candidate(candidate_id, job_description, candidate_name="Candidato", job_title="Vaga"):
    """Função auxiliar para gerar feedback de um candidato"""
    if not job_description or not job_description.strip():
        st.error("❌ Descrição da vaga não disponível para gerar feedback")
        return

    try:
        with st.spinner(f"🤖 Gerando feedback para {candidate_name}..."):
            payload = {"job_description": job_description.strip()}
            response = requests.post(
                f"{API_URL}/candidates/{candidate_id}/feedback",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                st.success(f"✅ Feedback gerado para {candidate_name}!")

                # Mostrar resultado em um container destacado
                with st.container():
                    st.markdown(f"### 💬 Feedback para {result['candidate_name']}")
                    st.markdown(f"**📧 Email:** {result['candidate_email']}")
                    st.markdown(f"**🎯 Vaga:** {job_title}")

                    st.markdown("---")

                    # Feedback formatado
                    st.markdown("**🤖 Feedback Gerado:**")
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                width: 100%;
                                max-width: 800px;
                                background-color: #e0e3e7;
                                color: #333;
                                padding: 20px;
                                border-radius: 10px;
                                border-left: 5px solid #1f77b4;
                                margin: 20px auto;
                            ">
                                {result["feedback"].replace('**', '<strong>').replace('**', '</strong>')}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # Opções adicionais
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📋 Copiar Feedback", key=f"copy_{candidate_id}"):
                            st.info("🚧 Funcionalidade em desenvolvimento")
                    with col2:
                        if st.button(f"📧 Enviar Email", key=f"email_{candidate_id}"):
                            st.info("🚧 Funcionalidade em desenvolvimento")
                    with col3:
                        if st.button(f"💾 Salvar", key=f"save_{candidate_id}"):
                            st.info("🚧 Funcionalidade em desenvolvimento")

            elif response.status_code == 404:
                st.error(f"❌ Candidato {candidate_name} não encontrado")
            else:
                st.error(f"❌ Erro ao gerar feedback: {response.text}")

    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()