import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO VISUAL & CSS (RipariBank Compact Mobile) ---
st.set_page_config(page_title="RipariBank", page_icon="💳", layout="centered")

# CSS OTIMIZADO: Layout Compacto e Mobile-First
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Redução drástica de espaços vazios para Mobile */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .stApp { background-color: #f4f6f9; }

    /* Card Compacto */
    .css-card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }

    /* Cartão de Crédito Ultra-Compacto */
    .credit-card {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: 16px;
        padding: 1.2rem;
        color: white;
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.3);
        margin-bottom: 15px;
        position: relative;
    }
    .credit-card h3 {
        color: rgba(255,255,255,0.9);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
    }
    .credit-card h1 {
        color: white;
        font-size: 2rem; /* Fonte menor para caber no celular */
        margin: 5px 0;
        font-weight: 800;
    }
    .credit-card .logo {
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 1.5rem;
        opacity: 0.6;
    }
    .credit-card .info-row {
        display: flex; 
        justify-content: space-between; 
        margin-top: 10px;
        font-size: 0.75rem;
    }

    /* Botões Otimizados para Toque (Altura reduzida mas clicável) */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 2.8em;
        font-weight: 600;
        border: none;
        font-size: 0.95rem;
    }
    .stButton>button[kind="primary"] {
        background: #4F46E5;
        color: white;
    }

    /* Ajuste de Inputs para ocupar menos espaço vertical */
    .stTextInput, .stNumberInput, .stSelectbox {
        margin-bottom: -10px;
    }
    
    /* Remove padding excessivo de Abas e Expanders */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 5px 10px;
        font-size: 0.9rem;
    }
    
    /* Títulos menores */
    h1, h2, h3 { letter-spacing: -0.5px; }
    
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
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
        st.error(f"Erro: {e}")
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

# --- 4. TELA DE LOGIN (COMPACTA) ---
if not st.session_state.logged_in:
    # Centralização
    st.markdown("###")
    st.markdown("""
    <div class="css-card" style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏦</div>
        <h2 style="margin:0; color:#333;">RipariBank</h2>
        <p style="font-size: 0.8rem; color: #666;">MOBILE EDITION</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        user_input = st.text_input("Usuário", placeholder="ex: daniel.ripari").lower().strip()
        pass_input = st.text_input("Senha", type="password")
        
        st.markdown("###")
        submitted = st.form_submit_button("ENTRAR", type="primary")
        
        if submitted:
            res = run_query("SELECT * FROM users WHERE name=? AND password=?", (user_input, pass_input))
            if res:
                st.session_state.logged_in = True
                st.session_state.user_id = res[0][0]
                st.session_state.user_name = res[0][1]
                st.session_state.role = res[0][2]
                st.rerun()
            else:
                st.toast("Erro de acesso.", icon="🔒")

# --- 5. SISTEMA PRINCIPAL (LAYOUT COMPACTO) ---
else:
    # --- HEADER ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user_name.title()}**")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()

    # --- SALDO ---
    res_bal = run_query("SELECT SUM(amount) FROM transactions WHERE user_id=?", (st.session_state.user_id,))
    saldo = res_bal[0][0] if res_bal and res_bal[0][0] else 0.0
    
    st.markdown(f"""
    <div class="credit-card">
        <div class="logo">💳</div>
        <h3>Saldo Atual</h3>
        <h1>R$ {saldo:,.2f}</h1>
        <div class="info-row">
            <span>{st.session_state.user_name.upper()}</span>
            <span>RPR-BANK</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- TABS ---
    tab_extrato, tab_grafico = st.tabs(["📜 Extrato", "📊 Visão"])

    with tab_extrato:
        df_hist = pd.read_sql_query(
            "SELECT timestamp, description, type, amount FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", 
            sqlite3.connect(DB_FILE), params=(st.session_state.user_id,)
        )
        
        if not df_hist.empty:
            st.dataframe(
                df_hist, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Data", format="DD/MM"),
                    "description": "Motivo",
                    "type": st.column_config.TextColumn("Tipo", width="small"),
                    "amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                }
            )
        else:
            st.caption("Sem movimentações.")

    with tab_grafico:
        if not df_hist.empty:
            chart_data = df_hist.groupby("type")["amount"].sum().reset_index()
            chart_data['amount'] = chart_data['amount'].abs()
            st.bar_chart(chart_data, x="type", y="amount", color="type", use_container_width=True)
        else:
            st.caption("Sem dados.")

    # --- ADMIN (CORREÇÃO DE LAYOUT) ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        # Expander padrão fechado para economizar espaço se não for usar
        with st.expander("💸 Novo Lançamento", expanded=True):
            filhos = pd.read_sql_query("SELECT id, name FROM users WHERE role='user'", sqlite3.connect(DB_FILE))
            
            if filhos.empty:
                st.warning("Sem contas de filhos.")
            else:
                with st.form("form_lancamento"):
                    # Layout vertical para garantir legibilidade no mobile
                    target_name = st.selectbox("Para quem?", filhos['name'].tolist())
                    
                    # Correção do Radio Button: Full width para ler o texto
                    op = st.radio("Tipo de Operação", ["Crédito", "Débito"], horizontal=True)
                    
                    val = st.number_input("Valor (R$)", min_value=0.00, step=1.0) 
                    desc = st.text_input("Motivo")
                    
                    st.markdown("###")
                    if st.form_submit_button("CONFIRMAR", type="primary"):
                        if val > 0 and desc:
                            target_id = filhos[filhos['name'] == target_name]['id'].values[0]
                            final_val = val if op == "Crédito" else -val
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)", 
                                      (int(target_id), final_val, desc, ts, op), commit=True)
                            
                            st.toast("Lançamento OK!", icon="✅")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.toast("Preencha tudo.", icon="⚠️")

        with st.expander("⚙️ Admin Usuários"):
            tab_add, tab_ger = st.tabs(["Criar", "Editar"])
            
            with tab_add:
                with st.form("add_u"):
                    nn = st.text_input("Nome (user.sobrenome)").lower().strip()
                    np = st.text_input("Senha")
                    nr = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("Salvar"):
                        if nn and np:
                            if not run_query("SELECT * FROM users WHERE name=?", (nn,)):
                                run_query("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (nn, nr, np), commit=True)
                                st.toast("Criado!", icon="🎉")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Já existe.")

            with tab_ger:
                all_u = pd.read_sql_query("SELECT id, name FROM users ORDER BY name", sqlite3.connect(DB_FILE))
                sel_u = st.selectbox("Editar:", all_u['name'].unique())
                uid = all_u[all_u['name'] == sel_u]['id'].values[0]
                
                with st.form("edit_p"):
                    new_pass = st.text_input("Nova Senha")
                    if st.form_submit_button("Alterar Senha"):
                        run_query("UPDATE users SET password=? WHERE id=?", (new_pass, int(uid)), commit=True)
                        st.success("Senha alterada.")
                
                st.markdown("###")
                chk = st.checkbox("Liberar Exclusão", key=f"del_{uid}")
                if st.button("Apagar Usuário", disabled=not chk):
                    if uid != st.session_state.user_id:
                        run_query("DELETE FROM transactions WHERE user_id=?", (int(uid),), commit=True)
                        run_query("DELETE FROM users WHERE id=?", (int(uid),), commit=True)
                        st.rerun()
                    else:
                        st.error("Erro.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #aaa;'>RipariBank Mobile v4.0</div>", unsafe_allow_html=True)
