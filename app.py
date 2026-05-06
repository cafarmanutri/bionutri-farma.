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
        if rcq < 0.90: risco = "Baixo"
        elif rcq <= 0.95: risco = "Moderado"
        elif rcq <= 1.0: risco = "Alto"
        else: risco = "Muito Alto"
    else:
        if rcq < 0.80: risco = "Baixo"
        elif rcq <= 0.85: risco = "Moderado"
        elif rcq <= 0.90: risco = "Alto"
        else: risco = "Muito Alto"
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
    if sexo == "Masculino":
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    
    fatores = {"Sedentario": 1.2, "Levemente Ativo": 1.375, "Moderadamente Ativo": 1.55, "Muito Ativo": 1.725, "Extremamente Ativo": 1.9}
    get = tmb * fatores.get(nivel_atividade, 1.2)
    return tmb, get

def calcular_agua(peso):
    return peso * 35 / 1000

# --- INTERFACE ---

st.title("🌿 BioNutri Farma")
st.caption("Responsável Técnica: Dra. Carla Ferraz (Farmacêutica & Nutricionista)")

# Sidebar
with st.sidebar:
    st.header("📋 Dados do Paciente")
    nome = st.text_input("Nome Completo", "Nome do Paciente")
    idade = st.number_input("Idade", min_value=1, max_value=120, value=30)
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    peso = st.number_input("Peso (kg)", min_value=10.0, value=70.0)
    altura = st.number_input("Altura (cm)", min_value=50, value=170)
    atividade = st.selectbox("Nivel de Atividade", ["Sedentario", "Levemente Ativo", "Moderadamente Ativo", "Muito Ativo", "Extremamente Ativo"])

tabs = st.tabs(["📏 Antropometria", "🤏 Dobras Cutâneas", "📊 Resultados & Relatório"])

with tabs[0]:
    st.subheader("Medidas Circunferenciais (cm)")
    col1, col2, col3 = st.columns(3)
    with col1:
        pescoco = st.number_input("Pescoço", value=35.0)
        braco_d = st.number_input("Braço Direito", value=30.0)
        braco_e = st.number_input("Braço Esquerdo", value=30.0)
    with col2:
        cintura = st.number_input("Cintura (Estreita)", value=80.0)
        abdomen = st.number_input("Abdômen (Cintura Larga)", value=85.0)
        quadril = st.number_input("Quadril", value=100.0)
    with col3:
        coxa_d = st.number_input("Coxa Direita", value=55.0)
        coxa_e = st.number_input("Coxa Esquerda", value=55.0)
        pant_d = st.number_input("Panturrilha Direita", value=36.0)
        pant_e = st.number_input("Panturrilha Esquerda", value=36.0)

with tabs[1]:
    st.subheader("Protocolo Pollock (7 Dobras) - mm")
    c1, c2 = st.columns(2)
    dobras = {}
    with c1:
        dobras['Bíceps'] = st.number_input("Bíceps", value=8.0)
        dobras['Tríceps'] = st.number_input("Tríceps", value=12.0)
        dobras['Subescapular'] = st.number_input("Subescapular", value=15.0)
        dobras['Axilar Média'] = st.number_input("Axilar Média", value=15.0)
    with c2:
        dobras['Peitoral'] = st.number_input("Peitoral", value=12.0)
        dobras['Supra-ilíaca'] = st.number_input("Supra-ilíaca", value=18.0)
        dobras['Abdominal'] = st.number_input("Abdominal", value=20.0)

