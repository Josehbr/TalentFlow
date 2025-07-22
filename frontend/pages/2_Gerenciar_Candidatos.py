import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def candidates_page():
    load_css("frontend/style.css")
    st.header("Gerenciamento de Candidatos")

    # Primeiro, carrega as vagas disponíveis
    try:
        response = requests.get(f"{API_URL}/jobs/")
        if response.status_code == 200:
            jobs_data = response.json()
            if jobs_data["total_vagas"] > 0:
                vagas_options = {f"{vaga['titulo']} (ID: {vaga['id']})": vaga['id']
                               for vaga in jobs_data["vagas"]}

                with st.container(border=True):
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

if __name__ == "__main__":
    candidates_page()
