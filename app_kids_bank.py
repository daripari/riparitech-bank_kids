import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank Stealth", page_icon="💎", layout="centered")

# CSS STEALTH GRAPHITE UI - V8.0
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #080808;
        color: #FFFFFF;
    }
    
    .stApp { background-color: #080808; }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 2rem !important; max-width: 450px !important; }

    /* Logo Estilo Stealth */
    .stealth-header {
        text-align: left;
        padding-bottom: 2rem;
    }
    .stealth-logo {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: #3B82F6; /* Electric Blue */
        text-transform: uppercase;
    }
    
    /* Cards Sólidos */
    .stealth-card {
        background-color: #121214;
        border: 1px solid #222224;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }

    .admin-row {
        background-color: #121214;
        border-bottom: 1px solid #1A1A1C;
        padding: 12px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .label-minor {
        color: #636366;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .val-major {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Botões Stealth */
    .stButton>button {
        border-radius: 8px !important;
        background-color: #1C1C1E !important;
        color: #FFFFFF !important;
        border: 1px solid #2C2C2E !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        height: 50px !important;
        transition: 0.1s;
    }
    
    .stButton>button:hover {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    /* Botão Primário */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #3B82F6 !important;
        border: none !important;
    }

    /* Calculadora de Alta Precisão */
    .calc-box {
        background-color: #000000;
        border: 2px solid #1C1C1E;
        border-radius: 8px;
        padding: 15px;
        text-align: right;
        font-size: 2rem;
        font-family: 'JetBrains Mono', monospace;
        color: #3B82F6;
        margin-bottom: 15px;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    /* Tabs Minimalistas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1C1C1E; }
    .stTabs [data-baseweb="tab"] { color: #636366; font-size: 0.8rem; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #3B82F6 !important; }

    /* Input */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121214 !important;
        border: 1px solid #2C2C2E !important;
        border-radius: 8px !important;
    }

    hr { border: 0; border-top: 1px solid #1C1C1E; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS ---
@st.cache_resource
def get_connection():
    return st.connection("supabase", type="sql")

conn = get_connection()

def run_query(query_str, params=None, commit=False):
    try:
        if commit:
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            st.cache_data.clear()
            return True
        else:
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except:
        return None

@st.cache_data(ttl=600)
def get_cached_balance(uid):
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    return res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0

@st.cache_data(ttl=600)
def get_cached_family_balances():
    query = """
        SELECT u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)

@st.cache_data(ttl=600)
def get_cached_history(uid):
    return run_query("SELECT timestamp as data, description as motivo, amount as valor FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 15", params={'uid': uid})

# --- 3. ESTADO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""

# --- 4. LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<div style='margin-top:4rem; text-align:center;'><h1 class='stealth-logo'>💎 RipariBank</h1><p style='color:#444;'>Security Protocol v8.0</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Usuário").lower().strip()
        p = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("AUTENTICAR", use_container_width=True):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.cache_data.clear()
                st.rerun()
            else: st.toast("Acesso Negado.")

# --- 5. DASHBOARD ---
else:
    # --- HEADER ---
    h_col1, h_col2, h_col3 = st.columns([2.5, 0.6, 0.6])
    with h_col1:
        st.markdown("<div class='stealth-logo'>💎 RipariBank</div>", unsafe_allow_html=True)
    with h_col2:
        if st.button("🔄", key="ref"):
            st.cache_data.clear()
            st.rerun()
    with h_col3:
        if st.button("🚪", key="out"):
            st.session_state.logged_in = False
            st.cache_data.clear()
            st.rerun()

    if st.session_state.role == 'admin':
        st.markdown("<div class='stealth-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-minor'>Monitoramento de Ativos</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"""
                <div class='admin-row'>
                    <span style='font-weight:600;'>{row['name'].title()}</span>
                    <span style='color:#3B82F6; font-family:monospace; font-weight:700;'>R$ {row['balance']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("💸 LANÇAMENTO TÁTICO"):
            users_df = run_query("SELECT id, name FROM users WHERE role='user'")
            if users_df is not None and not users_df.empty:
                with st.form("new_trans_p"):
                    target = st.selectbox("Conta Destino:", users_df['name'].tolist())
                    val = st.number_input("Montante (R$)", min_value=0.0, step=1.0)
                    tipo = st.radio("Operação", ["Depósito", "Retirada"], horizontal=True)
                    desc = st.text_input("Motivo")
                    if st.form_submit_button("EXECUTAR", use_container_width=True):
                        if val > 0 and desc:
                            u_target_id = users_df[users_df['name'] == target]['id'].values[0]
                            final_val = val if tipo == "Depósito" else -val
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': final_val, 'desc': desc, 'ts': datetime.now(), 't': tipo}, commit=True)
                            st.success("Transação Confirmada.")
                            time.sleep(1); st.rerun()

        with st.expander("⚙️ COMANDO DE USUÁRIOS"):
            tab_list, tab_add = st.tabs(["Listagem", "Novo Registro"])
            with tab_list:
                all_u = run_query("SELECT id, name, role FROM users ORDER BY name")
                st.dataframe(all_u, use_container_width=True, hide_index=True)
            with tab_add:
                with st.form("add_user_form"):
                    nn = st.text_input("Username").lower().strip()
                    np = st.text_input("Senha")
                    nr = st.selectbox("Nível", ["user", "admin"])
                    if st.form_submit_button("CADASTRAR"):
                        run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params={'n': nn, 'r': nr, 'p': np}, commit=True)
                        st.rerun()

    else:
        saldo = get_cached_balance(st.session_state.user_id)
        st.markdown(f"""
        <div class="stealth-card">
            <div class="label-minor">Saldo em Conta | {st.session_state.user_name.upper()}</div>
            <div class="val-major">R$ {saldo:,.2f}</div>
            <div style="margin-top:10px; font-size:0.6rem; color:#3B82F6;">● CONEXÃO CRIPTOGRAFADA</div>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["📊 Histórico", "📈 Evolução", "🧮 Calculadora"])
        
        with tabs[0]:
            df_hist = get_cached_history(st.session_state.user_id)
            if df_hist is not None and not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else: st.info("Sem registros no momento.")
        
        with tabs[1]:
            if df_hist is not None and not df_hist.empty:
                st.area_chart(df_hist.set_index('data')['valor'], color="#3B82F6")
        
        with tabs[2]:
            st.markdown(f"<div class='calc-box'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            
            def k_press(k): st.session_state.calc_expr += str(k)
            def k_clr(): st.session_state.calc_expr = ""
            def k_solve():
                try: st.session_state.calc_expr = str(eval(st.session_state.calc_expr.replace('×', '*').replace('÷', '/')))
                except: st.session_state.calc_expr = "Erro"

            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", key="n7", on_click=k_press, args=("7",))
            c2.button("8", key="n8", on_click=k_press, args=("8",))
            c3.button("9", key="n9", on_click=k_press, args=("9",))
            c4.button("_÷_", key="ndiv", on_click=k_press, args=("/",))

            c1.button("4", key="n4", on_click=k_press, args=("4",))
            c2.button("5", key="n5", on_click=k_press, args=("5",))
            c3.button("6", key="n6", on_click=k_press, args=("6",))
            c4.button("_×_", key="nmul", on_click=k_press, args=("*",))

            c1.button("1", key="n1", on_click=k_press, args=("1",))
            c2.button("2", key="n2", on_click=k_press, args=("2",))
            c3.button("3", key="n3", on_click=k_press, args=("3",))
            c4.button("_-_", key="nsub", on_click=k_press, args=("-",))

            c1.button(" + ", key="n0", on_click=k_press, args=("0",))
            c2.button(".", key="ndot", on_click=k_press, args=(".",))
            c3.button("C", key="nclr", on_click=k_clr)
            c4.button("_+_", key="nadd", on_click=k_press, args=("+",))

            st.button("CALCULAR", key="nsolve", type="primary", use_container_width=True, on_click=k_solve)

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#1A1A1C; font-size:0.6rem; margin-top:4rem;'>RIPARIBANK STEALTH CORE v8.0</div>", unsafe_allow_html=True)