with tabs[2]:
    # Cálculos
    imc, imc_classe = calcular_imc(peso, altura)
    rcq, rcq_risco = calcular_rcq(cintura, quadril, sexo)
    perc_gordura, m_gorda, m_magra = calcular_composicao(sexo, idade, peso, dobras)
    tmb, get = calcular_metabolismo(peso, altura, idade, sexo, atividade)
    agua = calcular_agua(peso)

    # Dashboard
    st.subheader("Dashboard Clínico")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric("IMC", f"{imc:.1f}", imc_classe)
    res2.metric("RCQ", f"{rcq:.2f}", f"Risco {rcq_risco}")
    res3.metric("% Gordura", f"{perc_gordura:.1f}%")
    res4.metric("Água Diária", f"{agua:.2f} L")

    st.markdown("---")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**Referência RCQ (Relação Cintura-Quadril)**")
        rcq_data = {
            "Risco": ["Baixo", "Moderado", "Alto", "Muito Alto"],
            "Homens": ["< 0.90", "0.90 - 0.95", "0.96 - 1.00", "> 1.00"],
            "Mulheres": ["< 0.80", "0.80 - 0.85", "0.86 - 0.90", "> 0.90"]
        }
        st.table(pd.DataFrame(rcq_data))

    with col_t2:
        st.write("**Metas Calóricas (Kcal)**")
        st.write(f"🔥 Manutenção: **{get:.0f} kcal**")
        st.write(f"📉 Emagrecimento: **{get-500:.0f} kcal**")
        st.write(f"📈 Ganho de Massa: **{get+400:.0f} kcal**")

    # GERAÇÃO DE PDF
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_fill_color(26, 35, 126)
        pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, "BIONUTRI FARMA - RELATORIO CLINICO", ln=True, align='C')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 5, "Dra. Carla Ferraz - Farmaceutica & Nutricionista", ln=True, align='C')
        
        # Dados Paciente
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Paciente: {nome.upper()}", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"Idade: {idade} anos | Sexo: {sexo} | Atividade: {atividade}", ln=True)
        pdf.cell(0, 6, f"Peso: {peso}kg | Altura: {altura}cm | IMC: {imc:.2f} ({imc_classe})", ln=True)

        # Seção 1: Medidas Antropométricas
        pdf.ln(5)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "1. MEDIDAS ANTROPOMETRICAS (cm)", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        
        medidas = [
            [f"Pescoco: {pescoco}", f"Cintura: {cintura}", f"Coxa D: {coxa_d}"],
            [f"Braco D: {braco_d}", f"Abdomen: {abdomen}", f"Coxa E: {coxa_e}"],
            [f"Braco E: {braco_e}", f"Quadril: {quadril}", f"Pant. D: {pant_d}"],
            ["", f"RCQ: {rcq:.2f}", f"Pant. E: {pant_e}"]
        ]
        for row in medidas:
            pdf.cell(60, 7, row[0], 0)
            pdf.cell(60, 7, row[1], 0)
            pdf.cell(60, 7, row[2], 0)
            pdf.ln()

        # Seção 2: Referência RCQ (Tabela no PDF)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, f"2. CLASSIFICACAO RCQ - Resultado: {rcq_risco}", ln=True, fill=True)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(40, 7, "Risco", 1, 0, 'C')
        pdf.cell(75, 7, "Homens", 1, 0, 'C')
        pdf.cell(75, 7, "Mulheres", 1, 1, 'C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(40, 6, "Baixo", 1, 0, 'C'); pdf.cell(75, 6, "< 0.90", 1, 0, 'C'); pdf.cell(75, 6, "< 0.80", 1, 1, 'C')
        pdf.cell(40, 6, "Moderado", 1, 0, 'C'); pdf.cell(75, 6, "0.90 - 0.95", 1, 0, 'C'); pdf.cell(75, 6, "0.80 - 0.85", 1, 1, 'C')
        pdf.cell(40, 6, "Alto", 1, 0, 'C'); pdf.cell(75, 6, "0.96 - 1.00", 1, 0, 'C'); pdf.cell(75, 6, "0.86 - 0.90", 1, 1, 'C')
        pdf.cell(40, 6, "Muito Alto", 1, 0, 'C'); pdf.cell(75, 6, "> 1.00", 1, 0, 'C'); pdf.cell(75, 6, "> 0.90", 1, 1, 'C')

        # Seção 3: Composição e Dobras
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "3. COMPOSICAO CORPORAL E DOBRAS (mm)", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 7, f"Percentual de Gordura: {perc_gordura:.1f}%", ln=True)
        pdf.cell(0, 7, f"Massa Magra: {m_magra:.1f} kg | Massa Gorda: {m_gorda:.1f} kg", ln=True)
        
        pdf.ln(2)
        pdf.set_font("Arial", 'I', 9)
        dobras_texto = ", ".join([f"{k}: {v}mm" for k, v in dobras.items()])
        pdf.multi_cell(0, 6, f"Dobras: {dobras_texto}")

        # Seção 4: Planejamento
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "4. NECESSIDADES ENERGETICAS E HIDRICAS", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 7, f"Taxa Metabolica Basal: {tmb:.0f} kcal", ln=True)
        pdf.cell(0, 7, f"Manter Peso: {get:.0f} kcal | Emagrecer: {get-500:.0f} kcal | Massa: {get+400:.0f} kcal", ln=True)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, f"META DE HIDRATACAO: {agua:.2f} Litros de agua por dia", ln=True)

        return pdf.output(dest='S').encode('latin-1')

    st.markdown("---")
    if st.button("Gerar Relatório Final"):
        pdf_out = gerar_pdf()
        st.download_button(
            label="💾 Baixar Relatório em PDF",
            data=pdf_out,
            file_name=f"Relatorio_{nome.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
