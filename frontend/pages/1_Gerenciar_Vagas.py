import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def jobs_page():
    load_css("frontend/style.css")
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
                            with st.container():
                                st.subheader(vaga['titulo'])
                                st.write(f"**ID:** {vaga['id']}")
                                st.write(f"**Descrição:** {vaga['descricao_resumida']}")
                                if vaga["tem_descricao_estruturada"]:
                                    st.success("Possui descrição estruturada")
                                else:
                                    st.warning("Sem descrição estruturada")
                                st.markdown("---")
                    else:
                        st.info("Nenhuma vaga cadastrada ainda")
                else:
                    st.error(f"Erro ao carregar vagas: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

def add_footer():
    st.markdown("---")
    st.markdown("Feito com ❤️ por [seu nome ou time](link-para-seu-github)")

if __name__ == "__main__":
    jobs_page()
    add_footer()
