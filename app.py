import streamlit as st
import pandas as pd
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="BioNutri Farma", layout="wide", page_icon="🌿")

# Estilização CSS Customizada
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
    
    perc_g = ((4.95 / densidade) - 4.50) * 100
    m_gorda = peso * (perc_g / 100)
    m_magra = peso - m_gorda
    return perc_g, m_gorda, m_magra

def calcular_metabolismo(peso, altura, idade, sexo, nivel_atividade):
    # Equação de Mifflin-St Jeor
    if sexo == "Masculino":
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    
    fatores = {
        "Sedentário": 1.2,
        "Levemente Ativo": 1.375,
        "Moderadamente Ativo": 1.55,
        "Muito Ativo": 1.725,
        "Extremamente Ativo": 1.9
    }
    get = tmb * fatores[nivel_atividade]
    return tmb, get

def calcular_agua(peso):
    return peso * 35 / 1000  # 35ml por kg

# --- INTERFACE ---

st.title("🌿 BioNutri Farma")
st.caption("Responsável Técnica: Dra. Carla Ferraz (Farmacêutica & Nutricionista)")

# Sidebar
with st.sidebar:
    st.header("📋 Dados do Paciente")
    nome = st.text_input("Nome Completo")
    idade = st.number_input("Idade", min_value=1, max_value=120, value=30)
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    peso = st.number_input("Peso (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.1)
    altura = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170)
    atividade = st.selectbox("Nível de Atividade", 
                             ["Sedentário", "Levemente Ativo", "Moderadamente Ativo", "Muito Ativo", "Extremamente Ativo"])

tabs = st.tabs(["📏 Antropometria", "🤏 Dobras Cutâneas", "📊 Resultados & Relatório"])

with tabs[0]:
    st.subheader("Medidas Circunferenciais (cm)")
    col1, col2 = st.columns(2)
    with col1:
        braço_d = st.number_input("Braço Direito", value=30.0)
        coxa_d = st.number_input("Coxa Direita", value=55.0)
    with col2:
        cintura = st.number_input("Cintura", value=80.0)
        quadril = st.number_input("Quadril", value=100.0)

with tabs[1]:
    st.subheader("Protocolo Pollock (7 Dobras) - mm")
    col1, col2 = st.columns(2)
    dobras = {}
    with col1:
        dobras['Tríceps'] = st.number_input("Tríceps", value=12.0)
        dobras['Subescapular'] = st.number_input("Subescapular", value=15.0)
        dobras['Supra-ilíaca'] = st.number_input("Supra-ilíaca", value=18.0)
        dobras['Axilar Média'] = st.number_input("Axilar Média", value=15.0)
    with col2:
        dobras['Peitoral'] = st.number_input("Peitoral", value=12.0)
        dobras['Abdominal'] = st.number_input("Abdominal", value=20.0)
        dobras['Coxa'] = st.number_input("Coxa", value=20.0)

with tabs[2]:
    # Cálculos
    imc, imc_classe = calcular_imc(peso, altura)
    rcq, rcq_risco = calcular_rcq(cintura, quadril, sexo)
    perc_gordura, m_gorda, m_magra = calcular_composicao(sexo, idade, peso, dobras)
    tmb, get = calcular_metabolismo(peso, altura, idade, sexo, atividade)
    agua_diaria = calcular_agua(peso)

    # Dashboard
    st.subheader("Dashboard Clínico")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IMC", f"{imc:.1f}", imc_classe)
    c2.metric("RCQ", f"{rcq:.2f}", f"Risco {rcq_risco}")
    c3.metric("% Gordura", f"{perc_gordura:.1f}%")
    c4.metric("Massa Magra", f"{m_magra:.1f} kg")

    st.markdown("---")
    
    # NOVA SEÇÃO: PLANEJAMENTO NUTRICIONAL
    st.subheader("⚡ Planejamento Energético e Hidratação")
    
    if st.button("Calcular Necessidades Nutricionais"):
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write("**Gasto Energético (Kcal)**")
            metas_caloricas = {
                "Objetivo": ["Taxa Metabólica Basal", "Manter Peso", "Emagrecimento (Déficit)", "Ganho de Massa (Superávit)"],
                "Calorias (kcal)": [f"{tmb:.0f}", f"{get:.0f}", f"{get-500:.0f}", f"{get+400:.0f}"]
            }
            st.table(pd.DataFrame(metas_caloricas))
        
        with col_res2:
            st.write("**Ingestão Hídrica Recomendada**")
            st.metric("Água Diária", f"{agua_diaria:.2f} Litros")
            st.info("Recomendação baseada em 35ml por quilo de peso corporal.")

    # GERAÇÃO DE PDF ATUALIZADA
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_fill_color(26, 35, 126) # Azul Marinho
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 20, "BioNutri Farma - Relatorio Nutricional", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Dra. Carla Ferraz - Farmaceutica & Nutricionista", ln=True, align='C')
        
        # Dados Paciente
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Paciente: {nome}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 7, f"Idade: {idade} anos | Sexo: {sexo} | Peso: {peso}kg | Altura: {altura}cm", ln=True)
        pdf.cell(0, 7, f"Atividade: {atividade}", ln=True)
        
        # Composição Corporal
        pdf.ln(5)
        pdf.set_fill_color(232, 245, 233)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "1. COMPOSICAO CORPORAL", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"IMC: {imc:.2f} ({imc_classe})", ln=True)
        pdf.cell(0, 8, f"Percentual de Gordura: {perc_gordura:.2f}%", ln=True)
        pdf.cell(0, 8, f"Massa Magra: {m_magra:.2f}kg | Massa Gorda: {m_gorda:.2f}kg", ln=True)
        
        # Energético
        pdf.ln(5)
        pdf.set_fill_color(232, 245, 233)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. PLANEJAMENTO ENERGETICO E HIDRICO", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Taxa Metabolica Basal: {tmb:.0f} kcal", ln=True)
        pdf.cell(0, 8, f"Gasto Energetico Total (Manter Peso): {get:.0f} kcal", ln=True)
        pdf.cell(0, 8, f"Meta para Emagrecimento: {get-500:.0f} kcal", ln=True)
        pdf.cell(0, 8, f"Meta para Ganho de Massa: {get+400:.0f} kcal", ln=True)
        pdf.cell(0, 8, f"RECOMENDACAO DE AGUA: {agua_diaria:.2f} Litros/dia", ln=True)

        return pdf.output(dest='S').encode('latin-1')

    st.markdown("---")
    pdf_output = gerar_pdf()
    st.download_button(
        label="📄 Baixar Relatório Clínico Completo",
        data=pdf_output,
        file_name=f"Relatorio_{nome}.pdf",
        mime="application/pdf"
    )
