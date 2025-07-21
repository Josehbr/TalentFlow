import streamlit as st
import requests

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Configuração da página
st.set_page_config(
    page_title="TalentFlow - Seleção Inteligente",
    page_icon="🚀",
    layout="wide"
)

# URL da API
API_URL = "http://localhost:8000"

def add_footer():
    st.markdown("---")
    st.markdown("Feito com ❤️ por [seu nome ou time](link-para-seu-github)")

def main():
    load_css("frontend/style.css")
    st.sidebar.title("TalentFlow")
    st.sidebar.markdown("---")
    
    st.title("Bem-vindo ao TalentFlow!")
    
    # Status da API
    try:
        response = requests.get(f"{API_URL}/jobs/health", timeout=5)
        if response.status_code == 200:
            st.success("API funcionando corretamente!")
        else:
            st.error("API com problemas")
    except:
        st.error("Não foi possível conectar à API")
    
    st.markdown("""
    ### Fluxo de Trabalho:
    
    1. **Gerenciar Vagas**: Faça o upload de um arquivo JSON com as vagas ou visualize as já cadastradas.
    
    2. **Gerenciar Candidatos**: Faça o upload de candidatos para uma vaga específica.
    
    3. **Ranking**: Gere um ranking de candidatos para uma vaga com base na análise de IA.
    
    4. **Feedback**: Gere feedbacks personalizados para os candidatos.
    
    Utilize o menu na barra lateral para navegar entre as funcionalidades.
    """)

if __name__ == "__main__":
    main()
    add_footer()