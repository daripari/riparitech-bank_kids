import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO (Theme: Minimalist Midnight) ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS REFORÇADO PARA FIXAÇÃO ABSOLUTA E ALINHAMENTO HORIZONTAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }

    .stApp { background-color: #0B0E14; color: #BBBBBB; }

    /* BLINDAGEM CONTRA QUEBRA DE POSITION: FIXED */
    [data-testid="stAppViewContainer"], 
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stVerticalBlock"] {
        transform: none !important;
        perspective: none !important;
        overflow: visible !important;
    }
    
    #MainMenu, footer, header { visibility: hidden !important; }

    /* BARRA DE NAVEGAÇÃO FIXA */
    .nav-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 55px;
        background-color: #0B0E14;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    /* LOGO À ESQUERDA */
    .nav-logo {
        position: fixed;
        top: 16px; 
        left: 1.2rem;
        font-size: 1.1rem !important;
        font-weight: 600;
        color: white;
        z-index: 1000000;
        margin: 0;
        pointer-events: none;
    }

    /* --- POSICIONAMENTO DOS BOTÕES LADO A LADO --- */
    
    /* BOTÃO SAIR (Extrema Direita) */
    div.element-container:has(button[key="logout_header"]) {
        position: fixed !important;
        top: 13px !important;
        right: 1rem !important;
        z-index: 1000001 !important;
        width: auto !important;
    }

    /* BOTÃO REFRESH (Ao lado do Sair) */
    div.element-container:has(button[key="refresh_header"]) {
        position: fixed !important;
        top: 13px !important;
        right: 4.8rem !important; /* Espaçamento calculado para o lado */
        z-index: 1000001 !important;
        width: auto !important;
    }

    /* Estilo dos botões do Header */
    div.element-container:has(button[key="logout_header"]) button,
    div.element-container:has(button[key="refresh_header"]) button {
        height: 28px !important;
        padding: 0 10px !important;
        font-size: 0.7rem !important;
        background: #1A1C24 !important;
        color: #888 !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        text-transform: uppercase;
        font-weight: 600;
        display: inline-flex !important;
    }

    div.element-container:has(button[key="logout_header"]) button:hover,
    div.element-container:has(button[key="refresh_header"]) button:hover {
        color: white !important;
        border-color: #00C853 !important;
    }

    /* CONTEÚDO PRINCIPAL */
    .block-container {
        padding-top: 5rem !important; 
        padding-bottom: 2rem !important;
        max-width: 500px;
    }

    .slim-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 15px;
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
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (SUPABASE) ---
try:
    conn = st.connection("supabase", type="sql")
except Exception:
    st.error("Erro: Connection String ausente nos Secrets.")
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
                {'n': 'daniel', 'r': 'admin', 'p': '1234'},
                {'n': 'ligia', 'r': 'admin', 'p': '1234'},
                {'n': 'murilo', 'r': 'user', 'p': 'kids1'},
                {'n': 'cecilia', 'r': 'user', 'p': 'kids2'}
            ]
            for u in initial_users:
                run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params=u, commit=True)

init_db()

# --- 3. STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<div class='nav-bar'><p class='nav-logo'>💎 RipariBank</p></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; margin-top:3rem;'><p style='color:#666; font-size:0.8rem;'>Acesso Seguro</p></div>", unsafe_allow_html=True)
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
            else: st.toast("Acesso negado.")

