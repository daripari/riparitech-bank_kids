import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank", page_icon="💎", layout="centered")

# CSS NEO-BANK MINIMALIST
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

    /* Estilização Global dos Botões */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #222222 !important;
        font-size: 1rem !important; /* Aumentado de 0.8 para 1.0 */
        height: 42px !important;    /* Ajustado para acomodar melhor os símbolos */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: 0.2s;
        line-height: 1 !important;
    }
    
    .stButton>button:hover {
        border-color: #10B981 !important;
        color: #10B981 !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Estilo Específico da Calculadora */
    .calc-display {
        background-color: #000;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
        text-align: right;
        font-size: 1.5rem;
        font-family: 'Inter', sans-serif;
        color: #10B981;
        margin-bottom: 10px;
        min-height: 55px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    hr { border: 0; border-top: 1px solid #222; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS ---
try:
    conn = st.connection("supabase", type="sql")
except Exception:
    st.error("Conexão perdida com a nuvem.")
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
    if res is not None and not res.empty and res.iloc[0]['cnt'] == 0:
        for u in [{'n':'daniel','r':'admin','p':'1234'}, {'n':'ligia','r':'admin','p':'1234'}, 
                  {'n':'murilo','r':'user','p':'kids1'}, {'n':'cecilia','r':'user','p':'kids2'}]:
            run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params=u, commit=True)

init_db()

# --- 3. LOGICA DE ESTADO ---
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
                st.rerun()
            else: st.toast("Credenciais inválidas.")

# --- 5. DASHBOARD PRINCIPAL ---
else:
    # --- HEADER ---
    h_col1, h_col2, h_col3 = st.columns([2, 0.5, 0.5])
    with h_col1:
        st.markdown("<div class='header-logo'>💎 RipariBank</div>", unsafe_allow_html=True)
    with h_col2:
        if st.button("🔄", key="ref"): st.rerun()
    with h_col3:
        if st.button("🚪", key="out"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # --- VISUALIZAÇÃO DE SALDOS ---
    if st.session_state.role == 'admin':
        st.markdown("<div class='balance-label'>Saldos da Família</div>", unsafe_allow_html=True)
        saldos_query = """
            SELECT u.name, COALESCE(SUM(t.amount), 0) as balance 
            FROM users u 
            LEFT JOIN transactions t ON u.id = t.user_id 
            WHERE u.role = 'user' 
            GROUP BY u.name, u.id
            ORDER BY u.name
        """
        df_saldos = run_query(saldos_query)
        
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"""
                <div class='admin-user-card'>
                    <span style='font-weight:600;'>{row['name'].title()}</span>
                    <span style='color:#10B981; font-weight:700;'>R$ {row['balance']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum utilizador registado.")
    else:
        res_bal = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': st.session_state.user_id})
        saldo = res_bal.iloc[0]['total'] if res_bal is not None and not res_bal.empty and pd.notnull(res_bal.iloc[0]['total']) else 0.0
        
        st.markdown(f"""
        <div class="glass-card">
            <div class="balance-label">Meu Saldo</div>
            <div class="balance-value">R$ {saldo:,.2f}</div>
            <div style="color:#666; font-size:0.8rem;">Olá, {st.session_state.user_name.title()}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- SEÇÃO DE CONTEÚDO (TABS) ---
    if st.session_state.role == 'user':
        tab1, tab2, tab3 = st.tabs(["HISTÓRICO", "ANÁLISE", "CALCULADORA"])
        
        with tab1:
            df_hist = run_query("SELECT timestamp as data, description as motivo, amount as valor FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 10", params={'uid': st.session_state.user_id})
            if df_hist is not None and not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else:
                st.info("Ainda não tens movimentos.")
        
        with tab2:
            if df_hist is not None and not df_hist.empty:
                st.area_chart(df_hist.set_index('data')['valor'], height=200)
        
        with tab3:
            # Layout da Calculadora
            st.markdown(f"<div class='calc-display'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            
            def add_to_calc(val):
                st.session_state.calc_expr += str(val)

            def clear_calc():
                st.session_state.calc_expr = ""

            def solve_calc():
                try:
                    # Substitui X por * para avaliação
                    expr = st.session_state.calc_expr.replace('x', '*')
                    st.session_state.calc_expr = str(eval(expr))
                except:
                    st.session_state.calc_expr = "Erro"

            # Grid de botões
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("7", key="c7"): add_to_calc(7)
            if c2.button("8", key="c8"): add_to_calc(8)
            if c3.button("9", key="c9"): add_to_calc(9)
            if c4.button("/", key="cdiv"): add_to_calc("/")

            if c1.button("4", key="c4"): add_to_calc(4)
            if c2.button("5", key="c5"): add_to_calc(5)
            if c3.button("6", key="c6"): add_to_calc(6)
            if c4.button("x", key="cmul"): add_to_calc("x")

            if c1.button("1", key="c1"): add_to_calc(1)
            if c2.button("2", key="c2"): add_to_calc(2)
            if c3.button("3", key="c3"): add_to_calc(3)
            # Labels com espaços para garantir renderização correta
            if c4.button(" - ", key="csub"): add_to_calc("-")

            if c1.button("0", key="c0"): add_to_calc(0)
            if c2.button(".", key="cdot"): add_to_calc(".")
            if c3.button("C", key="cclr"): clear_calc()
            if c4.button(" + ", key="cadd"): add_to_calc("+")

            if st.button("=", key="csolve", type="primary", use_container_width=True): solve_calc()
    
    else:
        # Área do Administrador
        st.markdown("---")
        st.markdown("### Painel de Controlo")
        
        with st.expander("💸 NOVO LANÇAMENTO", expanded=True):
            users_df = run_query("SELECT id, name FROM users WHERE role='user'")
            if users_df is not None and not users_df.empty:
                with st.form("new_trans"):
                    target = st.selectbox("Para quem?", users_df['name'].tolist())
                    val = st.number_input("Quanto?", min_value=0.0, step=0.5)
                    tipo = st.radio("Tipo", ["Depósito", "Retirada"], horizontal=True)
                    desc = st.text_input("Qual o motivo?")
                    if st.form_submit_button("EFETUAR TRANSFERÊNCIA"):
                        if val > 0 and desc:
                            u_target_id = users_df[users_df['name'] == target]['id'].values[0]
                            final_val = val if tipo == "Depósito" else -val
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': final_val, 'desc': desc, 'ts': datetime.now(), 't': tipo}, commit=True)
                            st.success("Lançamento efetuado!")
                            time.sleep(1); st.rerun()

        with st.expander("👤 GERIR MEMBROS"):
            all_users = run_query("SELECT id, name, role FROM users ORDER BY name")
            st.dataframe(all_users, use_container_width=True, hide_index=True)
            
            with st.form("add_user"):
                new_n = st.text_input("Novo Nome").lower().strip()
                new_p = st.text_input("Senha Inicial")
                new_r = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("CRIAR CONTA"):
                    run_query("INSERT INTO users (name, role, password) VALUES (:n, :r, :p)", params={'n':new_n, 'r':new_r, 'p':new_p}, commit=True)
                    st.rerun()

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#333; font-size:0.7rem; margin-top:4rem;'>RipariBank v6.3 | Secured Minimalist Hub</div>", unsafe_allow_html=True)
