import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS NEO-BANK MINIMALIST ULTRA-FAST
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #FFFFFF;
    }
    
    .stApp { background-color: #050505; }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .header-logo {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .admin-user-card {
        background: rgba(255, 255, 255, 0.02);
        border-left: 3px solid #10B981;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .balance-label {
        color: #888888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .balance-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #10B981;
        margin: 0.5rem 0;
    }

    /* Botões - Ajuste de visibilidade total */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #222222 !important;
        font-size: 1.2rem !important; /* Aumentado para visibilidade */
        font-weight: 700 !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
    }
    
    .stButton>button:hover {
        border-color: #10B981 !important;
        color: #10B981 !important;
    }

    /* Estilo Específico da Calculadora */
    .calc-display {
        background-color: #000;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 15px;
        text-align: right;
        font-size: 2rem;
        font-family: 'Inter', sans-serif;
        color: #10B981;
        margin-bottom: 15px;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);
    }

    hr { border: 0; border-top: 1px solid #222; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS COM CACHE (PERFORMANCE) ---
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
            st.cache_data.clear() # Limpa o cache após gravação
            return True
        else:
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except:
        return None

# Funções de Dados com Cache para evitar delay na Calculadora
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
    return run_query("SELECT timestamp as data, description as motivo, amount as valor FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 10", params={'uid': uid})

# --- 3. INICIALIZAÇÃO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""

# --- 4. INTERFACE DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<div style='margin-top:4rem; text-align:center;'><h1 style='font-size:2.5rem;'>💎</h1><h1>RipariBank</h1><p style='color:#666;'>Controle Financeiro Familiar</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Utilizador").lower().strip()
        p = st.text_input("Palavra-passe", type="password").strip()
        if st.form_submit_button("ENTRAR"):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.cache_data.clear()
                st.rerun()
            else: st.toast("Credenciais inválidas.")

# --- 5. DASHBOARD PRINCIPAL ---
else:
    # --- HEADER ---
    h_col1, h_col2, h_col3 = st.columns([2, 0.5, 0.5])
    with h_col1:
        st.markdown("<div class='header-logo'>💎 RipariBank</div>", unsafe_allow_html=True)
    with h_col2:
        if st.button("🔄", key="ref"):
            st.cache_data.clear()
            st.rerun()
    with h_col3:
        if st.button("🚪", key="out"):
            st.session_state.logged_in = False
            st.cache_data.clear()
            st.rerun()
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # --- VISUALIZAÇÃO DE SALDOS (USANDO CACHE) ---
    if st.session_state.role == 'admin':
        st.markdown("<div class='balance-label'>Saldos da Família</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"<div class='admin-user-card'><b>{row['name'].title()}</b><span style='color:#10B981;'>R$ {row['balance']:,.2f}</span></div>", unsafe_allow_html=True)
    else:
        saldo = get_cached_balance(st.session_state.user_id)
        st.markdown(f"""
        <div class="glass-card">
            <div class="balance-label">Meu Saldo</div>
            <div class="balance-value">R$ {saldo:,.2f}</div>
            <div style="color:#666; font-size:0.8rem;">Olá, {st.session_state.user_name.title()}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- TABS (INTERAÇÃO LOCAL) ---
    if st.session_state.role == 'user':
        tab1, tab2, tab3 = st.tabs(["HISTÓRICO", "ANÁLISE", "CALCULADORA"])
        
        with tab1:
            df_hist = get_cached_history(st.session_state.user_id)
            if df_hist is not None and not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else: st.info("Sem movimentos.")
        
        with tab2:
            if df_hist is not None and not df_hist.empty:
                st.area_chart(df_hist.set_index('data')['valor'], height=200)
        
        with tab3:
            # CALCULADORA PURE FRONT (SEM ACESSO AO DB NO RERUN)
            st.markdown(f"<div class='calc-display'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            
            def press_key(key): st.session_state.calc_expr += str(key)
            def clear_calc(): st.session_state.calc_expr = ""
            def solve_calc():
                try:
                    expr = st.session_state.calc_expr.replace('×', '*').replace('÷', '/')
                    st.session_state.calc_expr = str(eval(expr))
                except: st.session_state.calc_expr = "Erro"

            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", key="k7", on_click=press_key, args=("7",))
            c2.button("8", key="k8", on_click=press_key, args=("8",))
            c3.button("9", key="k9", on_click=press_key, args=("9",))
            c4.button("÷", key="kdiv", on_click=press_key, args=("/",))

            c1.button("4", key="k4", on_click=press_key, args=("4",))
            c2.button("5", key="k5", on_click=press_key, args=("5",))
            c3.button("6", key="k6", on_click=press_key, args=("6",))
            c4.button("×", key="kmul", on_click=press_key, args=("*",))

            c1.button("1", key="k1", on_click=press_key, args=("1",))
            c2.button("2", key="k2", on_click=press_key, args=("2",))
            c3.button("3", key="k3", on_click=press_key, args=("3",))
            c4.button("-", key="ksub", on_click=press_key, args=("-",)) # Símbolo simples para garantir visibilidade

            c1.button("0", key="k0", on_click=press_key, args=("0",))
            c2.button(".", key="kdot", on_click=press_key, args=(".",))
            c3.button("C", key="kclr", on_click=clear_calc)
            c4.button("+", key="kadd", on_click=press_key, args=("+",)) # Símbolo simples

            st.button("=", key="ksolve", type="primary", use_container_width=True, on_click=solve_calc)
    
    else:
        # ÁREA ADMIN
        st.markdown("---")
        with st.expander("💸 NOVO LANÇAMENTO", expanded=True):
            users_df = run_query("SELECT id, name FROM users WHERE role='user'")
            if users_df is not None and not users_df.empty:
                with st.form("new_trans"):
                    target = st.selectbox("Para quem?", users_df['name'].tolist())
                    val = st.number_input("Quanto?", min_value=0.0, step=0.5)
                    tipo = st.radio("Tipo", ["Depósito", "Retirada"], horizontal=True)
                    desc = st.text_input("Qual o motivo?")
                    if st.form_submit_button("LANÇAR"):
                        if val > 0 and desc:
                            u_target_id = users_df[users_df['name'] == target]['id'].values[0]
                            final_val = val if tipo == "Depósito" else -val
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': final_val, 'desc': desc, 'ts': datetime.now(), 't': tipo}, commit=True)
                            st.success("Sucesso!")
                            time.sleep(1); st.rerun()

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#333; font-size:0.7rem; margin-top:4rem;'>RipariBank v6.5 | Otimizado para Velocidade</div>", unsafe_allow_html=True)