# --- 5. DASHBOARD ---
else:
    # NAVBAR FIXA
    st.markdown("<div class='nav-bar'><p class='nav-logo'>💎 RipariBank</p></div>", unsafe_allow_html=True)
    
    # BOTÕES DO HEADER
    if st.button("🔄", key="refresh_header"):
        st.rerun()
        
    if st.button("SAIR", key="logout_header"):
        st.session_state.logged_in = False
        st.rerun()

    # Saudação
    st.markdown(f"<p style='color:#666; font-size: 0.8rem;'>Olá, <b>{st.session_state.user_name.title()}</b></p>", unsafe_allow_html=True)

    # Saldo
    res_bal = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': st.session_state.user_id})
    saldo = res_bal.iloc[0]['total'] if res_bal is not None and not res_bal.empty and pd.notnull(res_bal.iloc[0]['total']) else 0.0
    
    st.markdown(f"""
    <div class="slim-card">
        <span style="color:#888; font-size:0.8rem;">SALDO DISPONÍVEL</span>
        <span class="balance-val">R$ {saldo:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    # Conteúdo
    t1, t2 = st.tabs(["EXTRATO", "RESUMO"])
    with t1:
        df = run_query("SELECT timestamp, description, type, amount FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 10", params={'uid': st.session_state.user_id})
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.caption("Sem movimentos.")
    
    with t2:
        if df is not None and not df.empty:
            st.bar_chart(df.groupby("type")["amount"].sum().abs(), height=150)

    # ADMIN PANEL
    if st.session_state.role == 'admin':
        st.markdown("---")
        with st.expander("💸 LANÇAMENTO RÁPIDO"):
            users = run_query("SELECT id, name FROM users WHERE role='user'")
            if users is not None and not users.empty:
                with st.form("tr_fast"):
                    tgt = st.selectbox("Membro:", users['name'].tolist())
                    v = st.number_input("Valor", min_value=0.0, step=1.0)
                    o = st.radio("Tipo:", ["Crédito", "Débito"], horizontal=True)
                    d = st.text_input("Nota")
                    if st.form_submit_button("LANÇAR", type="primary"):
                        if v > 0 and d:
                            uid_tgt = users[users['name'] == tgt]['id'].values[0]
                            final = v if o == "Crédito" else -v
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, :ts, :t)", 
                                      params={'u': int(uid_tgt), 'a': final, 'd': d, 'ts': datetime.now(), 't': o}, commit=True)
                            st.toast("Sucesso!")
                            time.sleep(0.5); st.rerun()

        with st.expander("⚙️ GESTÃO DE ACESSOS"):
            tab_add, tab_ed = st.tabs(["Novo", "Gerir"])
            with tab_add:
                with st.form("new_mem"):
                    nn = st.text_input("Nome").lower().strip()
                    np = st.text_input("Senha").strip()
                    nr = st.selectbox("Perfil", ["user", "admin"])
                    if st.form_submit_button("CRIAR"):
                        if nn and np:
                            run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params={'n': nn, 'r': nr, 'p': np}, commit=True)
                            st.toast("Membro criado!"); time.sleep(0.5); st.rerun()
            
            with tab_ed:
                all_u = run_query("SELECT id, name FROM users ORDER BY name")
                if all_u is not None and not all_u.empty:
                    sel_u = st.selectbox("Escolher:", all_u['name'].tolist())
                    u_id = all_u[all_u['name'] == sel_u]['id'].values[0]
                    with st.form("p_edit"):
                        new_p = st.text_input("Nova Senha").strip()
                        if st.form_submit_button("SALVAR"):
                            run_query("UPDATE users SET password=:p WHERE id=:id", params={'p': new_p, 'id': int(u_id)}, commit=True)
                            st.toast("Ok!"); time.sleep(0.5); st.rerun()
                    if st.button("REMOVER MEMBRO"):
                        if int(u_id) != st.session_state.user_id:
                            run_query("DELETE FROM transactions WHERE user_id=:id", params={'id': int(u_id)}, commit=True)
                            run_query("DELETE FROM users WHERE id=:id", params={'id': int(u_id)}, commit=True)
                            st.rerun()

# --- FOOTER ---
st.markdown("<div style='text-align: center; color: #333; font-size: 0.6rem; margin-top: 3rem;'>RipariBank v4.8 | Secured by Supabase</div>", unsafe_allow_html=True)
