import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO (Theme: Midnight Fintech) ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS "DARK MODE" AGRESSIVO E COMPACTO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    
    /* Fundo Global Escuro */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }

    /* REMOÇÃO TOTAL DE ESPAÇOS - ULTIMATE COMPACT */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100%;
    }
    
    /* Esconde Menu Hamburguer e Footer padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; color: white; }
    p, div, span { font-family: 'Inter', sans-serif; }
    
    /* CARD SALDO - DESIGN "CYBERPUNK" */
    .neon-card {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem;
        position: relative;
        box-shadow: 0 0 15px rgba(48, 43, 99, 0.4);
        margin-bottom: 15px;
        overflow: hidden;
    }
    /* Efeito de brilho no card */
    .neon-card::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
        transform: rotate(30deg);
        pointer-events: none;
    }

    /* INPUTS ESCUROS (GHOST) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
        color: #aaa !important;
        font-size: 0.8rem !important;
    }

    /* BOTÕES CUSTOMIZADOS */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: #262730;
        color: white;
        border: 1px solid #444;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:active {
        transform: scale(0.98);
        background: #333;
    }
    /* Botão Primário (Ação) - Verde Neon sutil */
    .stButton>button[kind="primary"] {
        background: #00C853; /* Verde forte */
        color: white;
        border: none;
        box-shadow: 0 4px 10px rgba(0, 200, 83, 0.3);
    }
    
    /* DATAFRAME TRANSPARENTE */
    div[data-testid="stDataFrame"] {
        background: transparent;
    }
    
    /* EXPANDER ESTILIZADO (MÓDULOS) */
    .streamlit-expanderHeader {
        background-color: #161920;
        color: white;
        border-radius: 8px;
        font-size: 0.9rem;
    }
    div[data-testid="stExpander"] {
        background-color: #0E1117;
        border: none;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #161920;
        padding: 5px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        white-space: nowrap;
        background-color: transparent;
        color: #888;
        border-radius: 6px;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
        color: white;
        font-weight: bold;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (SQLITE) ---
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
    run_query('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TEXT, type TEXT)''', commit=True)
    
    # Seeding inicial (apenas se vazio)
    if run_query("SELECT count(*) FROM users")[0][0] == 0:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        users = [
            ('danielripari', 'admin', '1234'), 
            ('ligiaripari', 'admin', '1234'), 
            ('muriloripari', 'user', 'kids1'), 
            ('ceciliaripari', 'user', 'kids2')
        ]
        c.executemany("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", users)
        conn.commit()
        conn.close()

init_db()

# --- 3. STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

# --- 4. LOGIN (DARK & BOLD & CASE INSENSITIVE) ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; margin-bottom:0;">💎</h1>
        <h2 style="font-weight:800; letter-spacing: -1px; margin-top:0;">Ripari<span style="color:#00C853;">Bank</span></h2>
        <p style="color:#666; font-size: 0.7rem; letter-spacing: 2px;">BLACK EDITION</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login"):
        # .lower() e .strip() garantem que "DanielRipari " vire "danielripari"
        u = st.text_input("USUÁRIO", placeholder="danielripari").lower().strip()
        # .strip() na senha previne espaço acidental do teclado mobile
        p = st.text_input("SENHA", type="password").strip()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("ACESSAR SISTEMA", type="primary"):
            # Query reforçada com lower(name) para garantir match absoluto
            res = run_query("SELECT * FROM users WHERE lower(name)=? AND password=?", (u, p))
            if res:
                st.session_state.logged_in = True
                st.session_state.user_id = res[0][0]
                st.session_state.user_name = res[0][1]
                st.session_state.role = res[0][2]
                st.rerun()
            else:
                st.toast("Usuário ou senha incorretos", icon="🚫")

# --- 5. DASHBOARD (COMPACTO) ---
else:
    # --- HEADER ULTRA COMPACTO (INLINE) ---
    c1, c2, c3 = st.columns([1, 6, 1])
    with c1: st.markdown("💎")
    with c2: st.markdown(f"**{st.session_state.user_name.split('.')[0].title()}** <span style='color:#666; font-size:0.7rem;'>{st.session_state.role.upper()}</span>", unsafe_allow_html=True)
    with c3: 
        if st.button("✖"): # Botão X pequeno para sair
            st.session_state.logged_in = False
            st.rerun()

    # --- SALDO HERO ---
    bal = run_query("SELECT SUM(amount) FROM transactions WHERE user_id=?", (st.session_state.user_id,))
    saldo = bal[0][0] if bal and bal[0][0] else 0.0
    
    st.markdown(f"""
    <div class="neon-card">
        <div style="color:#888; font-size:0.7rem; margin-bottom:5px;">SALDO ATUAL</div>
        <div style="font-size:2.2rem; font-weight:800; color:white; font-family:'Roboto Mono', monospace;">R$ {saldo:,.2f}</div>
        <div style="text-align:right; margin-top:-20px; font-size:1.5rem; opacity:0.3;">📶</div>
    </div>
    """, unsafe_allow_html=True)

    # --- TABS COMPACTAS ---
    t1, t2 = st.tabs(["EXTRATO", "GRÁFICOS"])
    
    with t1:
        df = pd.read_sql_query("SELECT timestamp, description, type, amount FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", sqlite3.connect(DB_FILE), params=(st.session_state.user_id,))
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "timestamp": st.column_config.DatetimeColumn("Data", format="DD/MM"),
                "description": st.column_config.TextColumn("Desc", width="medium"),
                "type": st.column_config.TextColumn("Op", width="small"),
                "amount": st.column_config.NumberColumn("R$", format="%.2f")
            })
        else:
            st.caption("Sem dados.")

    with t2:
        if not df.empty:
            chart = df.groupby("type")["amount"].sum().reset_index()
            chart['amount'] = chart['amount'].abs()
            st.bar_chart(chart, x="type", y="amount", color="type", use_container_width=True)

    # --- ADMIN AREA ---
    if st.session_state.role == 'admin':
        st.markdown("<hr style='border-color: #333; margin: 15px 0;'>", unsafe_allow_html=True)
        
        # Módulo de Lançamento (Expandido por padrão)
        with st.expander("💸 NOVO LANÇAMENTO", expanded=True):
            users = pd.read_sql_query("SELECT id, name FROM users WHERE role='user'", sqlite3.connect(DB_FILE))
            if not users.empty:
                with st.form("trans_mobile"):
                    # Linha 1: Quem
                    target = st.selectbox("Para:", users['name'].tolist())
                    
                    # Linha 2: Valor e Tipo (Lado a lado, compacto)
                    c_val, c_op = st.columns([1, 1.2]) # Ajuste de proporção
                    with c_val:
                        val = st.number_input("Valor", min_value=0.0, step=1.0)
                    with c_op:
                        # Label manual para garantir leitura no mobile
                        st.caption("Operação:")
                        op = st.radio("LabelOculto", ["Crédito", "Débito"], horizontal=True, label_visibility="collapsed")
                    
                    # Linha 3: Motivo
                    desc = st.text_input("Motivo")
                    
                    if st.form_submit_button("CONFIRMAR", type="primary"):
                        if val > 0 and desc:
                            uid = users[users['name'] == target]['id'].values[0]
                            final = val if op == "Crédito" else -val
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)", (int(uid), final, desc, ts, op), commit=True)
                            st.toast("Lançado!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
            else:
                st.warning("Cadastre filhos.")

        # Módulo de Membros (Colapsado)
        with st.expander("⚙️ MEMBROS"):
            tab_a, tab_b = st.tabs(["NOVO", "GERENCIAR"])
            with tab_a:
                with st.form("new_u"):
                    # Força lower e strip na criação também
                    n = st.text_input("Nome").lower().strip()
                    p = st.text_input("Senha").strip()
                    r = st.selectbox("Role", ["user", "admin"])
                    if st.form_submit_button("Criar"):
                        if n and p and not run_query("SELECT * FROM users WHERE name=?", (n,)):
                            run_query("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (n, r, p), commit=True)
                            st.toast("OK!", icon="👍")
                            time.sleep(0.5)
                            st.rerun()
            
            with tab_b:
                all_u = pd.read_sql_query("SELECT id, name FROM users", sqlite3.connect(DB_FILE))
                if not all_u.empty:
                    sel = st.selectbox("User:", all_u['name'].unique())
                    t_uid = all_u[all_u['name'] == sel]['id'].values[0]
                    
                    # Form senha
                    with st.form("pwd"):
                        np = st.text_input("Nova Senha").strip()
                        if st.form_submit_button("Salvar Senha"):
                            run_query("UPDATE users SET password=? WHERE id=?", (np, int(t_uid)), commit=True)
                            st.toast("Senha Salva")
                    
                    st.write("")
                    del_chk = st.checkbox("Liberar Delete", key=f"d{t_uid}")
                    if st.button("EXCLUIR", disabled=not del_chk):
                        if t_uid != st.session_state.user_id:
                            run_query("DELETE FROM transactions WHERE user_id=?", (int(t_uid),), commit=True)
                            run_query("DELETE FROM users WHERE id=?", (int(t_uid),), commit=True)
                            st.rerun()
                        else: st.error("Erro.")

# --- FOOTER INVISÍVEL PARA ECONOMIZAR ESPAÇO ---
