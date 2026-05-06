import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Configuração da Página
st.set_page_config(page_title="BioNutri Farma", layout="wide", page_icon="🌿")

# Estilização CSS Customizada (Cores Clínicas)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #1A237E; color: white; border-radius: 8px; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #e8f5e9; border-radius: 5px; }
    div[data-testid="stMetricValue"] { color: #2E7D32; }
    h1, h2, h3 { color: #1A237E; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CÁLCULO ---

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5: classe = "Abaixo do peso"
    elif imc < 25: classe = "Peso normal"
    elif imc < 30: classe = "Sobrepeso"
    else: classe = "Obesidade"
    return imc, classe

def calcular_rcq(cintura, quadril, sexo):
    rcq = cintura / quadril
    # Tabela simplificada de risco
    if sexo == "Masculino":
        risco = "Baixo" if rcq < 0.90 else "Moderado" if rcq < 0.96 else "Alto"
    else:
        risco = "Baixo" if rcq < 0.80 else "Moderado" if rcq < 0.86 else "Alto"
    return rcq, risco

def calcular_composicao(sexo, idade, peso, dobras):
    soma_7 = sum(dobras.values())
    if sexo == "Masculino":
        densidade = 1.112 - (0.00043499 * soma_7) + (0.00000055 * (soma_7 ** 2)) - (0.00028826 * idade)
    else:
        densidade = 1.097 - (0.00046971 * soma_7) + (0.00000056 * (soma_7 ** 2)) - (0.00012828 * idade)
    
    percentual_gordura = ((4.95 / densidade) - 4.50) * 100
    massa_gorda = peso * (percentual_gordura / 100)
    massa_magra = peso - massa_gorda
    return percentual_gordura, massa_gorda, massa_magra

# --- INTERFACE ---

st.title("🌿 BioNutri Farma")
st.caption("Responsável Técnica: Dra. Carla Ferraz (Farmacêutica & Nutricionista)")

# Sidebar para Dados Cadastrais
with st.sidebar:
    st.header("📋 Dados do Paciente")
    nome = st.text_input("Nome Completo")
    idade = st.number_input("Idade", min_value=1, max_value=120, value=30)
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    peso = st.number_input("Peso (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.1)
    altura = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170)

tabs = st.tabs(["📏 Antropometria", "🤏 Dobras Cutâneas", "📊 Resultados & Relatório"])

with tabs[0]:
    st.subheader("Medidas Circunferenciais (cm)")
    col1, col2 = st.columns(2)
    with col1:
        braço_d = st.number_input("Braço Direito", value=30.0)
        braço_e = st.number_input("Braço Esquerdo", value=30.0)
        coxa_d = st.number_input("Coxa Direita", value=55.0)
        coxa_e = st.number_input("Coxa Esquerda", value=55.0)
    with col2:
        pescoço = st.number_input("Pescoço", value=38.0)
        cintura = st.number_input("Cintura", value=80.0)
        barriga = st.number_input("Abdominal (Cintura)", value=85.0)
        quadril = st.number_input("Quadril", value=100.0)
        panturrilha_d = st.number_input("Panturrilha Direita", value=35.0)

with tabs[1]:
    st.subheader("Protocolo Pollock (7 Dobras) - mm")
    col1, col2 = st.columns(2)
    dobras = {}
    with col1:
        dobras['Bíceps'] = st.number_input("Bíceps", value=10.0)
        dobras['Tríceps'] = st.number_input("Tríceps", value=12.0)
        dobras['Subescapular'] = st.number_input("Subescapular", value=15.0)
        dobras['Axilar Média'] = st.number_input("Axilar Média", value=15.0)
    with col2:
        dobras['Peitoral'] = st.number_input("Peitoral", value=12.0)
        dobras['Supra-ilíaca'] = st.number_input("Supra-ilíaca", value=18.0)
        dobras['Abdominal'] = st.number_input("Abdominal", value=20.0)

with tabs[2]:
    # Cálculos
    imc, imc_classe = calcular_imc(peso, altura)
    rcq, rcq_risco = calcular_rcq(cintura, quadril, sexo)
    perc_gordura, m_gorda, m_magra = calcular_composicao(sexo, idade, peso, dobras)

    # Dashboard
    st.subheader("Dashboard Clínico")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IMC", f"{imc:.1f}", imc_classe)
    c2.metric("RCQ", f"{rcq:.2f}", f"Risco {rcq_risco}")
    c3.metric("% Gordura", f"{perc_gordura:.1f}%")
    c4.metric("Massa Magra", f"{m_magra:.1f} kg")

    # Tabelas de Referência
    st.markdown("---")
    st.write("### 📚 Tabelas de Referência")
    
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        st.write("**Referência % Gordura (Pollock/ACSM)**")
        ref_data = {
            "Classificação": ["Atleta", "Bom", "Normal", "Elevado", "Muito Elevado"],
            "Homens (20-39)": ["6-10%", "11-16%", "17-21%", "22-26%", ">26%"],
            "Mulheres (20-39)": ["12-15%", "16-23%", "24-30%", "31-36%", ">36%"]
        }
        st.table(pd.DataFrame(ref_data))

    # GERAÇÃO DE PDF
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_fill_color(184, 134, 11) # Cor B8860B (Dourado Profundo)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 22)
        pdf.cell(0, 20, "BioNutri Farma - Relatorio Clinico", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Dra. Carla Ferraz - Farmaceutica & Nutricionista", ln=True, align='C')
        
        # Dados do Paciente
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Paciente: {nome}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Idade: {idade} anos | Sexo: {sexo} | Peso: {peso}kg | Altura: {altura}cm", ln=True)
        
        # Resultados
        pdf.ln(10)
        pdf.set_fill_color(232, 245, 233) # Verde Claro
        pdf.cell(0, 10, "RESULTADOS DA AVALIACAO", ln=True, fill=True, align='C')
        pdf.cell(0, 10, f"IMC: {imc:.2f} ({imc_classe})", ln=True)
        pdf.cell(0, 10, f"RCQ: {rcq:.2f} (Risco {rcq_risco})", ln=True)
        pdf.cell(0, 10, f"Percentual de Gordura: {perc_gordura:.2f}%", ln=True)
        pdf.cell(0, 10, f"Massa Gorda: {m_gorda:.2f} kg", ln=True)
        pdf.cell(0, 10, f"Massa Magra: {m_magra:.2f} kg", ln=True)
        
        # Dobras
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DOBRAS CUTANEAS (mm)", ln=True)
        pdf.set_font("Arial", '', 10)
        for k, v in dobras.items():
            pdf.cell(90, 8, f"{k}: {v} mm", border=1)
            pdf.ln()

        return pdf.output(dest='S').encode('latin-1')

    pdf_output = gerar_pdf()
    st.download_button(
        label="📄 Baixar Relatório PDF Profissional",
        data=pdf_output,
        file_name=f"Avaliacao_{nome}.pdf",
        mime="application/pdf"
    )
