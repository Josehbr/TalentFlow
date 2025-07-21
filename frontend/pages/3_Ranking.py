import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def ranking_page():
    load_css("frontend/style.css")
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

                                                with st.container():
                                                    st.markdown(f"### {badge_color} **{candidato['nome']}**")
                                                    st.write(f"**Email:** {candidato['email']}")

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
                                                    st.markdown("---")

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

def add_footer():
    st.markdown("---")
    st.markdown("Feito com ❤️ por [seu nome ou time](link-para-seu-github)")

if __name__ == "__main__":
    ranking_page()
    add_footer()
