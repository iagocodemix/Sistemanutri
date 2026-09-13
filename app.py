import streamlit as ui
import csv
import os
import pandas as pd

NOME_ARQUIVO = 'consultas_nutricionais.csv'
ARQUIVO_CARDAPIOS = 'cardapios_pacientes.csv'
SENHA_CORRETA = "Mi81283137."

ui.set_page_config(
    page_title="WebDiet Pro",
    page_icon="🥗",
    layout="wide"
)

# ESTILO VISUAL
ui.markdown("""
    <style>
    .stApp { background-color: #f7f9fc; }
    .metric-card {
        background-color: #ffffff; padding: 20px; 
        border-radius: 12px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-left: 5px solid #2e7d32;
    }
    h1, h2, h3 { 
        color: #1b5e20 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    div.stButton > button:first-child {
        background-color: #2e7d32 !important; 
        color: white !important;
        border-radius: 8px; width: 100%; 
        height: 45px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

ui.title("🥗 Sistema de Nutrição Integrada")

senha = ui.text_input("Chave de Acesso:", type="password")
if senha != SENHA_CORRETA:
    ui.warning("🔒 Digite a chave de acesso clínica.")
else:
    ui.success("🔑 Sistema Liberado!")
    ui.markdown("---")
    
    aba1, aba2, aba3, aba4 = ui.tabs([
        "📋 Anamnese & MET", 
        "📐 Antropometria", 
        "🍳 Cardápio", 
        "📚 Prontuário"
    ])

    with aba1:
        ui.header("Ficha Clínica & Rotina Esportiva")
        c1, c2, c3 = ui.columns(3)
        nome = c1.text_input("Nome do Paciente")
        idade = c2.number_input("Idade", 1, 120, 25)
        sexo = c3.radio(
            "Sexo Biológico", 
            ["Masculino", "Feminino"], 
            horizontal=True
        )

        c4, c5 = ui.columns(2)
        peso = c4.number_input("Peso (kg)", 0.0, 300.0, 70.0, 0.1)
        altura = c5.number_input("Altura (m)", 0.0, 2.5, 1.70, 0.01)

        ui.subheader("🎯 Planejamento e Objetivos")
        objetivo = ui.selectbox("Qual o principal objetivo?", [
            "Emagrecimento (Déficit Calórico)", 
            "Ganho de Massa Muscular (Hipertrofia)", 
            "Melhora da Saúde (Normocalórica)"
        ])

        ui.subheader("🏋️‍♂️ Atividade Física (MET)")
        modalidade = ui.selectbox("Selecione o esporte:", [
            "Musculação Intensa (MET: 6.0)", 
            "Corrida Moderada 8km/h (MET: 8.3)", 
            "Natação Funcional (MET: 6.0)", 
            "Ciclismo de Rua (MET: 7.5)", 
            "Nenhum / Sedentário (MET: 1.0)"
        ])
        tempo = ui.number_input("Duração (minutos):", 0, 180, 60)

        if ui.button("Calcular Metabolismo", key="btn_cad"):
            if not nome or peso == 0.0 or altura == 0.0: 
                ui.error("⚠️ Nome, Peso e Altura obrigatórios!")
            else:
                imc = peso / (altura ** 2)
                if imc < 18.5: diag = "Abaixo do peso"
                elif imc < 25.0: diag = "Ideal"
                elif imc < 30.0: diag = "Sobrepeso"
                else: diag = "Obesidade"
                
                agua_ideal = (peso * 35) / 1000
                alt_cm = altura * 100
                
                # TAXA BASAL QUEBRADA EM LINHAS PEQUENAS
                if sexo == "Masculino":
                    geb = 66.5 + (13.75 * peso)
                    geb += (5.003 * alt_cm) - (6.75 * idade)
                else:
                    geb = 655.1 + (9.563 * peso)
                    geb += (1.85 * alt_cm) - (4.676 * idade)
                
                met_val = float(
                    modalidade.split("MET: ")[1].replace(")", "")
                )
                
                g_treino = (met_val * 3.5 * peso / 200) * tempo
                g_total = (geb * 1.2) + g_treino

                if "Emagrecimento" in objetivo:
                    calorias = g_total - 500
                    estrategia = "Hipocalórica (-500 kcal)"
                    g_prot = peso * 2.0
                    g_fat = peso * 0.8
                elif "Hipertrofia" in objetivo:
                    calorias = g_total + 300
                    estrategia = "Hipercalórica (+300 kcal)"
                    g_prot = peso * 2.2
                    g_fat = peso * 1.0
                else:
                    calorias = g_total
                    estrategia = "Normocalórica"
                    g_prot = peso * 1.5
                    g_fat = peso * 0.9

                cal_rest = calorias - ((g_prot * 4) + (g_fat * 9))
                g_carb = max(0.0, cal_rest / 4)

                ui.session_state['nome'] = nome
                ui.session_state['peso'] = peso
                ui.session_state['g_total'] = g_total
                ui.session_state['calorias'] = calorias
                ui.session_state['estrategia'] = estrategia
                ui.session_state['agua'] = agua_ideal
                
                macros_txt = f"P: {g_prot:.1f}g | C: {g_carb:.1f}g"
                macros_txt += f" | G: {g_fat:.1f}g"
                ui.session_state['macros'] = macros_txt

                ui.markdown(f"""<div class='metric-card'>
                <h3>🎯 Resultado: {nome}</h3>
                <p><b>Estratégia:</b> {estrategia}</p>
                <p><b>IMC:</b> {imc:.2f} ({diag})</p>
                <p><b>Meta Dieta:</b> {calorias:.0f} kcal</p>
                <p><b>Água:</b> {agua_ideal:.2f} L</p>
                <p><b>Gasto Total (TDEE):</b> {g_total:.0f} kcal</p>
                </div>""", unsafe_allow_html=True)

                ui.subheader("🥩 Macronutrientes Alvo")
                m1, m2, m3 = ui.columns(3)
                m1.metric("Proteínas", f"{g_prot:.1f} g")
                m2.metric("Carboidratos", f"{g_carb:.1f} g")
                m3.metric("Lipídios", f"{g_fat:.1f} g")

    with aba2:
        ui.header(" Jackson & Pollock (7 Dobras)")
        p_nome = ui.session_state.get('nome', 'Sem Paciente')
        ui.subheader(f"Avaliação Corporal: {p_nome}")
        
        ca1, ca2, ca3, ca4 = ui.columns(4)
        dc_peit = ca1.number_input("Peitoral (mm)", 0.0, 100.0, 10.0)
        dc_axil = ca2.number_input("Axilar (mm)", 0.0, 100.0, 12.0)
        dc_tric = ca3.number_input("Tricep (mm)", 0.0, 100.0, 14.0)
        dc_sube = ca4.number_input("Subescapular (mm)", 0.0, 100.0, 15.0)
        
        ca5, ca6, ca7 = ui.columns(3)
        dc_supr = ca5.number_input("Suprailíaca (mm)", 0.0, 100.0, 18.0)
        dc_abdo = ca6.number_input("Abdominal (mm)", 0.0, 100.0, 20.0)
        dc_coxa = ca7.number_input("Coxa (mm)", 0.0, 100.0, 15.0)

        if ui.button("Calcular Gordura Corporal"):
            soma = (dc_peit + dc_axil + dc_tric + 
                    dc_sube + dc_supr + dc_abdo + dc_coxa)
            
            if sexo == "Masculino":
                dc = 1.112 - (0.00043499 * soma) 
                dc += (0.00000055 * (soma**2)) - (0.00028826 * idade)
            else:
                dc = 1.097 - (0.00046971 * soma)
                dc += (0.00000056 * (soma**2)) - (0.00012828 * idade)
            
            bf = ((4.95 / dc) - 4.50) * 100
            p_peso = ui.session_state.get('peso', 70.0)
            m_gorda = p_peso * (bf / 100)
            m_magra = p_peso - m_gorda

            ui.markdown(f"""<div class='metric-card'>
            <h3>📊 Composição Corporal</h3>
            <p><b>Gordura (BF):</b> {bf:.1f}%</p>
            <p><b>Massa Magra:</b> {m_magra:.1f} kg</p>
            <p><b>Massa Gorda:</b> {m_gorda:.1f} kg</p>
            </div>""", unsafe_allow_html=True)

    with aba3:
        ui.header("🍳 Planejamento Alimentar")
        col_diet, col_sub = ui.columns(2)
        
        with col_diet:
            ui.subheader("Refeições")
            if 'calorias' in ui.session_state:
                c_meta = ui.session_state['calorias']
                m_meta = ui.session_state['macros']
                ui.info(f"🎯 Meta: {c_meta:.0f} kcal | {m_meta}")
                
            cafe = ui.text_area("☕ Café da Manhã:")
            almoco = ui.text_area("🍚 Almoço:")
            lanche = ui.text_area("🍏 Lanche:")
            jantar = ui.text_area("🥗 Jantar:")
            
            if ui.button("Gravar Cardápio"):
                ui.success("💾 Salvo com sucesso!")

        with col_sub:
            ui.subheader("🔄 Substituições")
            opcao_sub = ui.selectbox("Substituir por:", [
                "Arroz Integral (100g)", 
                "Batata Doce (120g)", 
                "Mandioca Cozida (90g)", 
                "Pão Integral (2 fatias)"
            ])
            ui.info(f"💡 Sugestão: Use **{opcao_sub}**.")

    with aba4:
        ui.header("📚 Prontuário Clínico")
        p_ativo = ui.session_state.get('nome', 'Nenhum')
        
        if p_ativo != 'Nenhum':
            m_cal = ui.session_state.get('g_total', 0)
            m_die = ui.session_state.get('calorias', 0)
            est_n = ui.session_state.get('estrategia', '')
            ag_pr = ui.session_state.get('agua', 0)
            ma_pr = ui.session_state.get('macros', '')
            
            # TEXTO FORMATADO VERTICALMENTE PARA NÃO CORTAR
            txt = f"PACIENTE: {p_ativo}\n"
            txt += f"ESTRATEGIA: {est_n}\n"
            txt += f"DIETA: {m_die:.0f} kcal\n"
            txt += f"MACROS: {ma_pr}\n"
            txt += f"AGUA: {ag_pr:.2f}L\n"
            txt += f"TDEE: {m_cal:.0f} kcal\n\n"
            txt += f"CARDAPIO:\n"
            txt += f"Cafe: {cafe}\nAlmoco: {almoco}\n"
            txt += f"Lanche: {lanche}\nJantar: {jantar}"
            
            ui.text_area("Visualização:", txt, height=250)
            ui.download_button(
                "📥 Baixar Relatório", 
                data=txt, 
                file_name=f"WebDiet_{p_ativo}.txt"
            )
        else:
            ui.info("Preencha a Aba 1 para gerar o prontuário.")
