import streamlit as ui
import csv
import os
import pandas as pd

nome_arquivo = 'consultas_nutricionais.csv'

# Configuração da página web
ui.set_page_config(page_title="Consultório Nutricional Pro", page_icon="🥑", layout="wide")

ui.title("🥑 Software de Nutrição Inteligente")

# --- NOVO: SISTEMA DE SEGURANÇA (TELA DE LOGIN) ---
# Definimos a senha de acesso aqui (mude se quiser)
SENHA_CORRETA = "Mi81283137."

# Criamos um campo de texto especial para senha no menu lateral ou no topo
ui.sidebar.subheader("🔒 Acesso Restrito")
senha_digitada = ui.sidebar.text_input("Digite a senha para acessar o sistema:", type="password")

# O sistema só roda se a senha estiver correta
if senha_digitada != SENHA_CORRETA:
    if senha_digitada == "":
        ui.warning("Please enter your password in the sidebar to access the clinic's systems. / Por favor, insira a senha na barra lateral para acessar o sistema da clínica.")
    else:
        ui.error("❌ Senha incorreta! Acesso negado.")
else:
    # --- TODO O RESTANTE DO SEU CÓDIGO FICA PROTEGIDO AQUI DENTRO ---
    ui.sidebar.success("🔑 Acesso Liberado!")
    
    # Criando as abas de navegação no topo do sistema
    aba_cadastro, aba_historico = ui.tabs(["📋 Nova Consulta", "📚 Histórico de Pacientes"])

    # --- ABA 1: NOVA CONSULTA ---
    with aba_cadastro:
        ui.header("Ficha de Anamnese & Avaliação")
        
        ui.subheader("👤 1. Dados Gerais")
        col1, col2, col3 = ui.columns(3)
        with col1:
            nome = ui.text_input("Nome Completo")
        with col2:
            idade = ui.number_input("Idade", min_value=1, max_value=120, value=25)
        with col3:
            sexo = ui.radio("Sexo Biológico", ["Masculino", "Feminino"], horizontal=True)

        ui.subheader("📊 2. Avaliação Física")
        col4, col5 = ui.columns(2)
        with col4:
            peso = ui.number_input("Peso Atual (kg)", min_value=0.0, value=0.0, step=0.1, format="%.1f")
        with col5:
            altura = ui.number_input("Altura (metros)", min_value=0.0, value=0.0, step=0.01, format="%.2f")

        ui.subheader("🏃‍♂️ 3. Estilo de Vida & Objetivos")
        objetivo = ui.selectbox("Qual o principal objetivo?", ["Emagrecimento", "Ganho de Massa Muscular (Hipertrofia)", "Melhora da Saúde / Qualidade de Vida"])
        atividade = ui.selectbox("Nível de atividade física diária:", [
            "Sedentário (Pouco ou nenhum exercício)", 
            "Levemente Ativo (Exercício leve 1-3 dias/semana)", 
            "Moderadamente Ativo (Exercício moderado 3-5 dias/semana)", 
            "Altamente Ativo (Exercício pesado 6-7 dias/semana)"
        ])

        ui.subheader("🩺 4. Hábitos & Restrições")
        restricoes = ui.text_input("Restrições alimentares ou alergias")
        agua = ui.slider("Consumo diário de água atual (em Litros)", min_value=0.0, max_value=6.0, value=1.5, step=0.1)

        if ui.button("Finalizar e Salvar Consulta", type="primary"):
            if nome == "" or peso == 0.0 or altura == 0.0:
                ui.error("⚠️ Nome, Peso e Altura são obrigatórios!")
            else:
                imc = peso / (altura * altura)
                if imc < 18.5: classificacao_imc = "Abaixo do peso"
                elif imc < 25.0: classificacao_imc = "Peso ideal"
                elif imc < 30.0: classificacao_imc = "Sobrepeso"
                else: classificacao_imc = "Obesidade"

                agua_ideal = (peso * 35) / 1000

                altura_cm = altura * 100
                if sexo == "Masculino":
                    geb = 66.5 + (13.75 * peso) + (5.003 * altura_cm) - (6.75 * idade)
                else:
                    geb = 655.1 + (9.563 * peso) + (1.85 * altura_cm) - (4.676 * idade)

                if "Sedentário" in atividade: fator = 1.2
                elif "Levemente" in atividade: fator = 1.375
                elif "Moderadamente" in atividade: fator = 1.55
                else: fator = 1.725
                
                gasto_total = geb * fator

                if objetivo == "Emagrecimento":
                    calorias_dieta = gasto_total - 500
                    estrategia = "Dieta Hipocalórica"
                    g_proteina = peso * 2.0
                    g_lipidios = peso * 0.8
                elif "Hipertrofia" in objetivo:
                    calorias_dieta = gasto_total + 300
                    estrategia = "Dieta Hipercalórica"
                    g_proteina = peso * 2.2
                    g_lipidios = peso * 1.0
                else:
                    calorias_dieta = gasto_total
                    estrategia = "Dieta Normocalórica"
                    g_proteina = peso * 1.5
                    g_lipidios = peso * 0.9

                calorias_proteina = g_proteina * 4
                calorias_lipidios = g_lipidios * 9
                calorias_restantes = calorias_dieta - (calorias_proteina + calorias_lipidios)
                g_carboidratos = max(0.0, calorias_restantes / 4)

                ui.success(f"✅ Avaliação de {nome} concluída!")
                
                res1, res2, res3 = ui.columns(3)
                with res1:
                    ui.metric("IMC Calculado", f"{imc:.2f}", classificacao_imc)
                with res2:
                    ui.metric("Meta Diária de Água", f"{agua_ideal:.2f} L")
                with res3:
                    ui.metric("Gasto Energético Total", f"{gasto_total:.0f} kcal")
                
                ui.info(f"🎯 **Meta para Dieta:** Recomendado consumir aproximadamente **{calorias_dieta:.0f} kcal/dia** para a estratégia de **{estrategia}**.")

                ui.subheader("🥩 Distribuição de Macronutrientes")
                m1, m2, m3 = ui.columns(3)
                with m1:
                    ui.metric("Proteínas", f"{g_proteina:.1f} g", f"{g_proteina * 4:.0f} kcal")
                with m2:
                    ui.metric("Carboidratos", f"{g_carboidratos:.1f} g", f"{g_carboidratos * 4:.0f} kcal")
                with m3:
                    ui.metric("Lipídios (Gorduras)", f"{g_lipidios:.1f} g", f"{g_lipidios * 9:.0f} kcal")

                arquivo_existe = os.path.exists(nome_arquivo)
                with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as arquivo:
                    escritor = csv.writer(arquivo)
                    if not arquivo_existe:
                        escritor.writerow([
                            "Nome", "Idade", "Sexo", "Peso", "Altura", "IMC", "Diagnostico", 
                            "Objetivo", "Atividade", "Restricoes", "Agua_Atual", "Agua_Ideal", 
                            "Gasto_Calorico", "Calorias_Meta", "Proteinas_g", "Carboidratos_g", "Lipidios_g"
                        ])
                    
                    escritor.writerow([
                        nome, idade, sexo, peso, altura, f"{imc:.2f}", classificacao_imc, 
                        objetivo, atividade, restricoes, agua, f"{agua_ideal:.2f}", 
                        f"{gasto_total:.0f}", f"{calorias_dieta:.0f}", f"{g_proteina:.1f}", f"{g_carboidratos:.1f}", f"{g_lipidios:.1f}"
                    ])

    # --- ABA 2: HISTÓRICO DE PACIENTES ---
    with aba_historico:
        ui.header("📚 Prontuários e Histórico de Consultas")
        
        if os.path.exists(nome_arquivo):
            dados = pd.read_csv(nome_arquivo)
            
            busca = ui.text_input("🔍 Buscar paciente pelo nome:")
            if busca:
                dados = dados[dados['Nome'].str.contains(busca, case=False, na=False)]
                
            ui.dataframe(dados, use_container_width=True)
            
            ui.subheader("📊 Estatísticas do Consultório")
            col_est1, col_est2 = ui.columns(2)
            
            with col_est1:
                ui.write(f"Total de consultas gravadas: **{len(dados)}**")
                contagem_diagnosticos = dados['Diagnostico'].value_counts()
                ui.write("**Distribuição de Pacientes por Categoria de IMC:**")
                ui.bar_chart(contagem_diagnosticos)
                
            with col_est2:
                contagem_objetivos = dados['Objetivo'].value_counts()
                ui.write("**Distribuição por Objetivo Clínico:**")
                ui.bar_chart(contagem_objetivos)
        else:
            ui.info("Nenhum paciente cadastrado no histórico ainda. Faça a primeira consulta na aba ao lado!")
