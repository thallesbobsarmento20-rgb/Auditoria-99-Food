import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px
from fpdf import FPDF

# 1. CONFIGURAÇÃO DE SEGURANÇA (LOGIN)
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 QA 99 Food - Login")
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

if check_password():
    # 2. CONEXÃO COM GOOGLE SHEETS
    import json
from google.oauth2 import service_account
import streamlit as st

service_account_info = json.loads(st.secrets["gcp_service_account"])

creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

    # 3. INTERFACE

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/43/99_logo.svg", width=100)

aba1, aba2 = st.tabs(["📝 Auditoria", "📈 Dashboard"])

with aba1:
st.header("Nova Auditoria de Menu")
with st.form("form_qa"):
loja = st.text_input("Nome/ID da Loja")
analista = st.selectbox("Analista Responsável", ["Ana", "Bruno", "Carlos"])
            
st.write("---")
c1 = st.checkbox("Preços estão corretos? (Peso 40%)")
c2 = st.checkbox("Regras de Complementos OK? (Peso 30%)")
c3 = st.checkbox("Fotos seguem o padrão? (Peso 15%)")
c4 = st.checkbox("Categorização correta? (Peso 10%)")
c5 = st.checkbox("Texto sem erros ortográficos? (Peso 5%)")
obs = st.text_area("Observações Adicionais")
            
            submit = st.form_submit_button("Registrar e Gerar Feedback")

        if submit:
            # Cálculo do Score
            score = (40 if c1 else 0) + (30 if c2 else 0) + (15 if c3 else 0) + (10 if c4 else 0) + (5 if c5 else 0)
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Salvar no Sheets
            sheet = conectar()
            sheet.append_row([data_hoje, loja, analista, int(c1), int(c2), int(c3), int(c4), int(c5), score, obs])
            
            st.success(f"Nota Final: {score}%")
            
            # Gerador de Texto para Copiar
            erros = [e for e, v in zip(["Preço", "Regras", "Fotos", "Cat", "Texto"], [c1,c2,c3,c4,c5]) if not v]
            st.code(f"Olá {analista}, menu da loja {loja} auditado.\nScore: {score}%\nCorreções: {', '.join(erros) if erros else 'Nenhuma'}")

    with aba2:
        st.header("Performance do Time")
        sheet = conectar()
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            fig = px.line(df, x="Data", y="Score", color="Analista", title="Evolução da Qualidade")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.tail(10))
