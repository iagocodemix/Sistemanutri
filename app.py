import streamlit as ui
import csv
import os
import pandas as pd

NOME_ARQUIVO = 'consultas_nutricionais.csv'
SENHA_CORRETA = "Mi81283137."

ui.set_page_config(
    page_title="WebDiet Pro",
    page_icon="🥗",
    layout="wide"
)

# INTERFACE COMPACTA
ui.markdown("""
    <style>
    .stApp { background-color: #f7f9fc; }
    .metric-card {
        background-color: #ffffff; padding: 15px; 
        border-radius: 10px; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-left: 5px solid #2e7d32;
    }
    h1, h2, h3 { color: #1b5e20 !important; }
    div.stButton > button:first-child {
        background-color: #2e7d32 !important; 
        color: white !important; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

ui.title("🥗 Sistema de Nutrição")

senha = ui.text_input("Chave:", type="password")
if senha != SENHA_CORRETA:
    ui.warning("🔒 Chave clínica requerida.")
else:
    ui.success("🔑 Liberado!")
    
    aba1, aba2, aba3, aba4, aba5 = ui.tabs([
        "📋 Anamnese & MET", "📐 Antropometria", 
        "🍳 Cardápio", "📚 Histórico Geral", "📄 Prontuário"
    ])

    with aba1:
        ui.header("Ficha Clínica")
        
        if ui.button("➕ Nova Ficha / Próximo Paciente"):
            for k in list(ui.session_state.keys()): del ui.session_state[k]
            ui.rerun()
            
        c1, c2, c3 = ui.columns(3)
        nome = c1.text_input("Nome", key='nome_paciente')
        idade = c2.number_input("Idade", 1, 120, 25, key='idade_paciente')
        sexo = c3.radio("Sexo", ["M", "F"], horizontal=True, key='sexo_paciente')

        c4, c5 = ui.columns(2)
        peso = c4.number_input("Peso (kg)", 0.0, 300.0, 70.0, 0.1, key='peso_paciente')
        altura = c5.number_input("Alt (m)", 0.0, 2.5, 1.70, 0.01, key='alt_paciente')

        objetivo = ui.selectbox("Objetivo:", [
            "Emagrecimento (Déficit Calórico)", 
            "Ganho de Massa Muscular (Hipertrofia)", 
            "Melhora da Saúde (Normocalórica)"
        ], key='obj_paciente')

        modalidade = ui.selectbox("Esporte (MET):", [
            "Musculação Intensa (MET: 6.0)", 
            "Corrida Moderada 8km/h (MET: 8.3)", 
            "Natação Funcional (MET: 6.0)", 
            "Ciclismo de Rua (MET: 7.5)", 
            "Nenhum / Sedentário (MET: 1.0)"
        ], key='met_paciente')
        tempo = ui.number_input("Tempo (min):", 0, 180, 60, key='tempo_paciente')

        if ui.button("Calcular", key="btn_cad"):
            if not nome or peso == 0.0 or altura == 0.0: 
                ui.error("⚠️ Dados obrigatórios!")
            else:
                imc = peso / (altura ** 2)
                agua = (peso * 35) / 1000
                alt_cm = altura * 100
                
                if sexo == "M":
                    geb = 66.5 + (13.75 * peso) + (5.003 * alt_cm) - (6.75 * idade)
                else:
                    geb = 655.1 + (9.563 * peso) + (1.85 * alt_cm) - (4.676 * idade)
                
                val_met = float(modalidade.split("MET: ")[1].replace(")", ""))
                g_treino = (val_met * 3.5 * peso / 200) * tempo
                g_total = (geb * 1.2) + g_treino

                if "Emagrecimento" in objetivo:
                    calorias, est, g_p, g_f = g_total - 500, "Hipocalórica", peso * 2.0, peso * 0.8
                elif "Hipertrofia" in objetivo:
                    calorias, est, g_p, g_f = g_total + 300, "Hipercalórica", peso * 2.2, peso * 1.0
                else:
                    calorias, est, g_p, g_f = g_total, "Normocalórica", peso * 1.5, peso * 0.9

                g_c = max(0.0, (calorias - ((g_p * 4) + (g_f * 9))) / 4)

                ui.session_state['g_total'] = g_total
                ui.session_state['calorias'] = calorias
                ui.session_state['estrategia'] = est
                ui.session_state['agua'] = agua
                ui.session_state['macros'] = f"P: {g_p:.1f}g|C: {g_c:.1f}g|G: {g_f:.1f}g"
                ui.session_state['calculado'] = True

                existe = os.path.exists(NOME_ARQUIVO)
                with open(NOME_ARQUIVO, mode='a', newline='', encoding='utf-8') as f:
                    esc = csv.writer(f)
                    if not existe:
                        esc.writerow(["Nome", "Idade", "Sexo", "Peso", "Alt", "Obj", "Est", "Kcal", "Agua"])
                    esc.writerow([nome, idade, sexo, peso, altura, objetivo, est, f"{calorias:.0f}", f"{agua:.2f}"])
                ui.success("💾 Salvo no histórico!")

        if ui.session_state.get('calculado', False):
            ui.markdown(f"""<div class='metric-card'>
            <h3>🎯 Resultado</h3>
            <p><b>Paciente:</b> {ui.session_state['nome_paciente']}</p>
            <p><b>Estratégia:</b> {ui.session_state['estrategia']}</p>
            <p><b>Meta Dieta:</b> {ui.session_state['calorias']:.0f} kcal</p>
            <p><b>Água:</b> {ui.session_state['agua']:.2f} L</p>
            <p><b>Macros:</b> {ui.session_state['macros']}</p>
            </div>""", unsafe_allow_html=True)

    with aba2:
        ui.header("Jackson & Pollock (7 Dobras)")
        ui.subheader(f"Paciente: {ui.session_state.get('nome_paciente', 'Nenhum')}")
        
        ca1, ca2, ca3, ca4 = ui.columns(4)
        dc_peit = ca1.number_input("Peitoral (mm)", 0.0, 100.0, 10.0, key='dc1')
        dc_axil = ca2.number_input("Axilar (mm)", 0.0, 100.0, 12.0, key='dc2')
        dc_tric = ca3.number_input("Tricep (mm)", 0.0, 100.0, 14.0, key='dc3')
        dc_sube = ca4.number_input("Subesc (mm)", 0.0, 100.0, 15.0, key='dc4')
        
        ca5, ca6, ca7 = ui.columns(3)
        dc_supr = ca5.number_input("Supra (mm)", 0.0, 100.0, 18.0, key='dc5')
        dc_abdo = ca6.number_input("Abdo (mm)", 0.0, 100.0, 20.0, key='dc6')
        dc_coxa = ca7.number_input("Coxa (mm)", 0.0, 100.0, 15.0, key='dc7')

        if ui.button("Calcular Gordura"):
            soma = dc_peit + dc_axil + dc_tric + dc_sube + dc_supr + dc_abdo + dc_coxa
            id_p = ui.session_state.get('idade_paciente', 25)
            if ui.session_state.get('sexo_paciente', 'M') == "M":
                dc = 1.112 - (0.00043499 * soma) + (0.00000055 * (soma**2)) - (0.00028826 * id_p)
            else:
                dc = 1.097 - (0.00046971 * soma) + (0.00000056 * (soma**2)) - (0.00012828 * id_p)
            
            bf = ((4.95 / dc) - 4.50) * 100
            p_w = ui.session_state.get('peso_paciente', 70.0)
            m_g = p_w * (bf / 100)
            m_m = p_w - m_g

            ui.session_state['bf'] = bf
            ui.session_state['m_m'] = m_m
            ui.session_state['m_g'] = m_g
            ui.session_state['antropo_calc'] = True

        if ui.session_state.get('antropo_calc', False):
            ui.markdown(f"""<div class='metric-card'>
            <h3>📊 Composição Corporal</h3>
            <p><b>BF:</b> {ui.session_state['bf']:.1f}%</p>
            <p><b>Massa Magra:</b> {ui.session_state['m_m']:.1f} kg</p>
            <p><b>Massa Gorda:</b> {ui.session_state['m_g']:.1f} kg</p>
            </div>""", unsafe_allow_html=True)

    with aba3:
        ui.header("🍳 Plano Alimentar")
        col_diet, col_sub = ui.columns(2)
        
        with col_diet:
            ui.subheader("Refeições")
            if 'calorias' in ui.session_state:
                ui.info(f"🎯 Meta: {ui.session_state['calorias']:.0f} kcal")
            
            ui.text_area("☕ Café da Manhã:", key='saved_cafe')
            ui.text_area("🍚 Almoço:", key='saved_almo')
            ui.text_area("🍏 Lanche:", key='saved_lanc')
            ui.text_area("🥗 Jantar:", key='saved_jant')

        with col_sub:
            ui.subheader("🔄 Substituições")
            opcao_sub = ui.selectbox("Trocar por:", ["Arroz Integral (100g)", "Batata Doce (120g)", "Mandioca (90g)", "Pão Integral (2 fat)"])
            ui.info(f"💡 Sugestão: Use **{opcao_sub}**.")

    with aba4:
        ui.header("📚 Banco de Dados")
        if os.path.exists(NOME_ARQUIVO):
            ui.dataframe(pd.read_csv(NOME_ARQUIVO), use_container_width=True)
            if ui.button("Apagar Histórico"):
                os.remove(NOME_ARQUIVO)
                ui.rerun()
        else:
            ui.info("Sem registros no arquivo CSV.")

    with aba5:
        ui.header("📚 Prontuário")
        p_ativo = ui.session_state.get('nome_paciente', '')
        
        if p_ativo != '':
            m_die = ui.session_state.get('calorias', 0)
            est_n = ui.session_state.get('estrategia', '')
            ag_pr = ui.session_state.get('agua', 0)
            ma_pr = ui.session_state.get('macros', '')
            
            c_f = ui.session_state.get('saved_cafe', 'Vazio')
            a_l = ui.session_state.get('saved_almo', 'Vazio')
            l_a = ui.session_state.get('saved_lanc', 'Vazio')
            j_a = ui.session_state.get('saved_jant', 'Vazio')
            
            txt = f"PACIENTE: {p_ativo}\nESTRATEGIA: {est_n}\nDIETA: {m_die:.0f} kcal\nMACROS: {ma_pr}\nAGUA: {ag_pr:.2f}L\n\nCARDAPIO:\nCafe: {c_f}\nAlmoco: {a_l}\nLanche: {l_a}\nJantar: {j_a}"
            ui.text_area("Texto:", txt, height=200)
            ui.download_button("📥 Baixar TXT", data=txt, file_name=f"WebDiet_{p_ativo}.txt")
        else:
            ui.info("Preencha o Nome na Aba 1.")
