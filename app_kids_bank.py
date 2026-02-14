import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO VISUAL & CSS (RipariBank Infinity Design) ---
st.set_page_config(page_title="RipariBank", page_icon="💳", layout="centered")

# CSS AVANÇADO: Transformando Streamlit em App Nativo
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo geral */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Container de Login e Cards */
    .css-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* O "Cartão de Crédito" Virtual */
    .credit-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        box-shadow: 0 10px 20px rgba(118, 75, 162, 0.4);
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .credit-card h3 {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }
    .credit-card h1 {
        color: white;
        font-size: 2.5rem;
        margin: 10px 0;
        font-weight: 800;
    }
    .credit-card .logo {
        position: absolute;
        top: 20px;
        right: 25px;
        font-size: 2rem;
        opacity: 0.5;
    }

    /* Botões Premium */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        font-weight: 700;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Botão Primário (Ação) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        box-shadow: 0 4px 15px rgba(24, 40, 72, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }

    /* Inputs Estilizados */
    .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 10px 15px;
        border: 1px solid #e0e0e0;
    }
    .stTextInput>div>div>input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.2);
    }

    /* Ajuste de Métricas e Tabelas */
    div[data-testid="stDataFrame"] {
        background: white;
        padding: 10px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (CONEXÃO DIRETA) ---
DB_FILE = 'kids_bank.db'

def run_query(query, params=(), commit=False):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute(query, params)
        if commit:
            conn.commit()
            return True
        else:
            return c.fetchall()
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return None
    finally:
        conn.close()

def init_db():
    run_query('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''', commit=True)
    
    users = run_query("SELECT count(*) FROM users WHERE name = 'daniel.ripari'")
    if users and users[0][0] == 0:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        initial_users = [
            ('daniel.ripari', 'admin', '1234'),
            ('ligia.ripari', 'admin', '1234'),
            ('murilo.ripari', 'user', 'kids1'),
            ('cecilia.ripari', 'user', 'kids2')
        ]
        c.executemany("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", initial_users)
        conn.commit()
        conn.close()

init_db()

# --- 3. VARIÁVEIS DE SESSÃO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. TELA DE LOGIN (DESIGN "GLASS") ---
if not st.session_state.logged_in:
    col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])
    
    with col_main:
        st.markdown("###") # Espaço topo
        
        # Container Visual de Login
        st.markdown("""
        <div class="css-card" style="text-align: center;">
            <div style="font-size: 4rem;">🏦</div>
            <h1 style="color: #333; margin-bottom: 0;">RipariBank</h1>
            <p style="color: #888; letter-spacing: 2px; font-size: 0.8rem; margin-top: 0;">INFINITY EDITION</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("###")
        
        with st.form("login_form"):
            user_input = st.text_input("Usuário", placeholder="ex: daniel.ripari").lower().strip()
            pass_input = st.text_input("Senha", type="password", placeholder="••••••")
            
            st.markdown("###")
            submitted = st.form_submit_button("ACESSAR MINHA CONTA", type="primary")
            
            if submitted:
                res = run_query("SELECT * FROM users WHERE name=? AND password=?", (user_input, pass_input))
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user_id = res[0][0]
                    st.session_state.user_name = res[0][1]
                    st.session_state.role = res[0][2]
                    st.toast(f"Bem-vindo de volta, {res[0][1].title()}!", icon="🚀")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.toast("Credenciais inválidas!", icon="❌")

# --- 5. SISTEMA PRINCIPAL (DASHBOARD PREMIUM) ---
else:
    # --- HEADER MINIMALISTA ---
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 3rem; background: #f0f2f6; width: 80px; height: 80px; line-height: 80px; border-radius: 50%; margin: 0 auto;">👤</div>
            <h3>{st.session_state.user_name.title()}</h3>
            <span style="background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">{st.session_state.role.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("SAIR DO APP", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()

    # --- SALDO (CARTÃO DE CRÉDITO VIRTUAL) ---
    res_bal = run_query("SELECT SUM(amount) FROM transactions WHERE user_id=?", (st.session_state.user_id,))
    saldo = res_bal[0][0] if res_bal and res_bal[0][0] else 0.0
    
    # HTML do Cartão
    st.markdown(f"""
    <div class="credit-card">
        <div class="logo">💳</div>
        <h3>Saldo Disponível</h3>
        <h1>R$ {saldo:,.2f}</h1>
        <p style="margin-top: 15px; opacity: 0.8; font-family: monospace; letter-spacing: 3px;">
            **** **** **** {str(st.session_state.user_id).zfill(4)}
        </p>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <span style="font-size: 0.8rem; opacity: 0.8;">TITULAR</span>
            <span style="font-size: 0.8rem; opacity: 0.8;">VALIDADE</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="font-weight: bold;">{st.session_state.user_name.upper()}</span>
            <span style="font-weight: bold;">12/30</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- ABAS MODERNAS ---
    tab_extrato, tab_grafico = st.tabs(["📜 Extrato", "📊 Gráficos"])

    with tab_extrato:
        st.caption("Últimas movimentações")
        df_hist = pd.read_sql_query(
            "SELECT timestamp, description, type, amount FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 15", 
            sqlite3.connect(DB_FILE), params=(st.session_state.user_id,)
        )
        
        if not df_hist.empty:
            st.dataframe(
                df_hist, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Data", format="DD/MM HH:mm"),
                    "description": "Descrição",
                    "type": "Tipo",
                    "amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                }
            )
        else:
            st.markdown("<div class='css-card' style='text-align:center; color: #888;'>Nenhuma movimentação ainda.</div>", unsafe_allow_html=True)

    with tab_grafico:
        if not df_hist.empty:
            chart_data = df_hist.groupby("type")["amount"].sum().reset_index()
            chart_data['amount'] = chart_data['amount'].abs()
            # Gráfico de Rosca (Donut) seria ideal, mas bar_chart é nativo e robusto
            st.bar_chart(chart_data, x="type", y="amount", color="type", use_container_width=True)
        else:
            st.info("Sem dados visuais.")

    # --- ADMINISTRAÇÃO (PAINEL CLEAN) ---
    if st.session_state.role == 'admin':
        st.markdown("###")
        st.subheader("⚙️ Painel de Comando")
        
        # Estilo Clean para os Expanders
        with st.expander("💸 Novo Lançamento", expanded=True):
            filhos = pd.read_sql_query("SELECT id, name FROM users WHERE role='user'", sqlite3.connect(DB_FILE))
            
            if filhos.empty:
                st.warning("Cadastre os filhos primeiro.")
            else:
                with st.form("form_lancamento"):
                    target_name = st.selectbox("Para quem?", filhos['name'].tolist())
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        val = st.number_input("Valor", min_value=0.00, step=1.0) 
                    with c2:
                        op = st.radio("Tipo", ["Crédito", "Débito"], horizontal=True)
                    
                    desc = st.text_input("Motivo")
                    
                    if st.form_submit_button("EFETUAR TRANSAÇÃO", type="primary"):
                        if val > 0 and desc:
                            target_id = filhos[filhos['name'] == target_name]['id'].values[0]
                            final_val = val if op == "Crédito" else -val
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)", 
                                      (int(target_id), final_val, desc, ts, op), commit=True)
                            
                            st.toast("Sucesso! Dinheiro enviado.", icon="💸")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.toast("Preencha todos os campos!", icon="⚠️")

        with st.expander("👥 Configurações de Membros"):
            tab_add, tab_edit = st.tabs(["Adicionar", "Gerenciar"])
            
            with tab_add:
                with st.form("form_add"):
                    col_u, col_p = st.columns(2)
                    new_n = col_u.text_input("Nome.Sobrenome").lower().strip()
                    new_p = col_p.text_input("Senha Inicial")
                    new_r = st.selectbox("Perfil", ["user", "admin"])
                    
                    if st.form_submit_button("CRIAR CONTA"):
                        if new_n and new_p:
                            check = run_query("SELECT * FROM users WHERE name=?", (new_n,))
                            if check:
                                st.error("Já existe.")
                            else:
                                run_query("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", 
                                          (new_n, new_r, new_p), commit=True)
                                st.toast(f"Usuário {new_n} criado!", icon="✅")
                                time.sleep(1)
                                st.rerun()

            with tab_edit:
                all_users = pd.read_sql_query("SELECT id, name FROM users ORDER BY name", sqlite3.connect(DB_FILE))
                t_user = st.selectbox("Selecionar Usuário", all_users['name'].unique())
                t_uid = all_users[all_users['name'] == t_user]['id'].values[0]

                # Alterar Senha
                with st.form("pwd_change"):
                    npwd = st.text_input(f"Nova senha para {t_user}")
                    if st.form_submit_button("ATUALIZAR SENHA"):
                        if npwd:
                            run_query("UPDATE users SET password=? WHERE id=?", (npwd, int(t_uid)), commit=True)
                            st.toast("Senha salva!", icon="🔒")
                
                st.markdown("---")
                # Exclusão
                check_del = st.checkbox("Destravar botão de exclusão", key=f"chk_{t_uid}")
                if st.button("EXCLUIR USUÁRIO", type="primary", disabled=not check_del):
                    if t_uid == st.session_state.user_id:
                        st.toast("Você não pode se excluir.", icon="🚫")
                    else:
                        run_query("DELETE FROM transactions WHERE user_id=?", (int(t_uid),), commit=True)
                        run_query("DELETE FROM users WHERE id=?", (int(t_uid),), commit=True)
                        st.toast("Usuário removido.", icon="🗑️")
                        time.sleep(1)
                        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #aaa; font-size: 0.8rem;">
    🛡️ RipariBank Secure System | v3.0 Infinity<br>
    Developed by <b>RipariTech</b>
</div>
""", unsafe_allow_html=True)
