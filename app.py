import streamlit as ui
import csv
import os
import pandas as pd

ARQ = 'consultas_nutricionais.csv'
SENHA = "Mi81283137."

ui.set_page_config(
    page_title="WebDiet",
    page_icon="🥗",
    layout="wide"
)

# DESIGN PROFISSIONAL COMPACTO
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

pass_in = ui.text_input("Chave:", type="password")
if pass_in != SENHA:
    ui.warning("🔒 Chave clínica requerida.")
else:
    ui.success("🔑 Liberado!")
    
    t1, t2, t3, t4, t5 = ui.tabs([
        "📋 Anamnese & MET", "📐 Antropometria", 
        "🍳 Cardápio", "📚 Histórico", "📄 Prontuário"
    ])
    with t1:
        ui.header("Ficha Clínica")
        c1, c2, c3 = ui.columns(3)
        nome = c1.text_input("Nome", key='n_p')
        idade = c2.number_input("Idade", 1, 120, 25, key='i_p')
        sexo = c3.radio("Sexo", ["M", "F"], horizontal=True, key='s_p')

        c4, c5 = ui.columns(2)
        peso = c4.number_input("Peso (kg)", 0.0, 300.0, 70.0, 0.1, key='p_p')
        alt = c5.number_input("Alt (m)", 0.0, 2.5, 1.70, 0.01, key='a_p')

        obj = ui.selectbox("Objetivo:", [
            "Emagrecimento (Déficit Calórico)", 
            "Ganho de Massa Muscular (Hipertrofia)", 
            "Melhora da Saúde (Normocalórica)"
        ], key='o_p')

        mod = ui.selectbox("Esporte (MET):", [
            "Musculação Intensa (MET: 6.0)", 
            "Corrida Moderada 8km/h (MET: 8.3)", 
            "Natação Funcional (MET: 6.0)", 
            "Ciclismo de Rua (MET: 7.5)", 
            "Nenhum / Sedentário (MET: 1.0)"
        ], key='m_p')
        tempo = ui.number_input("Tempo (min):", 0, 180, 60, key='t_p')

        if ui.button("Calcular", key="btn_cad"):
            if not nome or peso == 0.0 or alt == 0.0: 
                ui.error("⚠️ Dados obrigatórios!")
            else:
                imc = peso / (alt ** 2)
                agua = (peso * 35) / 1000
                alt_cm = alt * 100
                
                if sexo == "M":
                    geb = 66.5 + (13.75 * peso) + (5.003 * alt_cm) - (6.75 * idade)
                else:
                    geb = 655.1 + (9.563 * peso) + (1.85 * alt_cm) - (4.676 * idade)
                
                # CÁLCULO SEGURO DO MET TRATANDO A STRING CORRETAMENTE
                partes = mod.split("MET: ")
                val_met = float(partes[1].replace(")", ""))
                g_treino = (val_met * 3.5 * peso / 200) * tempo
                g_total = (geb * 1.2) + g_treino

                if "Emagrecimento" in obj:
                    kc, est, gp, gf = g_total - 500, "Hipocalórica", peso * 2.0, peso * 0.8
                elif "Hipertrofia" in obj:
                    kc, est, gp, gf = g_total + 300, "Hipercalórica", peso * 2.2, peso * 1.0
                else:
                    kc, est, gp, gf = g_total, "Normocalórica", peso * 1.5, peso * 0.9

                gc = max(0.0, (kc - ((gp * 4) + (gf * 9))) / 4)

                ui.session_state['g_total'] = g_total
                ui.session_state['calorias'] = kc
                ui.session_state['estrategia'] = est
                ui.session_state['agua'] = agua
                ui.session_state['gp'] = gp
                ui.session_state['gc'] = gc
                ui.session_state['gf'] = gf
                ui.session_state['calc'] = True

                existe = os.path.exists(ARQ)
                with open(ARQ, mode='a', newline='', encoding='utf-8') as f:
                    esc = csv.writer(f)
                    if not existe:
                        esc.writerow(["Nome", "Idade", "Sexo", "Peso", "Alt", "Obj", "Est", "Kcal", "Agua"])
                    esc.writerow([nome, idade, sexo, peso, alt, obj, est, f"{kc:.0f}", f"{agua:.2f}"])
                ui.success("💾 Salvo no histórico!")

        if ui.session_state.get('calc', False) and ui.session_state.get('n_p', ''):
            ui.markdown(f"""<div class='metric-card'>
            <h3>🎯 Resultado</h3>
            <p><b>Paciente:</b> {ui.session_state['n_p']}</p>
            <p><b>Estratégia:</b> {ui.session_state['estrategia']}</p>
            <p><b>Meta Dieta:</b> {ui.session_state['calorias']:.0f} kcal</p>
            <p><b>Água Recomendada:</b> {ui.session_state['agua']:.2f} L</p>
            <p><b>Gasto Calórico Total:</b> {ui.session_state['g_total']:.0f} kcal</p>
            </div>""", unsafe_allow_html=True)

            ui.subheader("🥩 Macronutrientes Calculados")
            m1, m2, m3 = ui.columns(3)
            m1.metric("Proteínas", f"{ui.session_state['gp']:.1f} g")
            m2.metric("Carboidratos", f"{ui.session_state['gc']:.1f} g")
            m3.metric("Lipídios", f"{ui.session_state['gf']:.1f} g")
    with t2:
        ui.header("Jackson & Pollock (7 Dobras)")
        ui.subheader(f"Paciente: {ui.session_state.get('n_p', 'Nenhum')}")
        
        ca1, ca2, ca3, ca4 = ui.columns(4)
        dc1 = ca1.number_input("Peitoral (mm)", 0.0, 100.0, 10.0, key='d1')
        dc2 = ca2.number_input("Axilar (mm)", 0.0, 100.0, 12.0, key='d2')
        dc3 = ca3.number_input("Tricep (mm)", 0.0, 100.0, 14.0, key='d3')
        dc4 = ca4.number_input("Subesc (mm)", 0.0, 100.0, 15.0, key='d4')
        
        ca5, ca6, ca7 = ui.columns(3)
        dc5 = ca5.number_input("Supra (mm)", 0.0, 100.0, 18.0, key='d5')
        dc6 = ca6.number_input("Abdo (mm)", 0.0, 100.0, 20.0, key='d6')
        dc7 = ca7.number_input("Coxa (mm)", 0.0, 100.0, 15.0, key='d7')

        if ui.button("Calcular Gordura"):
            soma = dc1 + dc2 + dc3 + dc4 + dc5 + dc6 + dc7
            id_p = ui.session_state.get('i_p', 25)
            if ui.session_state.get('s_p', 'M') == "M":
                dc = 1.112 - (0.00043499 * soma) + (0.00000055 * (soma**2)) - (0.00028826 * id_p)
            else:
                dc = 1.097 - (0.00046971 * soma) + (0.00000056 * (soma**2)) - (0.00012828 * id_p)
            
            bf = ((4.95 / dc) - 4.50) * 100
            p_w = ui.session_state.get('p_p', 70.0)
            m_g = p_w * (bf / 100)
            m_m = p_w - m_g

            ui.session_state['bf'] = bf
            ui.session_state['m_m'] = m_m
            ui.session_state['m_g'] = m_g
            ui.session_state['ant'] = True

        if ui.session_state.get('ant', False):
            ui.markdown(f"""<div class='metric-card'>
            <h3>📊 Composição Corporal</h3>
            <p><b>BF:</b> {ui.session_state['bf']:.1f}%</p>
            <p><b>Massa Magra:</b> {ui.session_state['m_m']:.1f} kg</p>
            <p><b>Massa Gorda:</b> {ui.session_state['m_g']:.1f} kg</p>
            </div>""", unsafe_allow_html=True)

    with t3:
        ui.header("🍳 Plano Alimentar & Modelos")
        col_diet, col_sub = ui.columns(2)
        
        with col_diet:
            ui.subheader("Refeições")
            if ui.session_state.get('calc', False):
                ui.info(f"🎯 Meta: {ui.session_state['calorias']:.0f} kcal")
            
            ui.text_area("☕ Café da Manhã:", key='sv_cafe')
            ui.text_area("🍚 Almoço:", key='sv_almo')
            ui.text_area("🍏 Lanche:", key='sv_lanc')
            ui.text_area("🥗 Jantar:", key='sv_jant')

        with col_sub:
            ui.subheader("📚 Biblioteca de Modelos")
            modelo = ui.selectbox("Escolha um Protocolo:", [
                "Nenhum", "Idosos (Perda de Peso)", 
                "Diabéticos (Controle)", "Hipertrofia Padrão",
                "Vegetariano/Vegano", "Gestante Padrão",
                "Hipertensão (DASH)", "Low Carb Estruturado"
            ])
            
            if ui.button("Injetar Modelo"):
                if "Idosos" in modelo:
                    ui.session_state['sv_cafe'] = "Omelete (2 ovos) + Aveia + Mamão com chia."
                    ui.session_state['sv_almo'] = "Frango grelhado + Arroz integral + Purê + Brócolis."
                    ui.session_state['sv_lanc'] = "Iogurte natural desnatado + 3 castanhas."
                    ui.session_state['sv_jant'] = "Sopa caseira de legumes com carne magra."
                elif "Diabetes" in modelo:
                    ui.session_state['sv_cafe'] = "Pão integral centeio + Queijo branco + Café sem açúcar."
                    ui.session_state['sv_almo'] = "Peixe assado + Mix folhas verdes + Lentilha."
                    ui.session_state['sv_lanc'] = "Abacate amassado com sementes de girassol."
                    ui.session_state['sv_jant'] = "Omelete de espinafre + Salada de tomate."
                elif "Hipertrofia" in modelo:
                    ui.session_state['sv_cafe'] = "4 ovos + 2 fatias de pão integral + Vitamina de banana."
                    ui.session_state['sv_almo'] = "Arroz branco (250g) + Feijão + Patinho moído (150g)."
                    ui.session_state['sv_lanc'] = "Whey protein + 50g farelo aveia + 1 maçã."
                    ui.session_state['sv_jant'] = "Macarrão + Frango desfiado (150g) + Molho natural."
                elif "Vegetariano" in modelo:
                    ui.session_state['sv_cafe'] = "Tofu mexido com cúrcuma + Torrada integral + Suco verde."
                    ui.session_state['sv_almo'] = "Arroz integral + Feijão preto + Hambúrguer de grão-de-bico."
                    ui.session_state['sv_lanc'] = "Mix de sementes (abóbora e girassol) + Frutas vermelhas."
                    ui.session_state['sv_jant'] = "Creme de ervilha com cubos de tofu grelhado."
                elif "Gestante" in modelo:
                    ui.session_state['sv_cafe'] = "Iogurte natural batido com morango + Aveia + 1 ovo cozido."
                    ui.session_state['sv_almo'] = "Alcatra magra + Arroz + Feijão + Espinafre cozido."
                    ui.session_state['sv_lanc'] = "1 banana prata com 1 colher de sopa de semente de linhaça."
                    ui.session_state['sv_jant'] = "Filé de salmão grelhado + Batata inglesa assada com casca."
                elif "Hipertensão" in modelo:
                    ui.session_state['sv_cafe'] = "Mingau de aveia com leite desnatado e rodelas de banana."
                    ui.session_state['sv_almo'] = "Peito de frango com ervas + Arroz integral + Alface."
                    ui.session_state['sv_lanc'] = "Uma porção de melão picado + Amêndoas sem sal."
                    ui.session_state['sv_jant'] = "Filé de pescada ao forno com tomate e cebola."
                elif "Low Carb" in modelo:
                    ui.session_state['sv_cafe'] = "Ovos mexidos na manteiga e fatias de abacate."
                    ui.session_state['sv_almo'] = "Contrafilé grelhado + Espaguete de abobrinha ao pesto."
                    ui.session_state['sv_lanc'] = "Lascas de coco seco + Mix de castanhas."
                    ui.session_state['sv_jant'] = "Frango assado + Salada de rúcula com queijo parmesão."
                ui.success("⚡ Modelo aplicado com sucesso!")
                ui.rerun()

    with t4:
        ui.header("📚 Banco de Dados")
        if os.path.exists(ARQ):
            ui.dataframe(pd.read_csv(ARQ), use_container_width=True)
            if ui.button("Apagar Histórico"):
                os.remove(ARQ)
                ui.rerun()
        else:
            ui.info("Sem registros no arquivo CSV.")

    with t5:
        ui.header("📚 Prontuário")
        p_ativo = ui.session_state.get('n_p', '')
        
        if p_ativo != '':
            m_die = ui.session_state.get('calorias', 0)
            est_n = ui.session_state.get('estrategia', '')
            ag_pr = ui.session_state.get('agua', 0)
            gp_p = ui.session_state.get('gp', 0)
            gc_p = ui.session_state.get('gc', 0)
            gf_p = ui.session_state.get('gf', 0)
            
            c_f = ui.session_state.get('sv_cafe', 'Vazio')
            a_l = ui.session_state.get('sv_almo', 'Vazio')
            l_a = ui.session_state.get('sv_lanc', 'Vazio')
            j_a = ui.session_state.get('sv_jant', 'Vazio')
            
            txt = f"PACIENTE: {p_ativo}\nESTRATEGIA: {est_n}\n"
            txt += f"DIETA: {m_die:.0f} kcal\n"
            txt += f"MACROS: P:{gp_p:.1f}g | C:{gc_p:.1f}g | G:{gf_p:.1f}g\n"
            txt += f"AGUA: {ag_pr:.2f}L\n\nCARDAPIO:\n"
            txt += f"Cafe: {c_f}\nAlmoco: {a_l}\n"
            txt += f"Lanche: {l_a}\nJantar: {j_a}"
            
            ui.text_area("Texto:", txt, height=200)
            ui.download_button("📥 Baixar TXT", data=txt, file_name=f"WebDiet_{p_ativo}.txt")
        else:
            ui.info("Preencha o Nome na Aba 1.")
