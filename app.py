import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# -------------------------
# LOGIN
# -------------------------

def check_login():
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:
        st.title("🔐 QA 99 Food - Sistema Profissional")

        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user in st.secrets["passwords"] and password == st.secrets["passwords"][user]:
                st.session_state.logged = True
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

        st.stop()


check_login()

# -------------------------
# GOOGLE SHEETS
# -------------------------

@st.cache_resource
def conectar_planilha():

    scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]

    service_account_info = st.secrets["gcp_service_account"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info,
        scope
)

    client = gspread.authorize(creds)

    sheet = client.open("Auditorias_99Food").worksheet("Dados")
    return sheet


sheet = conectar_planilha()

# -------------------------
# MENU
# -------------------------

menu = st.sidebar.selectbox(
    "Menu",
    ["Nova Auditoria", "Dashboard", "Ranking", "Exportar PDF"]
)

# -------------------------
# FUNÇÃO SCORE
# -------------------------

def calcular_score(c1, c2, c3, c4):
    return (25 if c1 else 0) + (25 if c2 else 0) + (25 if c3 else 0) + (25 if c4 else 0)

# -------------------------
# NOVA AUDITORIA
# -------------------------

if menu == "Nova Auditoria":

    st.title("📋 Nova Auditoria")

    loja = st.text_input("Nome da Loja")
    analista = st.selectbox("Analista", ["Ana", "Bruno", "Carlos"])

    c1 = st.checkbox("Preços corretos")
    c2 = st.checkbox("Complementos OK")
    c3 = st.checkbox("Fotos OK")
    c4 = st.checkbox("Cardápio organizado")

    obs = st.text_area("Observações")

    foto = st.file_uploader("📸 Upload de Foto", type=["png", "jpg", "jpeg"])

    if st.button("Registrar Auditoria"):

        score = calcular_score(c1, c2, c3, c4)

        data = datetime.now().strftime("%d/%m/%Y %H:%M")

        sheet.append_row([
            data,
            loja,
            analista,
            c1,
            c2,
            c3,
            c4,
            score,
            obs
        ])

        st.success("✅ Auditoria registrada!")

# -------------------------
# DASHBOARD
# -------------------------

elif menu == "Dashboard":
    
    menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Registrar"]
)

if menu == "Dashboard":

    st.title("📊 Dashboard")

    data = sheet.get_all_records()

    if len(data) == 0:
        st.warning("Sem dados na planilha ainda.")
    else:
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()

        st.subheader("Dados")
        st.dataframe(df)

        if "Loja" in df.columns and "Score" in df.columns:
            fig = px.bar(df, x="Loja", y="Score", title="Score por Loja")
            st.plotly_chart(fig)
        else:
            st.info("Colunas Loja e Score não encontradas.")


elif menu == "Ranking":

    st.title("🏆 Ranking")
    st.write("Conteúdo do ranking aqui")

# -------------------------
# RANKING
# -------------------------

elif menu == "Ranking":

    st.title("🏆 Ranking de Lojas")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if len(df) > 0:
        ranking = df.groupby("Nome da Loja")["Score"].mean().sort_values(ascending=False)

        st.dataframe(ranking)

# -------------------------
# EXPORTAR PDF
# -------------------------

elif menu == "Exportar PDF":

    st.title("📄 Exportar Relatório")

    if st.button("Gerar PDF"):

        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=10)

        for i, row in df.iterrows():
            linha = f"{row['Nome da Loja']} - Score: {row['Score']}"
            pdf.cell(200, 8, txt=linha, ln=True)

        pdf.output("relatorio.pdf")

        with open("relatorio.pdf", "rb") as f:
            st.download_button(
                "⬇️ Baixar PDF",
                f,
                file_name="relatorio.pdf"
            )
