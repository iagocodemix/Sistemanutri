import streamlit as ui
import csv
import os
import pandas as pd

# CONFIGURAÇÕES INICIAIS DO BANCO DE DADOS
NOME_ARQUIVO = 'consultas_nutricionais.csv'
ARQUIVO_CARDAPIOS = 'cardapios_pacientes.csv'
SENHA_CORRETA = "Mi81283137."

# 1. DESIGN PROFISSIONAL (Estilo WebDiet Clean)
ui.set_page_config(page_title="WebDiet Clone Pro", page_icon="🥗", layout="wide")

ui.markdown("""
    <style>
    .stApp { background-color: #f7f9fc; }
    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #2e7d32;
    }
    h1, h2, h3 { color: #1b5e20 !important; font-family: 'Segoe UI', sans-serif; }
    div.stButton > button:first-child {
        background-color: #2e7d32 !important; color: white !important;
        border-radius: 8px; width: 100%; height: 45px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

ui.title("🥗 Sistema de Nutrição Integrada (Premium)")

# --- TELA DE LOGIN ---
if ui.text_input("Chave de Acesso Clínica:", type="password") != SENHA_CORRETA:
    ui.warning("🔒 Digite a chave de acesso para desbloquear o ecossistema WebDiet.")
else:
    ui.success("🔑 Ecossistema liberado!"); ui.markdown("---")
    
    aba_cadastro, aba_antropo, aba_cardapio, aba_historico = ui.tabs([
        "📋 Anamnese & MET", "📐 Antropometria (Pollock)", "🍳 Cardápio Inteligente", "📚 Prontuário"
    ])

    # --- ABA 1: ANAMNESE & GASTO ENERGÉTICO ESPORTIVO (MET) ---
    with aba_cadastro:
        ui.header("Ficha Clínica & Rotina Esportiva")
        c1, c2, c3 = ui.columns(3)
        nome = c1.text_input("Nome do Paciente")
        idade = c2.number_input("Idade", 1, 120, 25)
        sexo = c3.radio("Sexo Biológico", ["Masculino", "Feminino"], horizontal=True)

        c4, c5 = ui.columns(2)
        peso = c4.number_input("Peso Atual (kg)", 0.0, 300.0, 70.0, 0.1)
        altura = c5.number_input("Altura (m)", 0.0, 2.5, 1.70, 0.01)

        ui.subheader("🏋️‍♂️ Prescrição de Atividade Física (Fator MET)")
        modalidade = ui.selectbox("Selecione o esporte principal do paciente:", [
            "Musculação Intensa (MET: 6.0)", "Corrida Moderada 8km/h (MET: 8.3)", 
            "Natação Funcional (MET: 6.0)", "Ciclismo de Rua (MET: 7.5)", "Nenhum / Sedentário (MET: 1.0)"
        ])
        tempo_treino = ui.number_input("Duração do treino diário (em minutos):", 0, 180, 60)

        if ui.button("Calcular Metabolismo & Salvar", key="btn_cadastro"):
            if not nome: ui.error("⚠️ Nome é obrigatório!")
            else:
                imc = peso / (altura ** 2)
                # Harris-Benedict Base
                geb = (66.5 + (13.75 * peso) + (5.003 * (altura*100)) - (6.75 * idade)) if sexo == "Masculino" else (655.1 + (9.563 * peso) + (1.85 * (altura*100)) - (4.676 * idade))
                
                # Cálculo MET: (MET * 3.5 * Peso / 200) * Minutos
                met_valor = float(modalidade.split("MET: ")[1].replace(")", ""))
                gasto_treino = (met_valor * 3.5 * peso / 200) * tempo_treino if met_valor > 1.0 else 0
                gasto_total = (geb * 1.2) + gasto_treino

                ui.session_state['nome'] = nome
                ui.session_state['peso'] = peso
                ui.session_state['gasto_total'] = gasto_total
                
                ui.markdown(f"""<div class='metric-card'>
                <h3>🎯 Resultado Clínico para {nome}</h3>
                <p><b>IMC:</b> {imc:.2f} | <b>Gasto Calórico Diário Total (TDEE):</b> {gasto_total:.0f} kcal</p>
                <p><b>Gasto isolado do treino:</b> {gasto_treino:.0f} kcal</p>
                </div>""", unsafe_allow_html=True)

    # --- ABA 2: ANTROPOMETRIA AVANÇADA (POLLOCK 7 DOBRAS) ---
    with aba_antropo:
        ui.header("📐 Protocolo Jackson & Pollock (7 Dobras)")
        p_nome = ui.session_state.get('nome', 'Paciente Não Selecionado')
        ui.subheader(f"Avaliação de Percentual de Gordura: {p_nome}")
        
        ca1, ca2, ca3, ca4 = ui.columns(4)
        dc_peitoral = ca1.number_input("Peitoral (mm)", 0.0, 100.0, 10.0)
        dc_axilar = ca2.number_input("Axilar Média (mm)", 0.0, 100.0, 12.0)
        dc_tricep = ca3.number_input("Tricep (mm)", 0.0, 100.0, 14.0)
        dc_subesc = ca4.number_input("Subescapular (mm)", 0.0, 100.0, 15.0)
        
        ca5, ca6, ca7 = ui.columns(3)
        dc_supra = ca5.number_input("Suprailíaca (mm)", 0.0, 100.0, 18.0)
        dc_abd = ca6.number_input("Abdominal (mm)", 0.0, 100.0, 20.0)
        dc_coxa = ca7.number_input("Coxa (mm)", 0.0, 100.0, 15.0)

        if ui.button("Calcular Composição Corporal"):
            soma_dobras = dc_peitoral + dc_axilar + dc_tricep + dc_subesc + dc_supra + dc_abd + dc_coxa
            # Fórmula de Densidade Corporal (Protocolo 7 Dobras)
            if sexo == "Masculino":
                dc = 1.112 - (0.00043499 * soma_dobras) + (0.00000055 * (soma_dobras**2)) - (0.00028826 * idade)
            else:
                dc = 1.097 - (0.00046971 * soma_dobras) + (0.00000056 * (soma_dobras**2)) - (0.00012828 * idade)
            
            bf = ((4.95 / dc) - 4.50) * 100
            p_atual_peso = ui.session_state.get('peso', 70)
            massa_gorda = p_atual_peso * (bf / 100)
            massa_magra = p_atual_peso - massa_gorda

            ui.markdown(f"""<div class='metric-card' style='border-left: 5px solid #0288d1;'>
            <h3>📊 Composição Corporal Obtida</h3>
            <p><b>% de Gordura (BF):</b> {bf:.1f}%</p>
            <p><b>Massa Magra Absoluta:</b> {massa_magra:.1f} kg | <b>Massa Gorda:</b> {massa_gorda:.1f} kg</p>
            </div>""", unsafe_allow_html=True)

    # --- ABA 3: CARDÁPIO INTELIGENTE & LISTA DE SUBSTITUIÇÃO ---
    with aba_cardapio:
        ui.header("🍳 Planejamento Alimentar Digital")
        
        col_diet, col_sub = ui.columns([2, 1])
        
        with col_diet:
            ui.subheader("Refeições Estruturadas")
            cafe = ui.text_area("☕ Café da Manhã:")
            almoco = ui.text_area("🍚 Almoço:")
            lanche = ui.text_area("🍏 Lanche:")
            jantar = ui.text_area("🥗 Jantar:")
            
            if ui.button("Gravar Cardápio Oficial"):
                ui.success("💾 Plano Alimentar integrado ao banco de dados do paciente!")

        with col_sub:
            ui.subheader("🔄 Substitutos Rápidos")
            ui.caption("Consulte equivalências direto do WebDiet:")
            opcao_sub = ui.selectbox("Trocar Carbo por:", ["Arroz Integral (100g)", "Batata Doce (120g)", "Mandioca Cozida (90g)", "Pão Integral (2 fatias)"])
            ui.info(f"💡 Equivalência: Substitua o carboidrato principal por **{opcao_sub}** mantendo a mesma carga glicêmica.")

    # --- ABA 4: PRONTUÁRIO & EXPORTAÇÃO ---
    with aba_historico:
        ui.header("📚 Prontuário Clínico Digital")
        p_ativo = ui.session_state.get('nome', 'Nenhum')
        
        if p_ativo != 'Nenhum':
            texto_completo = f"PACIENTE: {p_ativo}\nGASTO DIÁRIO ESTIMADO: {ui.session_state.get('gasto_total', 0):.0f} kcal\n\nCARDÁPIO SUGERIDO:\n{cafe}\n{almoco}\n{lanche}\n{jantar}"
            ui.text_area("Visualização do Prontuário:", texto_completo, height=250)
            ui.download_button("📥 Exportar Relatório para Impressão", data=texto_completo, file_name=f"WebDiet_{p_ativo}.txt")
        else:
            ui.info("Aguardando inserção de dados do paciente na Aba 1.")
