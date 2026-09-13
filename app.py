import streamlit as ui
import csv
import os
import pandas as pd

# CONFIGURAÇÕES INICIAIS
NOME_ARQUIVO = 'consultas_nutricionais.csv'
ARQUIVO_CARDAPIOS = 'cardapios_pacientes.csv'
SENHA_CORRETA = "Mi81283137."

ui.set_page_config(page_title="Consultório Nutricional Pro", page_icon="🥑", layout="wide")
ui.title("🥑 Software de Nutrição Inteligente")

# --- TELA DE LOGIN ---
ui.subheader("🔒 Acesso Restrito ao Sistema")
senha_digitada = ui.text_input("Digite a senha da clínica:", type="password")

if senha_digitada != SENHA_CORRETA:
    if senha_digitada == "":
        ui.warning("Por favor, digite a senha acima para liberar o acesso.")
    else:
        ui.error("❌ Senha incorreta! Acesso negado.")
else:
    ui.success("🔑 Acesso Liberado com Sucesso!")
    ui.markdown("---")
    
    # Criando as 4 abas de navegação
    aba_cadastro, aba_cardapio, aba_historico, aba_pdf = ui.tabs([
        "📋 Nova Consulta", "🍳 Montar Cardápio", "📚 Histórico", "📄 Exportar"
    ])

    # --- ABA 1: NOVA CONSULTA ---
    with aba_cadastro:
        ui.header("Ficha de Anamnese & Avaliação")
        
        ui.subheader("👤 1. Dados Gerais")
        col1, col2, col3 = ui.columns(3)
        with col1: nome = ui.text_input("Nome Completo")
        with col2: idade = ui.number_input("Idade", min_value=1, max_value=120, value=25)
        with col3: sexo = ui.radio("Sexo Biológico", ["Masculino", "Feminino"], horizontal=True)

        ui.subheader("📊 2. Avaliação Física")
        col4, col5 = ui.columns(2)
        with col4: peso = ui.number_input("Peso (kg)", min_value=0.0, value=0.0, step=0.1, format="%.1f")
        with col5: altura = ui.number_input("Altura (m)", min_value=0.0, value=0.0, step=0.01, format="%.2f")

        ui.subheader("🏃‍♂️ 3. Estilo de Vida & Objetivos")
        objetivo = ui.selectbox("Qual o principal objetivo?", ["Emagrecimento", "Ganho de Massa Muscular (Hipertrofia)", "Melhora da Saúde"])
        atividade = ui.selectbox("Nível de atividade física:", ["Sedentário", "Levemente Ativo", "Moderadamente Ativo", "Altamente Ativo"])

        ui.subheader("🩺 4. Hábitos & Restrições")
        restricoes = ui.text_input("Restrições alimentares ou alergias")
        agua = ui.slider("Consumo diário de água atual (em Litros)", min_value=0.0, max_value=6.0, value=1.5, step=0.1)

        if ui.button("Finalizar e Salvar Consulta", type="primary"):
            if nome == "" or peso == 0.0 or altura == 0.0:
                ui.error("⚠️ Nome, Peso e Altura são obrigatórios!")
            else:
                # Cálculos Biológicos
                imc = peso / (altura ** 2)
                classificacao_imc = "Abaixo do peso" if imc < 18.5 else "Peso ideal" if imc < 25.0 else "Sobrepeso" if imc < 30.0 else "Obesidade"
                agua_ideal = (peso * 35) / 1000
                altura_cm = altura * 100
                
                # Gasto Energético (Harris-Benedict)
                if sexo == "Masculino":
                    geb = 66.5 + (13.75 * peso) + (5.003 * altura_cm) - (6.75 * idade)
                else:
                    geb = 655.1 + (9.563 * peso) + (1.85 * altura_cm) - (4.676 * idade)

                fator = 1.2 if "Sedentário" in atividade else 1.375 if "Levemente" in atividade else 1.55 if "Moderadamente" in atividade else 1.725
                gasto_total = geb * factor if 'factor' in locals() else geb * fator

                # Planejamento Dietético
                if objetivo == "Emagrecimento":
                    calorias_dieta, estrategia, g_proteina, g_lipidios = gasto_total - 500, "Dieta Hipocalórica", peso * 2.0, peso * 0.8
                elif "Hipertrofia" in objetivo:
                    calorias_dieta, estrategia, g_proteina, g_lipidios = gasto_total + 300, "Dieta Hipercalórica", peso * 2.2, peso * 1.0
                else:
                    calorias_dieta, estrategia, g_proteina, g_lipidios = gasto_total, "Dieta Normocalórica", peso * 1.5, peso * 0.9

                calorias_restantes = calorias_dieta - ((g_proteina * 4) + (g_lipidios * 9))
                g_carboidratos = max(0.0, calorias_restantes / 4)

                # Salvar na Sessão do App
                ui.session_state['nome_paciente'] = nome
                ui.session_state['calorias_meta'] = f"{calorias_dieta:.0f}"
                ui.session_state['agua_meta'] = f"{agua_ideal:.2f}"
                ui.session_state['macros_meta'] = f"P: {g_proteina:.1f}g | C: {g_carboidratos:.1f}g | G: {g_lipidios:.1f}g"

                # Mostrar Resultados na Tela
                ui.success(f"✅ Avaliação de {nome} concluída!")
                res1, res2, res3 = ui.columns(3)
                res1.metric("IMC Calculado", f"{imc:.2f}", classificacao_imc)
                res2.metric("Meta de Água", f"{agua_ideal:.2f} L")
                res3.metric("Gasto Energético", f"{gasto_total:.0f} kcal")
                
                # Salvar no Banco CSV
                arquivo_existe = os.path.exists(NOME_ARQUIVO)
                with open(NOME_ARQUIVO, mode='a', newline='', encoding='utf-8') as arquivo:
                    escritor = csv.writer(arquivo)
                    if not arquivo_existe:
                        escritor.writerow(["Nome", "Idade", "Sexo", "Peso", "Altura", "IMC", "Diagnostico", "Objetivo", "Calorias_Meta"])
                    escritor.writerow([nome, idade, sexo, peso, altura, f"{imc:.2f}", classificacao_imc, objetivo, f"{calorias_dieta:.0f}"])

    # --- ABA 2: MONTAR CARDÁPIO ---
    with aba_cardapio:
        ui.header("🍳 Prescrição do Plano Alimentar")
        p_atual = ui.session_state.get('nome_paciente', 'Paciente Não Selecionado')
        ui.subheader(f"Montando cardápio para: **{p_atual}**")
        
        if 'nome_paciente' in ui.session_state:
            ui.info(f"📈 **Metas Atuais:** {ui.session_state['calorias_meta']} kcal/dia | {ui.session_state['macros_meta']}")
        
        cafe = ui.text_area("☕ Café da Manhã:")
        almoco = ui.text_area("🍚 Almoço:")
        lanche = ui.text_area("🍏 Lanche da Tarde:")
        jantar = ui.text_area("🥗 Jantar:")
        
        if ui.button("Salvar Cardápio", type="primary"):
            if p_atual == 'Paciente Não Selecionado':
                ui.error("⚠️ Cadastre um paciente na Aba 1 antes de salvar.")
            else:
                arq_existe = os.path.exists(ARQUIVO_CARDAPIOS)
                with open(ARQUIVO_CARDAPIOS, mode='a', newline='', encoding='utf-8') as f:
                    escritor_c = csv.writer(f)
                    if not arq_existe:
                        escritor_c.writerow(["Paciente", "Cafe", "Almoco", "Lanche", "Jantar"])
                    escritor_c.writerow([p_atual, cafe, almoco, lanche, jantar])
                ui.success(f"💾 Cardápio de {p_atual} salvo!")

    # --- ABA 3: HISTÓRICO ---
    with aba_historico:
        ui.header("📚 Histórico de Consultas")
        if os.path.exists(NOME_ARQUIVO):
            df = pd.read_csv(NOME_ARQUIVO)
            ui.dataframe(df, use_container_width=True)
            if ui.button("Limpar Histórico"):
                os.remove(NOME_ARQUIVO)
                ui.rerun()
        else:
            ui.info("Nenhum registro encontrado.")

    # --- ABA 4: EXPORTAR ---
    with aba_pdf:
        ui.header("📄 Exportar Relatório")
        p_relatorio = ui.session_state.get('nome_paciente', None)
        
        if p_relatorio:
            texto = f"PACIENTE: {p_relatorio}\nMETA: {ui.session_state.get('calorias_meta')} kcal\nAGUA: {ui.session_state.get('agua_meta')}L\n\nCARDAPIO:\nCafe: {cafe}\nAlmoco: {almoco}\nLanche: {lanche}\nJantar: {jantar}"
            ui.text_area("Pré-visualização do documento:", texto, height=200)
            ui.download_button(label="📥 Baixar Plano (.txt)", data=texto, file_name=f"Plano_{p_relatorio}.txt", mime="text/plain")
        else:
            ui.warning("Cadastre um paciente na Aba 1 para gerar o relatório.")
