import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO (Theme: Minimalist Midnight) ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS ULTRA COMPACTO E MINIMALISTA COM HEADER FIXO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }

    .stApp { background-color: #0B0E14; color: #BBBBBB; }

    /* AJUSTE DO CONTAINER PARA HEADER FIXO */
    .block-container {
        padding-top: 3.5rem !important; /* Espaço para o header fixo não cobrir o conteúdo */
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px;
    }
    
    #MainMenu, footer, header { visibility: hidden; }

    /* Títulos Menores */
    h1 { font-size: 1.3rem !important; font-weight: 600; color: white; margin-bottom: 0px !important; margin-top: 0px !important; }
    h2 { font-size: 1.1rem !important; font-weight: 600; color: white; }
    h3 { font-size: 0.9rem !important; font-weight: 600; color: #888; }

    /* HEADER LOGO FIXO NO TOPO */
    .app-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #0B0E14; /* Fundo sólido para não transparecer conteúdo ao rolar */
        text-align: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 1000;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* CARD SALDO SLIM */
    .slim-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .balance-val {
        font-size: 1.4rem;
        font-weight: 600;
        color: #00C853;
        letter-spacing: -1px;
    }

    /* BOTÕES COMPACTOS */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 2.2em;
        font-size: 0.85rem;
        font-weight: 400;
        background: #1A1C24;
        color: #CCC;
        border: 1px solid #333;
    }
    .stButton>button[kind="primary"] {
        background: #00C853;
        color: white;
        border: none;
        font-weight: 600;
    }

    /* INPUTS MINIMALISTAS */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #161920 !important;
        color: white !important;
        border: 1px solid #2A2D35 !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        height: 35px !important;
    }
    
    /* Tabelas e Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; background: none; }
    .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 4px 8px; color: #666; }
    .stTabs [aria-selected="true"] { color: white; border-bottom: 2px solid #00C853; }
    
    .element-container { margin-bottom: 0.4rem !important; }
    div[data-testid="stExpander"] { border: none; background: #11141A; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (SUPABASE) ---
try:
    conn = st.connection("supabase", type="sql")
except Exception:
    st.error("Erro: Verifique os Secrets.")
    st.stop()

def run_query(query_str, params=None, commit=False):
    try:
        if commit:
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            return True
        else:
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except Exception:
        return None

def init_db():
    run_query('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT);''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TIMESTAMP, type TEXT);''', commit=True)
    
    res = run_query("SELECT count(*) as cnt FROM users")
    if res is not None and not res.empty:
        if res.iloc[0]['cnt'] == 0:
            initial_users = [
                {'n': 'danielripari', 'r': 'admin', 'p': '1234'},
                {'n': 'ligiaripari', 'r': 'admin', 'p': '1234'},
                {'n': 'muriloripari', 'r': 'user', 'p': 'kids1'},
                {'n': 'ceciliaripari', 'r': 'user', 'p': 'kids2'}
            ]
            for u in initial_users:
                run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params=u, commit=True)

init_db()

# --- 3. STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    # Header fixo também no login para consistência
    st.markdown("<div class='app-header'><h1>💎 RipariBank</h1></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; margin-top:2rem;'><p style='color:#666; font-size:0.8rem;'>Acesso Seguro à Nuvem</p></div>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Usuário").lower().strip()
        p = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR", type="primary"):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.rerun()
            else: st.toast("Erro no acesso.")

# --- 5. DASHBOARD ---
else:
    # Header Logo Fixo
    st.markdown("<div class='app-header'><h1>💎 RipariBank</h1></div>", unsafe_allow_html=True)

    # Info Usuário e Sair
    header_col, btn_col = st.columns([4, 1])
    header_col.markdown(f"<span style='color:#888;'>Conta:</span> **{st.session_state.user_name}**", unsafe_allow_html=True)
    if btn_col.button("SAIR"): 
        st.session_state.logged_in = False
        st.rerun()

    # Saldo Slim
    res_bal = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': st.session_state.user_id})
    saldo = res_bal.iloc[0]['total'] if res_bal is not None and not res_bal.empty and pd.notnull(res_bal.iloc[0]['total']) else 0.0
    
    st.markdown(f"""
    <div class="slim-card">
        <span style="color:#888; font-size:0.85rem;">SALDO DISPONÍVEL</span>
        <span class="balance-val">R$ {saldo:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    t1, t2 = st.tabs(["HISTÓRICO", "RESUMO"])
    with t1:
        df = run_query("SELECT timestamp, description, type, amount FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 8", params={'uid': st.session_state.user_id})
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.caption("Vazio.")
    
    with t2:
        if df is not None and not df.empty:
            st.bar_chart(df.groupby("type")["amount"].sum().abs(), height=150)

    # ADMIN
    if st.session_state.role == 'admin':
        st.markdown("---")
        with st.expander("💸 LANÇAMENTO"):
            users = run_query("SELECT id, name FROM users WHERE role='user'")
            if users is not None and not users.empty:
                with st.form("tr"):
                    tgt = st.selectbox("Para", users['name'].tolist())
                    v = st.number_input("Valor", min_value=0.0, step=1.0)
                    o = st.radio("Tipo", ["Crédito", "Débito"], horizontal=True)
                    d = st.text_input("Motivo")
                    if st.form_submit_button("LANÇAR", type="primary"):
                        if v > 0 and d:
                            uid_tgt = users[users['name'] == tgt]['id'].values[0]
                            final = v if o == "Crédito" else -v
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, :ts, :t)", 
                                      params={'u': int(uid_tgt), 'a': final, 'd': d, 'ts': datetime.now(), 't': o}, commit=True)
                            st.toast("Sucesso")
                            time.sleep(0.5); st.rerun()

        with st.expander("⚙️ GESTÃO DE USUÁRIOS"):
            tab_new, tab_manage = st.tabs(["Novo", "Gerenciar"])
            with tab_new:
                with st.form("nu"):
                    nn = st.text_input("Nome").lower().strip()
                    np = st.text_input("Senha").strip()
                    nr = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("Criar"):
                        if nn and np:
                            check = run_query("SELECT * FROM users WHERE name=:n", params={'n': nn})
                            if check is not None and check.empty:
                                run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params={'n': nn, 'r': nr, 'p': np}, commit=True)
                                st.toast("Criado"); time.sleep(0.5); st.rerun()
            
            with tab_manage:
                all_u = run_query("SELECT id, name FROM users ORDER BY name")
                if all_u is not None and not all_u.empty:
                    sel_u = st.selectbox("Selecionar Usuário", all_u['name'].tolist())
                    u_id = all_u[all_u['name'] == sel_u]['id'].values[0]
                    with st.form("edit_pass"):
                        new_p = st.text_input("Alterar Senha").strip()
                        if st.form_submit_button("Salvar Senha"):
                            if new_p:
                                run_query("UPDATE users SET password=:p WHERE id=:id", params={'p': new_p, 'id': int(u_id)}, commit=True)
                                st.toast("Atualizado"); time.sleep(0.5); st.rerun()
                    if st.button("EXCLUIR USUÁRIO"):
                        if int(u_id) != st.session_state.user_id:
                            run_query("DELETE FROM transactions WHERE user_id=:id", params={'id': int(u_id)}, commit=True)
                            run_query("DELETE FROM users WHERE id=:id", params={'id': int(u_id)}, commit=True)
                            st.rerun()

# --- FOOTER ---
st.markdown("<div style='text-align: center; color: #444; font-size: 0.7rem; margin-top: 2rem;'>RipariBank Minimal v4.2</div>", unsafe_allow_html=True)
