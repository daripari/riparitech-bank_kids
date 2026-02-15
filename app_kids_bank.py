import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank Premium", page_icon="💎", layout="centered")

# CSS PREMIUM NEO-BANK UI - VERSÃO CORRIGIDA (GRID E BOTÕES)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e Fundo */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #E0E0E0;
    }
    
    .stApp { background-color: #050505; }
    
    /* Ocultar elementos nativos */
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Header Estilizado */
    .header-logo {
        font-size: 1.3rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #FFFFFF 0%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Cards Premium (Glassmorphism) */
    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .admin-user-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .balance-label {
        color: #9CA3AF;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }
    
    .balance-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #10B981;
        margin: 0.4rem 0;
        letter-spacing: -1px;
    }

    /* --- CORREÇÃO DE BOTÕES ESTREITOS E SÍMBOLOS --- */
    .stButton>button {
        border-radius: 16px !important;
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #262626 !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        height: 55px !important;
        width: 100% !important;
        min-width: 60px !important; /* Garante que não fiquem estreitos */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: normal !important; /* Evita corte vertical de símbolos como + */
        padding: 5px !important; /* Espaço interno mínimo */
        margin: 0 !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton>button:hover {
        border-color: #10B981 !important;
        background-color: #161616 !important;
        color: #10B981 !important;
    }

    /* Botão Igual e Submit */
    div[data-testid="stFormSubmitButton"] button, 
    button[key="nsolve"] {
        background: #10B981 !important;
        color: #000000 !important;
        border: none !important;
    }

    /* Calculadora Visual */
    .calc-display {
        background-color: #000000;
        border: 2px solid #1A1A1A;
        border-radius: 16px;
        padding: 20px;
        text-align: right;
        font-size: 2.2rem;
        font-weight: 600;
        color: #10B981;
        margin-bottom: 15px;
        min-height: 85px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        box-shadow: inset 0 2px 20px rgba(0,0,0,0.9);
    }

    /* Estilização de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111111;
        border-radius: 10px 10px 0 0;
        padding: 8px 16px;
        color: #666;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(16, 185, 129, 0.1) !important;
        color: #10B981 !important;
        border-bottom: 2px solid #10B981 !important;
    }

    /* Inputs e Forms */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0A0A0A !important;
        border: 1px solid #222 !important;
        border-radius: 14px !important;
        color: white !important;
    }

    hr { border: 0; border-top: 1px solid #1A1A1A; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS COM CACHE ---
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

# --- 3. INICIALIZAÇÃO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""

# --- 4. INTERFACE DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<div style='margin-top:5rem; text-align:center;'><h1 style='font-size:3rem;'>💎</h1><h1 style='letter-spacing:-2px;'>RipariBank</h1><p style='color:#6B7280; font-weight:400;'>O seu futuro começa hoje.</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Nome de Usuário").lower().strip()
        p = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ACESSAR MINHA CONTA", use_container_width=True):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.cache_data.clear()
                st.rerun()
            else: st.toast("Usuário ou senha incorretos.")

# --- 5. DASHBOARD PRINCIPAL ---
else:
    # --- HEADER ---
    h_col1, h_col2, h_col3 = st.columns([2.5, 0.6, 0.6])
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
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # --- ÁREA ADMIN ---
    if st.session_state.role == 'admin':
        st.markdown("<div class='balance-label'>Saldos da Família</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"""
                <div class='admin-user-card'>
                    <div style='display:flex; align-items:center; gap:10px;'>
                        <span style='font-size:1.2rem;'>👤</span>
                        <span style='font-weight:600;'>{row['name'].title()}</span>
                    </div>
                    <span style='color:#10B981; font-weight:700; font-size:1.1rem;'>R$ {row['balance']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        with st.expander("💸 NOVO LANÇAMENTO RÁPIDO", expanded=True):
            users_df = run_query("SELECT id, name FROM users WHERE role='user'")
            if users_df is not None and not users_df.empty:
                with st.form("new_trans_p"):
                    target = st.selectbox("Para:", users_df['name'].tolist())
                    val = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
                    tipo = st.radio("Operação", ["Depósito", "Retirada"], horizontal=True)
                    desc = st.text_input("Referência / Motivo")
                    if st.form_submit_button("CONFIRMAR TRANSAÇÃO", use_container_width=True):
                        if val > 0 and desc:
                            u_target_id = users_df[users_df['name'] == target]['id'].values[0]
                            final_val = val if tipo == "Depósito" else -val
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': final_val, 'desc': desc, 'ts': datetime.now(), 't': tipo}, commit=True)
                            st.success("Transação concluída!")
                            time.sleep(1); st.rerun()

    # --- ÁREA USUÁRIO (KIDS) ---
    else:
        saldo = get_cached_balance(st.session_state.user_id)
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="balance-label">Saldo Atual</div>
                <div style="font-size:0.7rem; color:#4B5563; font-weight:700;">USER: {st.session_state.user_name.upper()}</div>
            </div>
            <div class="balance-value">R$ {saldo:,.2f}</div>
            <div style="display:flex; gap:10px; margin-top:10px;">
                <div style="background:rgba(16,185,129,0.1); padding:4px 10px; border-radius:8px; font-size:0.7rem; color:#10B981;">● CONTA ATIVA</div>
                <div style="background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:8px; font-size:0.7rem; color:#9CA3AF;">💎 RIPARI PREMIER</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["📊 Histórico", "📈 Evolução", "🧮 Calculadora"])
        
        with tabs[0]:
            df_hist = get_cached_history(st.session_state.user_id)
            if df_hist is not None and not df_hist.empty:
                def color_amount(val):
                    color = '#10B981' if val >= 0 else '#EF4444'
                    return f'color: {color}; font-weight: bold'
                st.dataframe(df_hist.style.map(color_amount, subset=['valor']), use_container_width=True, hide_index=True)
            else: st.info("Sem movimentos.")
        
        with tabs[1]:
            if df_hist is not None and not df_hist.empty:
                st.area_chart(df_hist.set_index('data')['valor'], color="#10B981", height=220)
        
        with tabs[2]:
            # CALCULADORA
            st.markdown(f"<div class='calc-display'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            
            def k_press(k): st.session_state.calc_expr += str(k)
            def k_clr(): st.session_state.calc_expr = ""
            def k_solve():
                try: 
                    # Avaliação segura básica
                    expr = st.session_state.calc_expr.replace('×', '*').replace('÷', '/')
                    st.session_state.calc_expr = str(eval(expr))
                except: st.session_state.calc_expr = "Erro"

            # Grid de botões com colunas Streamlit
            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", key="n7", on_click=k_press, args=("7",))
            c2.button("8", key="n8", on_click=k_press, args=("8",))
            c3.button("9", key="n9", on_click=k_press, args=("9",))
            c4.button("÷", key="ndiv", on_click=k_press, args=("/",))

            c1.button("4", key="n4", on_click=k_press, args=("4",))
            c2.button("5", key="n5", on_click=k_press, args=("5",))
            c3.button("6", key="n6", on_click=k_press, args=("6",))
            c4.button("×", key="nmul", on_click=k_press, args=("*",))

            c1.button("1", key="n1", on_click=k_press, args=("1",))
            c2.button("2", key="n2", on_click=k_press, args=("2",))
            c3.button("3", key="n3", on_click=k_press, args=("3",))
            # Símbolo "Menos" Matemático (U+2212)
            c4.button("−", key="nsub", on_click=k_press, args=("-",))

            c1.button("0", key="n0", on_click=k_press, args=("0",))
            c2.button(".", key="ndot", on_click=k_press, args=(".",))
            c3.button("C", key="nclr", on_click=k_clr)
            # Símbolo "Mais" Matemático Robusto
            c4.button("+", key="nadd", on_click=k_press, args=("+",))

            st.button("=", key="nsolve", type="primary", use_container_width=True, on_click=k_solve)

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#262626; font-size:0.65rem; margin-top:4rem;'>RipariBank v7.2 • 2024</div>", unsafe_allow_html=True)
