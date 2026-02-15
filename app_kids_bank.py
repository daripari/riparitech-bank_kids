import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO (Theme: Midnight Fintech) ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS "DARK MODE" (Mantido idêntico por ser sucesso de crítica)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 100%; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; color: white; }
    
    .neon-card {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 0 15px rgba(48, 43, 99, 0.4);
        margin-bottom: 15px;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1A1C24 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: #262730;
        color: white;
        border: 1px solid #444;
        font-weight: 600;
    }
    .stButton>button[kind="primary"] {
        background: #00C853; color: white; border: none;
    }
    
    div[data-testid="stExpander"] { background-color: #0E1117; border: none; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161920; padding: 5px; border-radius: 10px; }
    .stTabs [aria-selected="true"] { background-color: #262730; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (SUPABASE / POSTGRESQL) ---
# Usamos st.connection que gerencia o pool de conexões automaticamente
conn = st.connection("supabase", type="sql")

def run_query(query_str, params=None, commit=False):
    """
    Função wrapper para lidar com SQLAlchemy e PostgreSQL.
    No SQLAlchemy, usamos text() para SQL bruto e :param para bind.
    """
    try:
        if commit:
            # Para INSERT/UPDATE/DELETE usamos uma sessão transacional
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            return True
        else:
            # Para SELECT usamos query() direto que retorna DataFrame ou lista
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except Exception as e:
        st.error(f"Erro de Banco de Dados: {e}")
        return None

def init_db():
    # Criação de Tabelas (Sintaxe PostgreSQL)
    # SERIAL substitui AUTOINCREMENT do SQLite
    run_query('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, 
            name TEXT NOT NULL, 
            role TEXT, 
            password TEXT
        );
    ''', commit=True)
    
    run_query('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY, 
            user_id INTEGER, 
            amount REAL, 
            description TEXT, 
            timestamp TIMESTAMP, 
            type TEXT
        );
    ''', commit=True)
    
    # Seeding Inicial
    # Verifica se tabela está vazia
    res = run_query("SELECT count(*) as cnt FROM users")
    # O retorno do sqlalchemy com pandas é um DataFrame, pegamos o valor
    count = res.iloc[0]['cnt'] if not res.empty else 0
    
    if count == 0:
        # Inserção em lote usando SQL bruto
        initial_users = [
            {'n': 'danielripari', 'r': 'admin', 'p': '1234'},
            {'n': 'ligiaripari', 'r': 'admin', 'p': '1234'},
            {'n': 'muriloripari', 'r': 'user', 'p': 'kids1'},
            {'n': 'ceciliaripari', 'r': 'user', 'p': 'kids2'}
        ]
        
        for u in initial_users:
            run_query(
                "INSERT INTO users (name, role, password) VALUES (:n, :r, :p)",
                params=u,
                commit=True
            )

# Inicializa banco na nuvem
init_db()

# --- 3. STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; margin-bottom:0;">💎</h1>
        <h2 style="font-weight:800; letter-spacing: -1px; margin-top:0;">Ripari<span style="color:#00C853;">Bank</span></h2>
        <p style="color:#666; font-size: 0.7rem; letter-spacing: 2px;">CLOUD EDITION</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login"):
        u = st.text_input("USUÁRIO", placeholder="danielripari").lower().strip()
        p = st.text_input("SENHA", type="password").strip()
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("ACESSAR SISTEMA", type="primary"):
            # Sintaxe :param para Postgres via SQLAlchemy
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                # Acessa pelo nome da coluna (Pandas DataFrame)
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.rerun()
            else:
                st.toast("Acesso negado", icon="🚫")

# --- 5. DASHBOARD ---
else:
    # Header
    c1, c2, c3 = st.columns([1, 6, 1])
    with c1: st.markdown("💎")
    with c2: st.markdown(f"**{st.session_state.user_name.title()}** <span style='color:#666; font-size:0.7rem;'>{st.session_state.role.upper()}</span>", unsafe_allow_html=True)
    with c3: 
        if st.button("✖"):
            st.session_state.logged_in = False
            st.rerun()

    # Saldo (Query Agregada)
    res_bal = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': st.session_state.user_id})
    saldo = res_bal.iloc[0]['total'] if not res_bal.empty and pd.notnull(res_bal.iloc[0]['total']) else 0.0
    
    st.markdown(f"""
    <div class="neon-card">
        <div style="color:#888; font-size:0.7rem; margin-bottom:5px;">SALDO ATUAL</div>
        <div style="font-size:2.2rem; font-weight:800; color:white; font-family:'Roboto Mono', monospace;">R$ {saldo:,.2f}</div>
        <div style="text-align:right; margin-top:-20px; font-size:1.5rem; opacity:0.3;">📶</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["EXTRATO", "GRÁFICOS"])
    
    with t1:
        # PostgreSQL exige nomes de colunas explícitos ou mapeamento
        df = run_query(
            "SELECT timestamp, description, type, amount FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 10", 
            params={'uid': st.session_state.user_id}
        )
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

    # --- ADMIN ---
    if st.session_state.role == 'admin':
        st.markdown("<hr style='border-color: #333; margin: 15px 0;'>", unsafe_allow_html=True)
        
        with st.expander("💸 NOVO LANÇAMENTO", expanded=True):
            users = run_query("SELECT id, name FROM users WHERE role='user'")
            if not users.empty:
                with st.form("trans_mobile"):
                    target_name = st.selectbox("Para:", users['name'].tolist())
                    
                    c_val, c_op = st.columns([1, 1.2])
                    with c_val: val = st.number_input("Valor", min_value=0.0, step=1.0)
                    with c_op: 
                        st.caption("Op:")
                        op = st.radio("L", ["Crédito", "Débito"], horizontal=True, label_visibility="collapsed")
                    
                    desc = st.text_input("Motivo")
                    
                    if st.form_submit_button("CONFIRMAR", type="primary"):
                        if val > 0 and desc:
                            uid = users[users['name'] == target_name]['id'].values[0]
                            final = val if op == "Crédito" else -val
                            ts = datetime.now() # Python datetime object vai direto pro Postgres
                            
                            run_query(
                                "INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :type)", 
                                params={'uid': int(uid), 'amt': final, 'desc': desc, 'ts': ts, 'type': op}, 
                                commit=True
                            )
                            st.toast("Sucesso!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
            else:
                st.warning("Cadastre filhos.")

        with st.expander("⚙️ MEMBROS"):
            tab_a, tab_b = st.tabs(["NOVO", "GERENCIAR"])
            with tab_a:
                with st.form("new_u"):
                    n = st.text_input("Nome").lower().strip()
                    p = st.text_input("Senha").strip()
                    r = st.selectbox("Role", ["user", "admin"])
                    if st.form_submit_button("Criar"):
                        check = run_query("SELECT * FROM users WHERE name=:n", params={'n': n})
                        if check.empty:
                            run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params={'n': n, 'r': r, 'p': p}, commit=True)
                            st.toast("Criado!", icon="👍")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Já existe.")
            
            with tab_b:
                all_u = run_query("SELECT id, name FROM users")
                if not all_u.empty:
                    sel = st.selectbox("User:", all_u['name'].unique())
                    t_uid = all_u[all_u['name'] == sel]['id'].values[0]
                    
                    with st.form("pwd"):
                        np = st.text_input("Nova Senha").strip()
                        if st.form_submit_button("Salvar"):
                            run_query("UPDATE users SET password=:p WHERE id=:id", params={'p': np, 'id': int(t_uid)}, commit=True)
                            st.toast("Salvo")
                    
                    st.write("")
                    del_chk = st.checkbox("Liberar Delete", key=f"d{t_uid}")
                    if st.button("EXCLUIR", disabled=not del_chk):
                        if t_uid != st.session_state.user_id:
                            run_query("DELETE FROM transactions WHERE user_id=:id", params={'id': int(t_uid)}, commit=True)
                            run_query("DELETE FROM users WHERE id=:id", params={'id': int(t_uid)}, commit=True)
                            st.rerun()
                        else: st.error("Erro.")
